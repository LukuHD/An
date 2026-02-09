import sys
import json
import os
from datetime import datetime

from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                             QHBoxLayout, QLineEdit, QDateEdit, QComboBox, QScrollArea, 
                             QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QSize
from PyQt6.QtGui import QFont, QColor, QCursor

TASKS_FILE = "tasks.json"

class TaskManager:
    @staticmethod
    def load_tasks():
        if not os.path.exists(TASKS_FILE): return []
        try:
            with open(TASKS_FILE, 'r') as f: return json.load(f)
        except: return []

    @staticmethod
    def save_tasks(tasks):
        with open(TASKS_FILE, 'w') as f: json.dump(tasks, f, indent=4)
    
    @staticmethod
    def get_smart_priority_color(tasks):
        """
        LÓGICA BASADA 100% EN TIEMPO (Solicitado por usuario).
        La etiqueta 'Urgencia' es solo informativa, no cambia el color del radar.
        """
        if not tasks: return None
        
        today = datetime.now().date()
        min_days = 9999 
        found_any = False

        # Solo nos importa la fecha más cercana
        for t in tasks:
            try:
                deadline_str = t.get('deadline')
                if not deadline_str: continue
                
                d = datetime.strptime(deadline_str, "%Y-%m-%d").date()
                diff = (d - today).days
                
                if diff < min_days:
                    min_days = diff
                    found_any = True
            except:
                continue

        if not found_any: return None # No hay fechas válidas

        # --- REGLAS DE TIEMPO ESTRICTAS ---
        # 1. PÁNICO (Vencido)
        if min_days < 0: return "#ff0000"     # Rojo Neón
        
        # 2. URGENCIA REAL (Hoy)
        if min_days == 0: return "#ff4500"    # Naranja Rojizo
        
        # 3. PRECAUCIÓN (Mañana o pasado)
        if min_days <= 2: return "#ffcc00"    # Amarillo
        
        # 4. ATENCIÓN (Esta semana)
        if min_days <= 7: return "#00a8e8"    # Azul
        
        # 5. RELAX (Futuro lejano)
        return "#00ff7f"                      # Verde Primavera

# --- ESTILOS VISUALES ---
STYLES = """
QMainWindow { background-color: #121212; }
QLabel { color: #e0e0e0; font-family: 'Segoe UI'; }
QLineEdit, QComboBox, QDateEdit {
    background-color: #1e1e24; color: #fff; border: 1px solid #444; 
    padding: 8px; border-radius: 4px; font-family: 'Segoe UI';
}
QPushButton {
    background-color: #1e1e24; color: #00a8e8; border: 1px solid #00a8e8;
    padding: 8px; border-radius: 4px; font-weight: bold;
    qproperty-cursor: pointingHandCursor;
}
QPushButton:hover { background-color: rgba(0, 168, 232, 20); border: 1px solid #fff; }
"""

class TaskCard(QFrame):
    deleted = pyqtSignal() 

    def __init__(self, task_data, parent=None):
        super().__init__(parent)
        self.setFixedHeight(90)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        
        # El borde de la tarjeta SÍ respeta la categoría/urgencia que ella eligió
        # para que visualmente distinga qué tipo de tarea es, 
        # PERO el radar y el main solo miran el tiempo.
        urgency = task_data.get("urgency", "BAJA")
        colors = {"CRÍTICO": "#ff0000", "ALTA": "#ff9900", "MEDIA": "#ffff00", "BAJA": "#00a8e8"}
        border_color = colors.get(urgency, "#00a8e8")

        self.setStyleSheet(f"""
            QFrame {{
                background-color: #1a1a20; border-radius: 10px;
                border-left: 6px solid {border_color};
            }}
            QFrame:hover {{ background-color: #252530; }}
        """)

        layout = QHBoxLayout(self)
        info_layout = QVBoxLayout()
        
        title = QLabel(task_data.get("title", "Misión"))
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet("border: none; background: transparent;")
        
        # Lógica de tiempo para el texto
        deadline = task_data.get("deadline")
        cat = task_data.get("category", "General")
        try:
            d_date = datetime.strptime(deadline, "%Y-%m-%d").date()
            days = (d_date - datetime.now().date()).days
            
            # Texto descriptivo del tiempo
            if days == 0: 
                time_str = "¡ES HOY!"
                time_color = "#ff4500" # Naranja fuerte
            elif days < 0: 
                time_str = f"VENCIDO hace {abs(days)} días"
                time_color = "#ff0000" # Rojo
            elif days <= 2:
                time_str = f"Quedan {days} días"
                time_color = "#ffcc00" # Amarillo
            else: 
                time_str = f"Faltan {days} días"
                time_color = "#00ff7f" # Verde

        except:
            time_str = "Sin fecha"
            time_color = "#888"

        sub = QLabel(f"[{cat}] • {time_str}")
        sub.setStyleSheet(f"color: {time_color}; font-size: 11px; border: none; background: transparent;")
        
        info_layout.addWidget(title)
        info_layout.addWidget(sub)
        
        btn_done = QPushButton("✔")
        btn_done.setFixedSize(40, 30)
        btn_done.setStyleSheet(f"border: 1px solid {border_color}; color: {border_color};")
        btn_done.clicked.connect(self.complete)

        layout.addLayout(info_layout)
        layout.addStretch()
        layout.addWidget(btn_done)

    def complete(self):
        self.deleted.emit()

