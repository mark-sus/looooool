from kivy.core.window import Window
from kivy.utils import get_color_from_hex

# Кольори для додатку
class Colors:
    PRIMARY = get_color_from_hex("#6200ee")
    SECONDARY = get_color_from_hex("#03dac6")
    BACKGROUND = get_color_from_hex("#f5f5f5")
    SURFACE = get_color_from_hex("#ffffff")
    TEXT_PRIMARY = get_color_from_hex("#333333")
    TEXT_SECONDARY = get_color_from_hex("#666666")
    ERROR = get_color_from_hex("#b00020")
    SUCCESS = get_color_from_hex("#00c853")

# Налаштування вікна
Window.clearcolor = Colors.BACKGROUND