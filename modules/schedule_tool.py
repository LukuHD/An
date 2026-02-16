import sys
import json
import os
from datetime import datetime

from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                             QHBoxLayout, QLineEdit, QDateEdit, QComboBox, QScrollArea, 
                             QFrame, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
from PyQt6.QtGui import QFont, QColor, QPalette, QBrush, QPixmap

# Importamos los componentes visuales y el gestor de configuración
from modules.config_manager import ConfigManager
from modules.ui_components import DraggableTitleBar, PulseButton

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASKS_FILE = os.path.join(_BASE_DIR, "tasks.json")

# --- TASK MANAGER (EL CEREBRO) ---
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
        if not tasks: return None
        today = datetime.now().date()
        min_days = 9999
        found_any = False
        
        for t in tasks:
            try:
                deadline_str = t.get('deadline')
                if not deadline_str:
                    continue
                d = datetime.strptime(deadline_str, "%Y-%m-%d").date()
                diff = (d - today).days
                if diff < min_days:
                    min_days = diff
                    found_any = True
            except:
                continue

        if not found_any: return None
        
        # Reglas de color por tiempo
        if min_days < 0: return "#ff0000"     # Vencido (Rojo)
        if min_days == 0: return "#ff4500"    # Hoy (Naranja)
        if min_days <= 2: return "#ffcc00"    # <= 2 Días (Amarillo)
        if min_days <= 7: return "#00a8e8"    # <= 7 Días (Azul)
        return "#00ff7f"                      # Relax (Verde)

# --- ESTILOS CSS ---
STYLES = """
QMainWindow { background-color: #121212; border: 1px solid #333; }
QLabel { color: #e0e0e0; font-family: 'Segoe UI'; }
QLineEdit, QComboBox, QDateEdit {
    background-color: #1e1e24; color: #fff; border: 1px solid #444; 
    padding: 8px; border-radius: 4px; font-family: 'Segoe UI';
}
QPushButton {
    background-color: #1e1e24; color: #00a8e8; border: 1px solid #00a8e8;
    padding: 8px; border-radius: 4px; font-weight: bold;
}
QPushButton:hover { background-color: rgba(0, 168, 232, 20); border: 1px solid #fff; }
"""

# --- TARJETA DE TAREA (ANIMADA) ---
class TaskCard(QFrame):
    deleted = pyqtSignal() 

    def __init__(self, task_data, parent=None):
        super().__init__(parent)
        self.setFixedHeight(0) 
        self.target_height = 90
        
        urgency = task_data.get("urgency", "BAJA")
        colors = {"CRÍTICO": "#ff0000", "ALTA": "#ff9900", "MEDIA": "#ffff00", "BAJA": "#00a8e8"}
        self.border_color = colors.get(urgency, "#00a8e8")

        self.setStyleSheet(f"""
            QFrame {{
                background-color: #1a1a20; border-radius: 10px;
                border-left: 6px solid {self.border_color};
            }}
            QFrame:hover {{ background-color: #252530; }}
        """)

        layout = QHBoxLayout(self)
        info_layout = QVBoxLayout()
        
        title = QLabel(task_data.get("title", "Misión"))
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet("border: none; background: transparent;")
        
        deadline = task_data.get("deadline")
        cat = task_data.get("category", "General")
        
        try:
            d_date = datetime.strptime(deadline, "%Y-%m-%d").date()
            days = (d_date - datetime.now().date()).days
            if days == 0: 
                time_str = "¡ES HOY!"; time_color = "#ff4500"
            elif days < 0: 
                time_str = f"VENCIDO hace {abs(days)} días"; time_color = "#ff0000"
            elif days <= 2: 
                time_str = f"Quedan {days} días"; time_color = "#ffcc00"
            else: 
                time_str = f"Faltan {days} días"; time_color = "#00ff7f"
        except: 
            time_str = "Sin fecha"; time_color = "#888"

        sub = QLabel(f"[{cat}] • {time_str}")
        sub.setStyleSheet(f"color: {time_color}; font-size: 11px; border: none; background: transparent;")
        
        info_layout.addWidget(title)
        info_layout.addWidget(sub)
        
        self.btn_done = QPushButton("✔")
        self.btn_done.setFixedSize(40, 30)
        self.btn_done.setStyleSheet(f"border: 1px solid {self.border_color}; color: {self.border_color};")
        self.btn_done.clicked.connect(self.animate_completion)

        layout.addLayout(info_layout)
        layout.addStretch()
        layout.addWidget(self.btn_done)
        
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0) 

    def animate_entry(self):
        self.group = QParallelAnimationGroup(self)
        anim_height = QPropertyAnimation(self, b"maximumHeight")
        anim_height.setDuration(400)
        anim_height.setStartValue(0)
        anim_height.setEndValue(self.target_height)
        anim_height.setEasingCurve(QEasingCurve.Type.OutBack)
        
        anim_fade = QPropertyAnimation(self.opacity_effect, b"opacity")
        anim_fade.setDuration(400)
        anim_fade.setStartValue(0)
        anim_fade.setEndValue(1)
        
        self.group.addAnimation(anim_height)
        self.group.addAnimation(anim_fade)
        self.group.start()

    def animate_completion(self):
        self.setStyleSheet("QFrame { background-color: rgba(0, 255, 127, 0.2); border-radius: 10px; border-left: 6px solid #00ff7f; }")
        self.btn_done.hide()
        self.group_exit = QParallelAnimationGroup(self)
        anim_shrink = QPropertyAnimation(self, b"maximumHeight")
        anim_shrink.setDuration(300)
        anim_shrink.setStartValue(self.target_height)
        anim_shrink.setEndValue(0)
        anim_fade = QPropertyAnimation(self.opacity_effect, b"opacity")
        anim_fade.setDuration(300)
        anim_fade.setStartValue(1)
        anim_fade.setEndValue(0)
        self.group_exit.addAnimation(anim_shrink)
        self.group_exit.addAnimation(anim_fade)
        self.group_exit.finished.connect(self.deleted.emit)
        self.group_exit.start()

