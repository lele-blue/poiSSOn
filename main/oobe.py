from main.core_settings import get_core_setting


def init():
    match get_core_setting("poisson.core.oobe.state", None):
        case "poisson.oobe.first_start":
            return True
        case _:
            return False
