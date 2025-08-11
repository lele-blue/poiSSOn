from main.core_settings import get_core_setting


class PoissonThemeBase:
    background_url: str
    accent_color: str
    error_color: str
    color: str
    icon_color: str
    ambient_color: str
    secondary_color: str
    text_color: str
    background_important: str
    accent_color_light_transparent: str
    accent_color_text: str
    accent_color_light: str
    background_color: str

    def assemble(self):
        return f"""
    --material-accent-color: {self.accent_color};
    --icon-secondary-col: {self.secondary_color};
    --material-background-important: {self.background_important};
    --material-error-color: {self.error_color};
    color: {self.color};
    --icon-col: {self.icon_color};
    --material-ambient-color: {self.ambient_color};
    --material-accent-color-light-transparent: {self.accent_color_light_transparent};
    --material-accent-color-text: {self.accent_color_text};
    --material-accent-color-light: {self.accent_color_light};
    --material-text: {self.text_color};
    --material-background-color: {self.background_color};
"""


class PoissonThemeDefault(PoissonThemeBase):
    background_url = "login_bg.jpg"
    accent_color = "#b045f2"
    error_color = "red"
    color = "darkslategrey"
    icon_color = "darkslategrey"
    ambient_color = "darkslategrey"
    secondary_color = "#b045f2"
    text_color = "darkslategrey"
    background_important = "rgba(255, 255, 255, 0.5)"
    accent_color_light_transparent = "#f6befe"
    accent_color_text = "white"
    accent_color_light = "#ad00f4"
    background_color = "white"

class PoissonThemeCrimson(PoissonThemeBase):
    background_url = "crimson.png"
    accent_color = "#ee0202"
    error_color = "red"
    color = "black"
    icon_color = "black"
    ambient_color = "black"
    secondary_color = "#ee0202"
    text_color = "black"
    background_important = "rgba(255, 255, 255, 0.5)"
    accent_color_light_transparent = "#ffe7e6"
    accent_color_text = "white"
    accent_color_light = "#ee0202"
    background_color = "white"

class PoissonThemeDamp(PoissonThemeBase):
    background_url = "damp.jpg"
    accent_color = "#003f0f"
    error_color = "red"
    color = "#202020"
    icon_color = "#202020"
    ambient_color = "#202020"
    secondary_color = "#003f0f"
    text_color = "#202020"
    background_important = "rgba(255, 255, 255, 0.5)"
    accent_color_light_transparent = "#d9d9d9"
    accent_color_text = "white"
    accent_color_light = "#003f0f"
    background_color = "white"

class PoissonThemeEmber(PoissonThemeBase):
    background_url = "ember.jpg"
    accent_color = "#d5383f"
    error_color = "red"
    color = "black"
    icon_color = "black"
    ambient_color = "black"
    secondary_color = "black"
    text_color = "black"
    background_important = "rgba(255, 255, 255, 0.5)"
    accent_color_light_transparent = "#d9d9d9"
    accent_color_text = "white"
    accent_color_light = "#c5282f"
    background_color = "white"

class PoissonThemeDream(PoissonThemeBase):
    background_url = "dream.jpg"
    accent_color = "#b85e5c"
    error_color = "red"
    color = "black"
    icon_color = "#322a81"
    ambient_color = "black"
    secondary_color = "#322a81"
    text_color = "black"
    background_important = "rgba(255, 255, 255, 0.5)"
    accent_color_light_transparent = "#d9d9d9"
    accent_color_text = "white"
    accent_color_light = "#b85e5c"
    background_color = "white"

class PoissonThemePlain(PoissonThemeBase):
    background_url = "plain.jpg"
    accent_color = "#262626"
    error_color = "red"
    color = "black"
    icon_color = "black"
    ambient_color = "black"
    secondary_color = "black"
    text_color = "black"
    background_important = "rgba(255, 255, 255, 0.5)"
    accent_color_light_transparent = "#d9d9d9"
    accent_color_text = "white"
    accent_color_light = "#262626"
    background_color = "white"

poisson_theme_background_url = None
poisson_theme_root_css = None
poisson_instance_name = None

def get_current_root_css():
    global poisson_theme_root_css
    if poisson_theme_root_css: return poisson_theme_root_css

    theme = get_current_theme()

    poisson_theme_root_css = theme.assemble()

    return poisson_theme_root_css

def get_current_background_url():
    global poisson_theme_background_url
    if poisson_theme_background_url: return poisson_theme_background_url

    theme = get_current_theme()

    poisson_theme_background_url = "/auth/go/static/resolve/" + theme.background_url

    return poisson_theme_background_url

def get_current_theme() -> PoissonThemeBase:
    theme = None

    match get_core_setting("poisson.core.theme", None):
        case "poisson.theme.crimson":
            theme = PoissonThemeCrimson()
        case "poisson.theme.damp":
            theme = PoissonThemeDamp()
        case "poisson.theme.dream":
            theme = PoissonThemeDream()
        case "poisson.theme.plain":
            theme = PoissonThemePlain()
        case "poisson.theme.ember":
            theme = PoissonThemeEmber()
        case _:
            theme = PoissonThemeDefault()
    return theme

def invalidate_theme_cache():
    global poisson_theme_background_url, poisson_theme_root_css, poisson_instance_name
    poisson_theme_background_url = None
    poisson_theme_root_css = None
    poisson_instance_name = None

def get_instance_name():
    global poisson_instance_name
    if poisson_instance_name is not None: return poisson_instance_name

    poisson_instance_name = get_core_setting("poisson.core.instance_name", None)

    return poisson_instance_name
