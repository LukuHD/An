import json
import os

THEME_FILE = "theme.json"

# Colores por defecto (Aura Blue)
DEFAULT_THEME = {
    "accent": "#00a8e8",       # El color principal (botones, bordes)
    "background": "#121212",   # El fondo oscuro
    "text": "#e0e0e0",         # El texto
    "secondary": "#1e1e24"     # Fondo de los botones/tarjetas
}

class ConfigManager:
    @staticmethod
    def load_theme():
        if not os.path.exists(THEME_FILE):
            return DEFAULT_THEME
        try:
            with open(THEME_FILE, 'r') as f:
                data = json.load(f)
                # Asegurar que existan todas las claves (merge)
                return {**DEFAULT_THEME, **data} 
        except:
            return DEFAULT_THEME

    @staticmethod
    def save_theme(new_theme):
        with open(THEME_FILE, 'w') as f:
            json.dump(new_theme, f, indent=4)