from datetime import datetime, timedelta
import json
import logging
import os
from django.contrib.sessions.models import Session
from django.db import models
from django.utils import timezone
from django_otp.models import Device
from django_ratelimit.core import ALL, is_ratelimited
import webauthn
from django.conf import settings
from uuid import uuid4

from webauthn.helpers.base64url_to_bytes import base64url_to_bytes
from webauthn.helpers.bytes_to_base64url import bytes_to_base64url
from webauthn.helpers.generate_challenge import generate_challenge
from webauthn.helpers.options_to_json import options_to_json
from webauthn.helpers.exceptions import InvalidAuthenticationResponse, InvalidRegistrationResponse
from webauthn.helpers.structs import AttestationConveyancePreference, AuthenticatorAttachment, AuthenticatorSelectionCriteria, PublicKeyCredentialDescriptor, PublicKeyCredentialHint, ResidentKeyRequirement, UserVerificationRequirement, CredentialDeviceType, PublicKeyCredentialType

from main.core_settings import get_core_setting
from main.models import User

# Create your models here.

RESIDENT_KEY_SETTINGS_MAP = {
    "poisson.core.webauthn.resident_key_requirement.prefer": ResidentKeyRequirement.PREFERRED,
    "poisson.core.webauthn.resident_key_requirement.discourage": ResidentKeyRequirement.DISCOURAGED,
    "poisson.core.webauthn.resident_key_requirement.require": ResidentKeyRequirement.REQUIRED,
}

AUTHENTICATOR_ATTACHMENT_SETTINGS_MAP = {
    "poisson.core.webauthn.authenticator_attachment.platform": AuthenticatorAttachment.PLATFORM,
    "poisson.core.webauthn.authenticator_attachment.cross_platform": AuthenticatorAttachment.CROSS_PLATFORM,
    "poisson.core.webauthn.authenticator_attachment.none": None,
}

USER_VERIFICATION_SETTINGS_MAP = {
    "poisson.core.webauthn.user_verification_requirement.prefer": UserVerificationRequirement.PREFERRED,
    "poisson.core.webauthn.user_verification_requirement.discourage": UserVerificationRequirement.DISCOURAGED,
    "poisson.core.webauthn.user_verification_requirement.require": UserVerificationRequirement.REQUIRED,
}

AUTH_HINT_SETTINGS_MAP = {
    "poisson.core.webauthn.hint.none": [],
    "poisson.core.webauthn.hint.client_device": [PublicKeyCredentialHint.CLIENT_DEVICE],
    "poisson.core.webauthn.hint.hybrid": [PublicKeyCredentialHint.HYBRID],
    "poisson.core.webauthn.hint.security_key": [PublicKeyCredentialHint.SECURITY_KEY],
}

logger = logging.getLogger(__name__)

