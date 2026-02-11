import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QColorDialog, QPushButton, QMessageBox, QCheckBox,
                             QFileDialog, QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from modules.ui_components import DraggableTitleBar, PulseButton, animate_window_open
from modules.config_manager import ConfigManager

class ColorPickerBtn(QPushButton):
    """Botón cuadrado que muestra el color seleccionado."""
    def __init__(self, initial_color, label_text):
        super().__init__()
        self.current_color = initial_color
        self.setFixedSize(90, 90)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_style()
        self.setText(label_text)

    def update_style(self):
        # Determine text color based on background brightness
        c = QColor(self.current_color)
        brightness = (c.red() * 299 + c.green() * 587 + c.blue() * 114) / 1000
        text_color = "#000000" if brightness > 128 else "#ffffff"
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_color};
                border: 2px solid #555;
                border-radius: 12px;
                color: {text_color}; font-weight: bold; font-size: 10px;
            }}
            QPushButton:hover {{ border: 2px solid white; }}
        """)

class SettingsApp(QMainWindow):
    return_to_main = pyqtSignal(bool)

    def apply_theme(self):
        """Aplica los colores o la imagen de fondo al estilo de la ventana."""
        self.theme = ConfigManager.load_theme()
        
        if self.theme.get('use_background') and self.theme.get('background_image'):
            from PyQt6.QtGui import QPalette, QBrush, QPixmap
            path = self.theme.get('background_image')
            if os.path.exists(path):
                palette = QPalette()
                pixmap = QPixmap(path)
                # Escalamos la imagen al tamaño de la ventana
                scaled_pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                palette.setBrush(QPalette.ColorRole.Window, QBrush(scaled_pixmap))
                self.setPalette(palette)
                self.setAutoFillBackground(True)
        else:
            # Si no hay imagen, usamos el color de fondo del tema
            self.setStyleSheet(f"""
                QMainWindow {{ 
                    background-color: {self.theme.get('background', '#121212')}; 
                    border: 1px solid {self.theme.get('accent', '#00a8e8')}; 
                }}
            """)


    def __init__(self):
        super().__init__()
        self.resize(550, 700)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        self.theme = ConfigManager.load_theme()

                # Solo hacer el fondo translúcido si NO usamos imagen de fondo
        if not (self.theme.get('use_background') and self.theme.get('background_image')):
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.apply_theme() # Método para pintar

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QVBoxLayout(self.central)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {self.theme['background']}; border: 1px solid {self.theme['accent']}; }}
            QLabel {{ color: {self.theme['text']}; font-family: 'Segoe UI'; }}
        """)

        self.title_bar = DraggableTitleBar(self, "AURA :: CONFIGURACIÓN")
        self.layout.addWidget(self.title_bar)
        
        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        content = QWidget()
        self.c_layout = QVBoxLayout(content)
        self.c_layout.setContentsMargins(30, 15, 30, 30)
        
        lbl = QLabel("PERSONALIZACIÓN VISUAL")
        lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"color: {self.theme['accent']};")
        self.c_layout.addWidget(lbl)
        
        lbl_sub = QLabel("Haz clic en los cuadros para cambiar los colores.")
        lbl_sub.setStyleSheet("color: #888; font-size: 11px;")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.c_layout.addWidget(lbl_sub)
        
        # --- SECTION: Main Colors ---
        self._add_section_label("COLORES PRINCIPALES")
        
        grid1 = QGridLayout()
        grid1.setSpacing(12)
        
        self.btn_accent = ColorPickerBtn(self.theme['accent'], "Acento\n(Botones)")
        self.btn_accent.clicked.connect(lambda: self.pick_color("accent", self.btn_accent))
        
        self.btn_bg = ColorPickerBtn(self.theme['background'], "Fondo")
        self.btn_bg.clicked.connect(lambda: self.pick_color("background", self.btn_bg))
        
        self.btn_text = ColorPickerBtn(self.theme['text'], "Texto")
        self.btn_text.clicked.connect(lambda: self.pick_color("text", self.btn_text))
        
        self.btn_secondary = ColorPickerBtn(self.theme['secondary'], "Secundario\n(Tarjetas)")
        self.btn_secondary.clicked.connect(lambda: self.pick_color("secondary", self.btn_secondary))
        
        grid1.addWidget(self.btn_accent, 0, 0)
        grid1.addWidget(self.btn_bg, 0, 1)
        grid1.addWidget(self.btn_text, 0, 2)
        grid1.addWidget(self.btn_secondary, 0, 3)
        self.c_layout.addLayout(grid1)
        
        # --- SECTION: UI Detail Colors ---
        self._add_section_label("DETALLES DE INTERFAZ")
        
        grid2 = QGridLayout()
        grid2.setSpacing(12)
        
        self.btn_border = ColorPickerBtn(self.theme.get('border', '#333333'), "Bordes")
        self.btn_border.clicked.connect(lambda: self.pick_color("border", self.btn_border))
        
        self.btn_titlebar = ColorPickerBtn(self.theme.get('title_bar', '#0a0a0f'), "Barra\nTítulo")
        self.btn_titlebar.clicked.connect(lambda: self.pick_color("title_bar", self.btn_titlebar))
        
        self.btn_card_text = ColorPickerBtn(self.theme.get('card_text', '#ffffff'), "Texto\nTarjetas")
        self.btn_card_text.clicked.connect(lambda: self.pick_color("card_text", self.btn_card_text))
        
        self.btn_highlight = ColorPickerBtn(self.theme.get('highlight', '#00ff7f'), "Resaltado\n(Éxito)")
        self.btn_highlight.clicked.connect(lambda: self.pick_color("highlight", self.btn_highlight))
        
        grid2.addWidget(self.btn_border, 0, 0)
        grid2.addWidget(self.btn_titlebar, 0, 1)
        grid2.addWidget(self.btn_card_text, 0, 2)
        grid2.addWidget(self.btn_highlight, 0, 3)
        self.c_layout.addLayout(grid2)
        
        # --- SECTION: Background Image ---
        self._add_section_label("IMAGEN DE FONDO")
        
        bg_frame = QFrame()
        bg_frame.setStyleSheet(f"background-color: {self.theme['secondary']}; border-radius: 8px; padding: 10px;")
        bg_layout = QVBoxLayout(bg_frame)
        
        self.chk_bg = QCheckBox("Usar imagen de fondo")
        self.chk_bg.setChecked(self.theme.get('use_background', False))
        self.chk_bg.setStyleSheet(f"color: {self.theme['text']}; font-size: 12px;")
        self.chk_bg.stateChanged.connect(self._on_bg_toggle)
        bg_layout.addWidget(self.chk_bg)
        
        bg_path_row = QHBoxLayout()
        self.lbl_bg_path = QLabel(self.theme.get('background_image', '') or "Sin imagen seleccionada")
        self.lbl_bg_path.setStyleSheet("color: #888; font-size: 11px;")
        self.lbl_bg_path.setWordWrap(True)
        
        self.btn_browse = QPushButton("Buscar...")
        self.btn_browse.setFixedSize(80, 28)
        self.btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_browse.setStyleSheet(f"""
            QPushButton {{ background-color: {self.theme['secondary']}; color: {self.theme['accent']}; 
                          border: 1px solid {self.theme['accent']}; border-radius: 4px; font-size: 11px; }}
            QPushButton:hover {{ background-color: {self.theme['accent']}22; }}
        """)
        self.btn_browse.clicked.connect(self._browse_bg_image)
        self.btn_browse.setEnabled(self.chk_bg.isChecked())
        
        self.btn_clear_bg = QPushButton("Quitar")
        self.btn_clear_bg.setFixedSize(60, 28)
        self.btn_clear_bg.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_bg.setStyleSheet("""
            QPushButton { background-color: transparent; color: #ff4444; 
                          border: 1px solid #ff4444; border-radius: 4px; font-size: 11px; }
            QPushButton:hover { background-color: #ff444422; }
        """)
        self.btn_clear_bg.clicked.connect(self._clear_bg_image)
        self.btn_clear_bg.setEnabled(self.chk_bg.isChecked())
        
        bg_path_row.addWidget(self.lbl_bg_path, 1)
        bg_path_row.addWidget(self.btn_browse)
        bg_path_row.addWidget(self.btn_clear_bg)
        bg_layout.addLayout(bg_path_row)
        
        self.c_layout.addWidget(bg_frame)
        self.c_layout.addStretch()
        
        # Action buttons
        self.btn_save = PulseButton("GUARDAR CAMBIOS")
        self.btn_save.clicked.connect(self.save_changes)
        
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setFlat(True)
        self.btn_cancel.setStyleSheet("color: #666; text-decoration: underline;")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.close_no_save)

        self.c_layout.addWidget(self.btn_save)
        self.c_layout.addWidget(self.btn_cancel)
        
        scroll.setWidget(content)
        self.layout.addWidget(scroll)

    def _add_section_label(self, text):
        """Helper to add a styled section label."""
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {self.theme.get('accent', '#00a8e8')}; margin-top: 15px; margin-bottom: 5px;")
        self.c_layout.addWidget(lbl)

    def _on_bg_toggle(self, state):
        enabled = state == 2  # Qt.CheckState.Checked
        self.btn_browse.setEnabled(enabled)
        self.btn_clear_bg.setEnabled(enabled)
        self.theme['use_background'] = enabled

    def _browse_bg_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar imagen de fondo", "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if path:
            self.theme['background_image'] = path
            self.lbl_bg_path.setText(path)

    def _clear_bg_image(self):
        self.theme['background_image'] = ""
        self.lbl_bg_path.setText("Sin imagen seleccionada")

    def pick_color(self, key, btn_widget):
        color = QColorDialog.getColor(QColor(self.theme.get(key, '#ffffff')), self, "Elige un color")
        if color.isValid():
            hex_color = color.name()
            self.theme[key] = hex_color
            btn_widget.current_color = hex_color
            btn_widget.update_style()

    def save_changes(self):
        ConfigManager.save_theme(self.theme)
        msg = QMessageBox(self)
        msg.setWindowTitle("¡Guardado!")
        msg.setText("Tema actualizado con éxito.\nReiniciando interfaz...")
        msg.setStyleSheet("background-color: #222; color: white;")
        msg.exec()
        
        self.hide()
        self.return_to_main.emit(True)

    def close_no_save(self):
        self.hide()
        self.return_to_main.emit(False)