import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QGridLayout, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QCursor

from modules.reference import OverlayApp
from modules.schedule_tool import ScheduleApp, TaskManager # Importamos el gestor

class MainDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AURA :: Hub")
        self.resize(700, 450)
        
        # Estilo Global con Cursors arreglados
        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }
            QLabel { color: #e0e0e0; font-family: 'Segoe UI'; }
            QPushButton {
                background-color: #1e1e24; color: #00a8e8;
                border: 1px solid #00a8e8; border-radius: 8px;
                font-size: 14px; font-weight: bold; padding: 20px;
                qproperty-cursor: pointingHandCursor; /* Cursor Manita */
            }
            QPushButton:hover { background-color: rgba(0, 168, 232, 20); color: white; }
        """)

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QVBoxLayout(self.central)
        self.layout.setContentsMargins(50, 50, 50, 50)
        
        self.header = QLabel("AURA SUITE")
        self.header.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header.setStyleSheet("color: #00a8e8; letter-spacing: 5px;")
        
        self.grid = QGridLayout()
        self.grid.setSpacing(20)

        self.btn_ref = QPushButton("📂 REFERENCIAS")
        self.btn_ref.clicked.connect(self.open_ref)

        self.btn_sch = QPushButton("📅 HORARIOS")
        self.btn_sch.clicked.connect(self.open_sch)

        self.grid.addWidget(self.btn_ref, 0, 0)
        self.grid.addWidget(self.btn_sch, 0, 1)

        self.layout.addWidget(self.header)
        self.layout.addLayout(self.grid)
        self.layout.addStretch()

        self.ref_win = None
        self.sch_win = None

        # Revisar tareas al iniciar
        self.check_urgency_status()

    def check_urgency_status(self):
        tasks = TaskManager.load_tasks()
        # CAMBIO AQUÍ
        urgent_color = TaskManager.get_smart_priority_color(tasks)
        
        if urgent_color:
            self.btn_sch.setStyleSheet(f"""
                QPushButton {{
                    background-color: #1e1e24; 
                    color: {urgent_color};
                    border: 2px solid {urgent_color};
                    border-radius: 8px;
                    font-size: 14px; font-weight: bold; padding: 20px;
                    qproperty-cursor: pointingHandCursor;
                }}
                QPushButton:hover {{ background-color: {urgent_color}22; }}
            """)
            self.btn_sch.setText(f"📅 HORARIOS\n({len(tasks)} Misiones)")
        else:
            self.btn_sch.setText("📅 HORARIOS\n(Todo limpio)")
            # Restaurar estilo por defecto si quieres, o dejar el azul chill

    def open_ref(self):
        if not self.ref_win:
            self.ref_win = OverlayApp()
            self.ref_win.return_to_main.connect(self.show_main_and_refresh)
        self.hide()
        self.ref_win.show()

    def open_sch(self):
        if not self.sch_win:
            self.sch_win = ScheduleApp()
            self.sch_win.return_to_main.connect(self.show_main_and_refresh)
        self.hide()
        self.sch_win.show()

    def show_main_and_refresh(self):
        """Al volver al menú, actualizamos el estado de las tareas."""
        self.check_urgency_status()
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainDashboard()
    w.show()
    sys.exit(app.exec())