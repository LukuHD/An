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
}

class ConfigManager:
    @staticmethod
    def load_theme():
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