class WebauthnDevice(Device):
    id = models.UUIDField(default=uuid4, primary_key=True)
    use_count = models.PositiveIntegerField(default=0)
    credentials = models.TextField()
    cred_id = models.TextField()
    publicKey = models.BinaryField()
    backed_up = models.BooleanField()
    device_type = models.CharField(max_length=32, choices=(("single_device", "single_device"), ("multi_device", "multi_device")))
    created = models.DateTimeField(editable=False)
    last_used = models.DateTimeField()
    last_seen_sign_count = models.PositiveIntegerField()
    icon = models.TextField(default="")
    current_challenge = models.BinaryField(null=True, blank=True)
    current_challenge_expire = models.DateTimeField(null=True, blank=True)

    def verify_is_allowed(self):
        if is_ratelimited(None, "Webauthn.Device", None, lambda *_:f"webauthn.{self.pk}", "3/5m", ALL, False):
            return False, {"message": "Ratelimited"}
        return True, None

    def verify_token(self, token):
        if not self.verify_is_allowed()[0]:
            logger.warning(f"User {self.user.username} ({self.user.uid}) tried to use a locked Webauthn Device")
            return False
        if self.current_challenge_expire < timezone.now():
            logger.warning(f"User {self.user.username} ({self.user.uid}) tried to use an expired Webauthn Challenge")
            return False

        try:
            verification_data = webauthn.verify_authentication_response(
                credential=token,
                credential_public_key=self.publicKey,
                expected_challenge=self.current_challenge,
                expected_origin=settings.SITE_URL,
                expected_rp_id=settings.OTP_WEBAUTHN_RP_ID,
                require_user_verification=USER_VERIFICATION_SETTINGS_MAP[get_core_setting("poisson.core.webauthn.user_verification_requirement", self.user)] == UserVerificationRequirement.REQUIRED,
                credential_current_sign_count=self.last_seen_sign_count,
            )
        except InvalidAuthenticationResponse as e:
            is_ratelimited(None, "Webauthn.Device", None, lambda *_: f"webauthn.{self.pk}", "3/5m", ALL, True)
            logger.warning(f"User {self.user.username} ({self.user.uid}) webauthn failed: {e.args[0]}")
            return False

        self.last_seen_sign_count = verification_data.new_sign_count
        self.current_challenge = b''
        self.current_challenge_expire = datetime.now()
        self.save()

        return True

    def generate_challenge(self):
        self.current_challenge = generate_challenge()
        self.current_challenge_expire = datetime.now() + timedelta(minutes=3)
        self.save()

        authentication_options = webauthn.generate_authentication_options(
            rp_id=settings.OTP_WEBAUTHN_RP_ID,
            challenge=self.current_challenge,
            timeout=12000,
            user_verification=USER_VERIFICATION_SETTINGS_MAP[get_core_setting("poisson.core.webauthn.user_verification_requirement", self.user)],
            allow_credentials=[PublicKeyCredentialDescriptor(id=base64url_to_bytes(self.cred_id))]
        )

        return options_to_json(authentication_options)

    @staticmethod
    def generate_registration(user: User, session: Session):
        challenge = generate_challenge()
        session["webauthn_challenge"] = bytes_to_base64url(challenge)
        session["webauthn_challenge_expire"] = (datetime.now() + timedelta(minutes=3)).isoformat()
        session.save()
        registration_options = webauthn.generate_registration_options(
            rp_id=settings.OTP_WEBAUTHN_RP_ID,
            rp_name=settings.OTP_WEBAUTHN_RP_NAME,
            user_id=user.uid.encode("UTF8"),
            user_name=user.username,
            user_display_name=user.get_full_name(),
            attestation=AttestationConveyancePreference.NONE,
            authenticator_selection=AuthenticatorSelectionCriteria(
                user_verification=USER_VERIFICATION_SETTINGS_MAP[get_core_setting("poisson.core.webauthn.user_verification_requirement", user)],
                authenticator_attachment=AUTHENTICATOR_ATTACHMENT_SETTINGS_MAP[get_core_setting("poisson.core.webauthn.authenticator_attachment", user)],
                resident_key=RESIDENT_KEY_SETTINGS_MAP[get_core_setting("poisson.core.webauthn.resident_key_requirement", user)]
            ),
            challenge=challenge,
            timeout=12000,
            hints=AUTH_HINT_SETTINGS_MAP[get_core_setting("poisson.core.webauthn.hint", user)],
            exclude_credentials=list(map(lambda device: PublicKeyCredentialDescriptor(base64url_to_bytes(device.cred_id)), WebauthnDevice.objects.filter(user=user)))
        )

        return options_to_json(registration_options)

    @classmethod
    def create_device(cls, credential: dict, user: User, session: Session):
        expect_challenge = session.get("webauthn_challenge")
        if not expect_challenge or datetime.fromisoformat(session.get("webauthn_challenge_expire")) < datetime.now():
            return {"action": "fail", "reason": "Challenge Expired or wrong"}

        session["webauthn_challenge"] = None
        session.save()

        try:
            data = webauthn.verify_registration_response(
                credential=credential,
                expected_challenge=base64url_to_bytes(expect_challenge),
                expected_rp_id=settings.OTP_WEBAUTHN_RP_ID,
                expected_origin=settings.SITE_URL,
                require_user_verification=get_core_setting("poisson.core.webauthn.user_verification_requirement", user) == "poisson.core.webauthn.user_verification_requirement.require",
                require_user_presence=True,
            )
            device = cls()
            device.cred_id = bytes_to_base64url(data.credential_id)
            device.name = "WebAuthn / Passkey"


            match data.credential_device_type:
                case CredentialDeviceType.SINGLE_DEVICE:
                    device.device_type = "single_device"
                case CredentialDeviceType.MULTI_DEVICE:
                    device.device_type = "multi_device"

            device.backed_up = data.credential_backed_up
            device.last_seen_sign_count = data.sign_count
            device.last_used = datetime.now()
            device.created = datetime.now()
            device.user = user
            device.publicKey = data.credential_public_key

            # registering a device wont be called often, so we only load the mapping on demand
            with open(os.path.join(os.path.dirname(__file__), "data", "aaguids.json")) as source:
                authenticator_info = json.load(source).get(data.aaguid)
                if authenticator_info:
                    device.name = authenticator_info.get("name", "")
                    device.icon = authenticator_info.get("icon_dark", "")

            device.name += "(" + device.cred_id[:12] + ")"

            device.save()
            return device

        except InvalidRegistrationResponse as e:
            return {"action": "fail", "reason": str(e.args[0])}























