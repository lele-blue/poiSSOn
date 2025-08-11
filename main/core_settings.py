import random
import string
from main.models import CoreSetting, User

def invalidate_theme_cache():
    from main.theming import invalidate_theme_cache
    invalidate_theme_cache()

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
    },
    "poisson.core.theme": {
        "default": "poisson.theme.default",
        "type": "choice",
        "post_update_hook": invalidate_theme_cache,
        "values": [
            "poisson.theme.default",
            "poisson.theme.crimson",
            "poisson.theme.damp",
            "poisson.theme.dream",
            "poisson.theme.ember",
            "poisson.theme.plain",
        ]
    },
    "poisson.core.oobe.state": {
        "default": "poisson.oobe.first_start",
        "type": "choice",
        "values": [
            # first_start is not an option so it cant be reverted to create a new admin
            "poisson.oobe.finished",
        ]
    },
    "poisson.core.instance_name": {
        "default": "Unnamed",
        "type": "string",
        "post_update_hook": invalidate_theme_cache,
        "max_length": 32
    }
}


def get_core_setting(key, user: User):
    return CoreSetting.objects.get(key=key).value
