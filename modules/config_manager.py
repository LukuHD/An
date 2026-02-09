<<<<<<< Updated upstream
import json
import os

# Usar ruta absoluta relativa al directorio del proyecto
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEME_FILE = os.path.join(_BASE_DIR, "theme.json")

# Colores por defecto (Aura Blue)
DEFAULT_THEME = {
    "accent": "#00a8e8",       # El color principal (botones, bordes)
    "background": "#121212",   # El fondo oscuro
    "text": "#e0e0e0",         # El texto
    "secondary": "#1e1e24",    # Fondo de los botones/tarjetas
    "border": "#333333",       # Color de bordes generales
    "title_bar": "#0a0a0f",    # Color de la barra de título
    "card_text": "#ffffff",    # Color del texto en tarjetas
    "highlight": "#00ff7f",    # Color de resaltado/éxito
    "use_background": False,   # Si se usa imagen de fondo
    "background_image": ""     # Ruta a imagen de fondo (vacío = sin imagen)
=======
import os
import json

# Base directory of the project (one level above modules)
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEME_FILE = os.path.join(_BASE_DIR, "theme.json")

DEFAULT_THEME = {
    "background": "#121212",
    "text": "#e0e0e0",
    "secondary": "#1e1e24",
    "accent": "#00a8e8",
    "border": "#444444",
    "highlight": "#00ff7f",
    "use_background": False,
    "background_image": ""
>>>>>>> Stashed changes
}

class ConfigManager:
    @staticmethod
    def load_theme():
<<<<<<< Updated upstream
        if not os.path.exists(THEME_FILE):
            return dict(DEFAULT_THEME)
        try:
            with open(THEME_FILE, 'r') as f:
                data = json.load(f)
                # Asegurar que existan todas las claves (merge)
                return {**DEFAULT_THEME, **data} 
        except Exception:
            return dict(DEFAULT_THEME)

    @staticmethod
    def save_theme(new_theme):
        with open(THEME_FILE, 'w') as f:
            json.dump(new_theme, f, indent=4)
=======
        """Load theme from theme.json, merge with defaults, and normalize paths."""
        if not os.path.exists(THEME_FILE):
            return DEFAULT_THEME.copy()
        try:
            with open(THEME_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Merge user theme with defaults
            theme = {**DEFAULT_THEME, **(data or {})}
            bg_img = theme.get('background_image')
            if bg_img:
                # If path is relative, make it relative to base dir
                if not os.path.isabs(bg_img):
                    theme['background_image'] = os.path.join(_BASE_DIR, bg_img)
            return theme
        except Exception:
            # Fallback to defaults on any error
            return DEFAULT_THEME.copy()

    @staticmethod
    def save_theme(theme):
        """Persist theme to theme.json. Returns True on success."""
        try:
            to_save = {**DEFAULT_THEME, **(theme or {})}
            with open(THEME_FILE, 'w', encoding='utf-8') as f:
                json.dump(to_save, f, indent=4)
            return True
        except Exception:
            return False
>>>>>>> Stashed changes
