from datetime import datetime, timedelta
from django.db import models
from django_otp.models import Device
from django_ratelimit.core import is_ratelimited
import webauthn
from django.conf import settings
from uuid import uuid4

from webauthn.helpers.structs import AttestationConveyancePreference, AuthenticatorAttachment, AuthenticatorSelectionCriteria, ResidentKeyRequirement

from main.core_settings import get_core_setting
from main.models import User

# Create your models here.

RESIDENT_KEY_SETTINGS_MAP = {
    "poisson.core.webauthn.resident_key_requirement.prefer": ResidentKeyRequirement.PREFERRED,
    "poisson.core.webauthn.resident_key_requirement.discourage": ResidentKeyRequirement.DISCOURAGED,
    "poisson.core.webauthn.resident_key_requirement.require": ResidentKeyRequirement.REQUIRED,
}

class WebauthnDevice(Device):
    pk = models.UUIDField(default=uuid4, primary_key=True)
    use_count = models.PositiveIntegerField(default=0)
    credentials = models.TextField()
    pubkey = models.TextField()

    def verify_is_allowed(self):
        if is_ratelimited(None, "Webauthn.Device", None, f"webauthn.{self.pk}", "3/5m", None, False):
            return False, {"message": "Ratelimited"}
        return True, None

    def verify_token(self, token):
        webauthn.verify_authentication_response(token=token, expected_origin=settings.SITE_URL, require_user_verification=True, credential_current_sign_count=self.use_count)
        return False

    def generate_challenge(self, user: User):
        complex_registration_options = webauthn.generate_registration_options(
            rp_id=settings.OTP_WEBAUTHN_RP_ID,
            rp_name=settings.OTP_WEBAUTHN_RP_NAME,
            user_id=user.uid.encode("UTF8"),
            user_name=user.username,
            user_display_name=user.get_full_name(),
            attestation=AttestationConveyancePreference.INDIRECT, # Todo evaluate if this is needed / add config (do we need to save this in the device?)
            authenticator_selection=AuthenticatorSelectionCriteria(
                authenticator_attachment=AuthenticatorAttachment.PLATFORM,
                resident_key=RESIDENT_KEY_SETTINGS_MAP[get_core_setting("poisson.core.webauthn.resident_key_requirement", user)]
            ),
            challenge=bytes([1, 2, 3, 4, 5, 6, 7, 8, 9, 0]),
            exclude_credentials=[
                PublicKeyCredentialDescriptor(id=b"1234567890"),
            ],
            supported_pub_key_algs=[COSEAlgorithmIdentifier.ECDSA_SHA_512],
            timeout=12000,
            hints=[PublicKeyCredentialHint.CLIENT_DEVICE],
        )