# --- APP PRINCIPAL DE HORARIOS ---
class ScheduleApp(QMainWindow):
    return_to_main = pyqtSignal()
    task_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(STYLES)
        self.tasks = TaskManager.load_tasks()
        self.theme = ConfigManager.load_theme()

        if not (self.theme.get('use_background') and self.theme.get('background_image')):
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.apply_theme()

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        
        self.title_bar = DraggableTitleBar(self, "ANYA :: MISIONES")
        self.main_layout.addWidget(self.title_bar)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20,20,20,20)
        
        header = QHBoxLayout()
        btn_back = PulseButton("<< VOLVER")
        btn_back.setFixedSize(100, 40)
        btn_back.clicked.connect(self.go_back)
        
        lbl_title = QLabel("CENTRO DE MANDO")
        lbl_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        
        header.addWidget(btn_back)
        header.addWidget(lbl_title)
        header.addStretch()
        self.content_layout.addLayout(header)

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
        for i, c in enumerate(["#00a8e8", "#ffff00", "#ff9900", "#ff0000"]):
            self.cmb_urgency.setItemData(i, QColor(c), Qt.ItemDataRole.ForegroundRole)
            
        self.inp_date = QDateEdit()
        self.inp_date.setDate(QDate.currentDate().addDays(1))
        self.inp_date.setCalendarPopup(True)
        self.inp_date.setFixedWidth(110)
        
        btn_add = QPushButton("AGREGAR")
        btn_add.clicked.connect(self.add_task)
        
        c_layout.addWidget(self.inp_title, 2)
        c_layout.addWidget(self.inp_cat, 1)
        c_layout.addWidget(self.cmb_urgency)
        c_layout.addWidget(self.inp_date)
        c_layout.addWidget(btn_add)
        self.content_layout.addWidget(creator_frame)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.t_layout = QVBoxLayout(self.container)
        self.t_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.container)
        self.content_layout.addWidget(self.scroll)
        
        self.main_layout.addWidget(self.content_widget)
        self.refresh(animate=False)

    def apply_theme(self):
        self.theme = ConfigManager.load_theme()
        if self.theme.get('use_background') and self.theme.get('background_image'):
            path = self.theme.get('background_image')
            if os.path.exists(path):
                palette = QPalette()
                pixmap = QPixmap(path)
                scaled_pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                palette.setBrush(QPalette.ColorRole.Window, QBrush(scaled_pixmap))
                self.setPalette(palette)
                self.setAutoFillBackground(True)
        else:
            bg_color = self.theme.get('background', '#121212')
            self.setStyleSheet(STYLES + f"\nQMainWindow {{ background-color: {bg_color}; border: 1px solid #333; }}")

    def resizeEvent(self, event):
        self.apply_theme()
        super().resizeEvent(event)

    def add_task(self):
        title = self.inp_title.text().strip() # .strip() evita misiones vacías
        if not title: 
            return
            
        new_t = {
            "title": title,
            "category": self.inp_cat.text() or "General",
            "urgency": self.cmb_urgency.currentText(),
            "deadline": self.inp_date.date().toString("yyyy-MM-dd")
        }
        self.tasks.append(new_t)
        TaskManager.save_tasks(self.tasks)
        
        # --- LIMPIEZA CORRECTA ---
        self.inp_title.clear() # Ahora sí reconoce 'self' porque está dentro del método
        self.inp_title.setFocus() # Mantiene el cursor ahí para que sigas escribiendo
        
        self.add_single_card(new_t, animate=True)
        self.task_changed.emit()

    def remove_task(self, task):
        if task in self.tasks:
            self.tasks.remove(task)
            TaskManager.save_tasks(self.tasks)
            self.task_changed.emit()
            # Forzamos un refresco para que el layout se reajuste 
            # después de que la animación de la tarjeta termine
            self.refresh(animate=False)

    def refresh(self, animate=False):
        for i in reversed(range(self.t_layout.count())):
            self.t_layout.itemAt(i).widget().setParent(None)
        sorted_tasks = sorted(self.tasks, key=lambda x: x['deadline'])
        for t in sorted_tasks:
            self.add_single_card(t, animate=animate)

    def add_single_card(self, t, animate=False):
        card = TaskCard(t)
        card.deleted.connect(lambda val=t: self.remove_task(val))
        self.t_layout.addWidget(card)
        if animate: card.animate_entry()
        else: 
            card.setFixedHeight(90)
            card.opacity_effect.setOpacity(1)

    def go_back(self):
        self.hide()
        self.return_to_main.emit()