from main.models import CoreSetting, User


CORE_SETTINGS = {
    "poisson.core.webauthn.authenticator_attachment": {
        "default": "poisson.core.webauthn.authenticator_attachment.platform",
        "type": "choice",
        "values": [
            "poisson.core.webauthn.authenticator_attachment.platform",
            "poisson.core.webauthn.authenticator_attachment.cross_platform",
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
