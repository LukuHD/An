import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Tus módulos
from modules.reference import ReferenceFrame
from modules.schedule_tool import ScheduleApp, TaskManager
from modules.settings_tool import SettingsApp
from modules.ui_components import PulseButton, DraggableTitleBar, animate_window_open
from modules.config_manager import ConfigManager
from modules.mascot import RafayelMascot # Importación de la mascota

class MainDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(700, 480)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Cargar Tema
        self.theme = ConfigManager.load_theme()
        
        # Fondo translúcido
        if not (self.theme.get('use_background') and self.theme.get('background_image')):
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.apply_theme()

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.title_bar = DraggableTitleBar(self, "ANYA :: HUB")
        self.main_layout.addWidget(self.title_bar)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(50, 20, 50, 40)
        
        self.header = QLabel("ANYA")
        self.header.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header.setStyleSheet(f"color: {self.theme['accent']}; letter-spacing: 5px; margin-bottom: 10px;")
        
        self.grid = QGridLayout()
        self.grid.setSpacing(20)

        self.btn_ref = PulseButton("📂 REFERENCIAS")
        self.btn_ref.setFixedSize(200, 100)
        self.btn_ref.clicked.connect(self.open_ref)

        self.btn_sch = PulseButton("📅 HORARIOS")
        self.btn_sch.setFixedSize(200, 100)
        self.btn_sch.clicked.connect(self.open_sch)
        
        self.btn_set = PulseButton("🎨 AJUSTES")
        self.btn_set.setFixedSize(200, 100)
        self.btn_set.clicked.connect(self.open_settings)

        self.grid.addWidget(self.btn_ref, 0, 0)
        self.grid.addWidget(self.btn_sch, 0, 1)
        self.grid.addWidget(self.btn_set, 1, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)

        self.content_layout.addWidget(self.header)
        self.content_layout.addLayout(self.grid)
        self.content_layout.addStretch()

        self.main_layout.addWidget(self.content_widget)

        self.ref_win = None
        self.sch_win = None
        self.set_win = None

        self.check_urgency_status()

        # Iniciar Mascota
        self.mascot = RafayelMascot()
        self.mascot.show()

    def apply_theme(self):
        bg_style = f"background-color: {self.theme['background']};"
        if self.theme.get('use_background') and self.theme.get('background_image'):
            bg_path = self.theme['background_image'].replace('\\', '/')
            bg_style = f"background-image: url('{bg_path}'); background-repeat: no-repeat; background-position: center; background-size: cover;"

        border_color = self.theme.get('border', '#333')
        self.setStyleSheet(f"""
            QMainWindow {{ {bg_style} border: 1px solid {border_color}; }}
            QLabel {{ color: {self.theme['text']}; font-family: 'Segoe UI'; }}
        """)

    def check_urgency_status(self):
        tasks = TaskManager.load_tasks()
        urgent_color = TaskManager.get_smart_priority_color(tasks)
        if urgent_color:
            self.btn_sch.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.theme['secondary']}; color: {urgent_color};
                    border: 2px solid {urgent_color}; border-radius: 10px;
                    font-size: 14px; font-weight: bold;
                }}
            """)
            self.btn_sch.setText(f"📅 HORARIOS\n({len(tasks)} Misiones)")
        else:
            self.btn_sch.setText("📅 HORARIOS\n(Todo limpio)")

    def open_ref(self):
        if hasattr(self, 'mascot'):
            self.mascot.react_to_context("reference")
        if not self.ref_win:
            self.ref_win = ReferenceFrame() 
            self.ref_win.return_to_main.connect(self.show_main_and_refresh)
        self.hide()
        self.ref_win.show()
        animate_window_open(self.ref_win)

    def open_sch(self):
        if hasattr(self, 'mascot'):
            self.mascot.react_to_context("schedule")
            
        if not self.sch_win:
            self.sch_win = ScheduleApp()
            self.sch_win.return_to_main.connect(self.show_main_and_refresh)
            self.sch_win.task_changed.connect(self.mascot.notify_task_completed) 
        self.hide()
        animate_window_open(self.sch_win)

    def open_settings(self):
        if hasattr(self, 'mascot'):
            self.mascot.react_to_context("settings")
        if not self.set_win:
            self.set_win = SettingsApp()
            self.set_win.return_to_main.connect(self.handle_settings_close)
        self.hide()
        animate_window_open(self.set_win)

    def handle_settings_close(self, changed):
        if changed:
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            self.show_main_and_refresh()

    def show_main_and_refresh(self):
        self.check_urgency_status()
        if hasattr(self, 'mascot'):
            self.mascot.is_reacting = False
            # Forzamos a que se oculte el globo viejo antes de mostrar el nuevo
            self.mascot.bubble.hide() 
            self.mascot.behavior_timer.start(self.mascot.BEHAVIOR_TIMER_INTERVAL)
            self.mascot.set_state("happy")
            # El mensaje de bienvenida sí puede desaparecer solo
            self.mascot.say("¡Bienvenido de vuelta!", autohide=True) 
        animate_window_open(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainDashboard()
    w.show()
    sys.exit(app.exec())