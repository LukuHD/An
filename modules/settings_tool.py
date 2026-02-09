from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QColorDialog, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from modules.ui_components import DraggableTitleBar, PulseButton, animate_window_open
from modules.config_manager import ConfigManager

class ColorPickerBtn(QPushButton):
    """Botón cuadrado que muestra el color seleccionado."""
    def __init__(self, initial_color, label_text):
        super().__init__()
        self.current_color = initial_color
        self.setFixedSize(100, 100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_style()
        self.setText(label_text)

    def update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_color};
                border: 2px solid #555;
                border-radius: 15px;
                color: white; font-weight: bold; font-size: 12px;
            }}
            QPushButton:hover {{ border: 2px solid white; }}
        """)

class SettingsApp(QMainWindow):
    return_to_main = pyqtSignal(bool) # Bool: True si hubo cambios (para reiniciar)

    def __init__(self):
        super().__init__()
        self.resize(500, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Cargar tema actual
        self.theme = ConfigManager.load_theme()
        
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QVBoxLayout(self.central)
        self.layout.setContentsMargins(0,0,0,0)
        
        # Estilos base
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {self.theme['background']}; border: 1px solid {self.theme['accent']}; }}
            QLabel {{ color: {self.theme['text']}; font-family: 'Segoe UI'; }}
        """)

        # Barra Título
        self.title_bar = DraggableTitleBar(self, "AURA :: CONFIGURACIÓN")
        self.layout.addWidget(self.title_bar)
        
        # Contenido
        content = QWidget()
        self.c_layout = QVBoxLayout(content)
        self.c_layout.setContentsMargins(40,20,40,40)
        
        lbl = QLabel("PERSONALIZACIÓN VISUAL")
        lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.c_layout.addWidget(lbl)
        
        lbl_sub = QLabel("Haz clic en los cuadros para cambiar los colores.")
        lbl_sub.setStyleSheet("color: #888; font-size: 12px;")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.c_layout.addWidget(lbl_sub)
        
        # --- PICKERS ---
        grid = QHBoxLayout()
        grid.setSpacing(20)
        
        self.btn_accent = ColorPickerBtn(self.theme['accent'], "Color Principal\n(Botones/Bordes)")
        self.btn_accent.clicked.connect(lambda: self.pick_color("accent", self.btn_accent))
        
        self.btn_bg = ColorPickerBtn(self.theme['background'], "Color Fondo\n(Oscuro)")
        self.btn_bg.clicked.connect(lambda: self.pick_color("background", self.btn_bg))
        
        grid.addWidget(self.btn_accent)
        grid.addWidget(self.btn_bg)
        self.c_layout.addLayout(grid)
        self.c_layout.addStretch()
        
        # Botones de Acción
        self.btn_save = PulseButton("GUARDAR CAMBIOS")
        self.btn_save.clicked.connect(self.save_changes)
        
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setFlat(True)
        self.btn_cancel.setStyleSheet("color: #666; text-decoration: underline;")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.close_no_save)

        self.c_layout.addWidget(self.btn_save)
        self.c_layout.addWidget(self.btn_cancel)
        
        self.layout.addWidget(content)

    def pick_color(self, key, btn_widget):
        color = QColorDialog.getColor(QColor(self.theme[key]), self, "Elige un color")
        if color.isValid():
            hex_color = color.name()
            self.theme[key] = hex_color
            btn_widget.current_color = hex_color
            btn_widget.update_style()

    def save_changes(self):
        ConfigManager.save_theme(self.theme)
        # Mostrar mensaje amigable
        msg = QMessageBox(self)
        msg.setWindowTitle("¡Guardado!")
        msg.setText("Tema actualizado con éxito.\nReiniciando interfaz...")
        msg.setStyleSheet("background-color: #222; color: white;")
        msg.exec()
        
        self.hide()
        self.return_to_main.emit(True) # True = Recargar tema

    def close_no_save(self):
        self.hide()
        self.return_to_main.emit(False) # False = No hacer nada