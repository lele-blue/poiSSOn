from main.models import CoreSetting, User


CORE_SETTINGS = {
    "poisson.core.webauthn.authenticator_attachment": {
        "default": "poisson.core.webauthn.authenticator_attachment.cross_platform",
        "type": "choice",
        "values": [
            "poisson.core.webauthn.authenticator_attachment.platform",
            "poisson.core.webauthn.authenticator_attachment.cross_platform",
            "poisson.core.webauthn.authenticator_attachment.none",
        ]
    },
    "poisson.core.webauthn.hint": {
        "default": "poisson.core.webauthn.hint.security_key",
        "type": "choice",
        "values": [
            "poisson.core.webauthn.hint.none",
            "poisson.core.webauthn.hint.security_key",
            "poisson.core.webauthn.hint.client_device",
            "poisson.core.webauthn.hint.hybrid",
        ]
    },
    "poisson.core.webauthn.user_verification_requirement": {
        "default": "poisson.core.webauthn.user_verification_requirement.prefer",
        "type": "choice",
        "values": [
            "poisson.core.webauthn.user_verification_requirement.prefer",
            "poisson.core.webauthn.user_verification_requirement.require",
            "poisson.core.webauthn.user_verification_requirement.discourage",
        ]
    },
    "poisson.core.webauthn.resident_key_requirement": {
        "default": "poisson.core.webauthn.resident_key_requirement.prefer",
        "type": "choice",
        "values": [
            "poisson.core.webauthn.resident_key_requirement.prefer",
            "poisson.core.webauthn.resident_key_requirement.require",
            "poisson.core.webauthn.resident_key_requirement.discourage",
        ]
    }
}


def get_core_setting(key, user: User):
    return CoreSetting.objects.get(key=key).value
