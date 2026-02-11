from PyQt6.QtWidgets import QPushButton, QFrame, QHBoxLayout, QLabel, QApplication, QGraphicsOpacityEffect, QColorDialog
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QPoint
from modules.config_manager import ConfigManager


def _get_theme():
    """Load theme dynamically each time it's needed."""
    return ConfigManager.load_theme()


class PulseButton(QPushButton):
    def __init__(self, text, parent=None, custom_color=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._anim = QPropertyAnimation(self, b"geometry")
        self._original_geo = None
        
        theme = _get_theme()
        self.accent_color = custom_color if custom_color else theme["accent"]
        self.bg_color = theme["secondary"]
        self.text_color = self.accent_color

        self.update_style()

    def update_style(self, hover=False):
        if hover:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.accent_color}44;
                    color: white; 
                    border: 1px solid white;
                    border-radius: 10px; font-size: 14px; font-weight: bold; padding: 10px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.bg_color}; 
                    color: {self.text_color}; 
                    border: 1px solid {self.accent_color};
                    border-radius: 10px; font-size: 14px; font-weight: bold; padding: 10px;
                }}
            """)

    def enterEvent(self, event):
        if not self._original_geo:
            self._original_geo = self.geometry()
        geo = self.geometry()
        end_geo = QRect(geo.x()-2, geo.y()-2, geo.width()+4, geo.height()+4)
        self.start_anim(end_geo, QEasingCurve.Type.OutQuad)
        self.update_style(hover=True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._original_geo:
            self.start_anim(self._original_geo, QEasingCurve.Type.OutQuad)
        self.update_style(hover=False)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if self._original_geo:
            geo = self._original_geo
            self.start_anim(QRect(geo.x()+2, geo.y()+2, geo.width()-4, geo.height()-4), QEasingCurve.Type.OutBack, 50)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self._original_geo:
            geo = self._original_geo
            self.start_anim(QRect(geo.x()-2, geo.y()-2, geo.width()+4, geo.height()+4), QEasingCurve.Type.OutBack)
        super().mouseReleaseEvent(event)

    def start_anim(self, end_geo, curve, duration=100):
        self._anim.stop()
        self._anim.setDuration(duration)
        self._anim.setStartValue(self.geometry())
        self._anim.setEndValue(end_geo)
        self._anim.setEasingCurve(curve)
        self._anim.start()


class DraggableTitleBar(QFrame):
    def __init__(self, parent=None, title_text="ANYA"):
        super().__init__(parent)
        self.parent_window = parent
        self.setFixedHeight(40)
        
        theme = _get_theme()
        title_bar_color = theme.get('title_bar', theme['background'])
        border_color = theme.get('border', '#333')
        
        self.setStyleSheet(f"background-color: {title_bar_color}; border-bottom: 1px solid {border_color};")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 10, 0)
        
        lbl = QLabel(title_text)
        lbl.setStyleSheet(f"color: {theme['accent']}; font-family: 'Segoe UI'; font-weight: bold; letter-spacing: 2px;")
        
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(30, 30)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton { border: none; color: #666; font-size: 14px; border-radius: 15px; }
            QPushButton:hover { background-color: #ff4444; color: white; }
        """)
        btn_close.clicked.connect(QApplication.instance().quit)
        
        layout.addWidget(lbl)
        layout.addStretch()
        layout.addWidget(btn_close)
        self.old_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.parent_window.move(self.parent_window.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None


def animate_window_open(window):
    window.setWindowOpacity(0)
    window.show()
    original_pos = window.pos()
    start_pos = QPoint(original_pos.x(), original_pos.y() + 30)
    window.move(start_pos)

    window.anim_fade = QPropertyAnimation(window, b"windowOpacity")
    window.anim_fade.setDuration(400)
    window.anim_fade.setStartValue(0)
    window.anim_fade.setEndValue(1)
    window.anim_fade.setEasingCurve(QEasingCurve.Type.InOutQuad)
    window.anim_fade.start()

    window.anim_slide = QPropertyAnimation(window, b"pos")
    window.anim_slide.setDuration(500)
    window.anim_slide.setStartValue(start_pos)
    window.anim_slide.setEndValue(original_pos)
    window.anim_slide.setEasingCurve(QEasingCurve.Type.OutBack)
    window.anim_slide.start()