class ScheduleApp(QMainWindow):
    return_to_main = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aura :: Misiones")
        self.resize(800, 600)
        self.setStyleSheet(STYLES)
        self.tasks = TaskManager.load_tasks()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.layout = QVBoxLayout(main_widget)
        self.layout.setContentsMargins(20,20,20,20)

        # Header
        header = QHBoxLayout()
        btn_back = QPushButton("<< VOLVER")
        btn_back.setFixedSize(100, 30)
        btn_back.clicked.connect(self.go_back)
        
        lbl_title = QLabel("CENTRO DE MANDO")
        lbl_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #e0e0e0; margin-left: 10px;")
        
        header.addWidget(btn_back)
        header.addWidget(lbl_title)
        header.addStretch()
        self.layout.addLayout(header)

        # Creador
        creator_frame = QFrame()
        creator_frame.setStyleSheet("background-color: #2a2a35; border-radius: 8px;")
        c_layout = QHBoxLayout(creator_frame)
        
        self.inp_title = QLineEdit()
        self.inp_title.setPlaceholderText("Nueva Misión...")
        
        self.inp_cat = QLineEdit()
        self.inp_cat.setPlaceholderText("Categoría")
        self.inp_cat.setFixedWidth(150)
        
        self.cmb_urgency = QComboBox()
        self.cmb_urgency.addItems(["BAJA", "MEDIA", "ALTA", "CRÍTICO"])
        self.cmb_urgency.setFixedWidth(100)
        
        # Colores visuales en el combo (solo estética)
        for i, col in enumerate(["#00a8e8", "#ffff00", "#ff9900", "#ff0000"]):
            self.cmb_urgency.setItemData(i, QColor(col), Qt.ItemDataRole.ForegroundRole)

        self.inp_date = QDateEdit()
        self.inp_date.setDate(QDate.currentDate().addDays(1))
        self.inp_date.setCalendarPopup(True)
        self.inp_date.setFixedWidth(110)
        self.inp_date.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_add = QPushButton("AGREGAR")
        btn_add.clicked.connect(self.add_task)

        c_layout.addWidget(self.inp_title, 2)
        c_layout.addWidget(self.inp_cat, 1)
        c_layout.addWidget(self.cmb_urgency)
        c_layout.addWidget(self.inp_date)
        c_layout.addWidget(btn_add)
        
        self.layout.addWidget(creator_frame)

        # Lista
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.t_layout = QVBoxLayout(self.container)
        self.t_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.container)
        
        self.layout.addWidget(self.scroll)
        self.refresh()

    def add_task(self):
        if not self.inp_title.text(): return
        new_t = {
            "title": self.inp_title.text(),
            "category": self.inp_cat.text() or "General",
            "urgency": self.cmb_urgency.currentText(),
            "deadline": self.inp_date.date().toString("yyyy-MM-dd")
        }
        self.tasks.append(new_t)
        TaskManager.save_tasks(self.tasks)
        self.inp_title.clear()
        self.refresh()

    def remove_task(self, task):
        if task in self.tasks:
            self.tasks.remove(task)
            TaskManager.save_tasks(self.tasks)
            self.refresh()

    def refresh(self):
        for i in reversed(range(self.t_layout.count())):
            self.t_layout.itemAt(i).widget().setParent(None)
            
        # Ordenar estrictamente por fecha de entrega
        sorted_tasks = sorted(self.tasks, key=lambda x: x['deadline'])

        for t in sorted_tasks:
            card = TaskCard(t)
            card.deleted.connect(lambda val=t: self.remove_task(val))
            self.t_layout.addWidget(card)

    def go_back(self):
        self.hide()
        self.return_to_main.emit()