import sys
import json
import os
from datetime import datetime

from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                             QHBoxLayout, QLineEdit, QDateEdit, QComboBox, QScrollArea, 
                             QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QSize
from PyQt6.QtGui import QFont, QColor, QCursor

<<<<<<< Updated upstream
TASKS_FILE = "tasks.json"
=======
# Importamos los componentes visuales
from modules.ui_components import DraggableTitleBar, PulseButton
from modules.config_manager import ConfigManager
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes

class TaskManager:
    @staticmethod
    def load_tasks():
<<<<<<< Updated upstream
<<<<<<< Updated upstream
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
=======
=======
>>>>>>> Stashed changes
        if not os.path.exists(TASKS_FILE):
            return []
        try:
            with open(TASKS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []

    @staticmethod
    def save_tasks(tasks):
        with open(TASKS_FILE, 'w') as f:
            json.dump(tasks, f, indent=4)

    @staticmethod
    def get_smart_priority_color(tasks):
        if not tasks:
            return None
        today = datetime.now().date()
        min_days = float('inf')
        found_any = False
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
        for t in tasks:
            try:
                deadline_str = t.get('deadline')
                if not deadline_str: continue
                
                d = datetime.strptime(deadline_str, "%Y-%m-%d").date()
                diff = (d - today).days
                
                if diff < min_days:
                    min_days = diff
                    found_any = True
<<<<<<< Updated upstream
<<<<<<< Updated upstream
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
=======
=======
>>>>>>> Stashed changes
            except Exception:
                continue
        if not found_any:
            return None
        if min_days < 0:
            return "#ff0000"
        if min_days == 0:
            return "#ff4500"
        if min_days <= 2:
            return "#ffcc00"
        if min_days <= 7:
            return "#00a8e8"
        return "#00ff7f"

    @staticmethod
    def sort_key(task):
        """Safe sort key that handles missing/invalid deadlines."""
        deadline_str = task.get('deadline', '')
        if not deadline_str:
            return '9999-12-31'
        try:
            datetime.strptime(deadline_str, "%Y-%m-%d")
            return deadline_str
        except (ValueError, TypeError):
            return '9999-12-31'

class TaskCard(QFrame):
    deleted = pyqtSignal()

    def __init__(self, task_data, theme, parent=None):
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
<<<<<<< Updated upstream
        
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
        title = QLabel(task_data.get("title", "Misión"))
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet("border: none; background: transparent;")
        
        # Lógica de tiempo para el texto
        deadline = task_data.get("deadline")
        cat = task_data.get("category", "General")
<<<<<<< Updated upstream
<<<<<<< Updated upstream
=======
        
        deadline = task_data.get("deadline")
        cat = task_data.get("category", "General")
>>>>>>> Stashed changes
=======
        
        deadline = task_data.get("deadline")
        cat = task_data.get("category", "General")
>>>>>>> Stashed changes
        try:
            d_date = datetime.strptime(deadline, "%Y-%m-%d").date()
            days = (d_date - datetime.now().date()).days
<<<<<<< Updated upstream
<<<<<<< Updated upstream
            
            # Texto descriptivo del tiempo
            if days == 0: 
=======
=======
>>>>>>> Stashed changes
            if days == 0:
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
<<<<<<< Updated upstream
        
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
        info_layout.addWidget(title)
        info_layout.addWidget(sub)
        
        btn_done = QPushButton("✔")
        btn_done.setFixedSize(40, 30)
        btn_done.setStyleSheet(f"border: 1px solid {border_color}; color: {border_color};")
        btn_done.clicked.connect(self.complete)

        layout.addLayout(info_layout)
        layout.addStretch()
<<<<<<< Updated upstream
<<<<<<< Updated upstream
        layout.addWidget(btn_done)

    def complete(self):
        self.deleted.emit()

=======
=======
>>>>>>> Stashed changes
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
        self.setMinimumHeight(0)

    def animate_completion(self):
        self.setStyleSheet("QFrame { background-color: rgba(0, 255, 127, 0.2); border-radius: 10px; border-left: 6px solid #00ff7f; }")
        self.btn_done.hide()
        self.group_exit = QParallelAnimationGroup(self)
        anim_shrink = QPropertyAnimation(self, b"maximumHeight")
        anim_shrink.setDuration(300)
        anim_shrink.setStartValue(self.target_height)
        anim_shrink.setEndValue(0)
        anim_shrink.setEasingCurve(QEasingCurve.Type.InBack)
        anim_fade = QPropertyAnimation(self.opacity_effect, b"opacity")
        anim_fade.setDuration(300)
        anim_fade.setStartValue(1)
        anim_fade.setEndValue(0)
        self.group_exit.addAnimation(anim_shrink)
        self.group_exit.addAnimation(anim_fade)
        self.group_exit.finished.connect(self.deleted.emit)
        self.group_exit.start()

        self.group_exit = QParallelAnimationGroup(self)
        
        anim_shrink = QPropertyAnimation(self, b"maximumHeight")
        anim_shrink.setDuration(300)
        anim_shrink.setStartValue(self.target_height)
        anim_shrink.setEndValue(0)
        anim_shrink.setEasingCurve(QEasingCurve.Type.InBack)
        
        anim_fade = QPropertyAnimation(self.opacity_effect, b"opacity")
        anim_fade.setDuration(300)
        anim_fade.setStartValue(1)
        anim_fade.setEndValue(0)
        
        self.group_exit.addAnimation(anim_shrink)
        self.group_exit.addAnimation(anim_fade)
        self.group_exit.finished.connect(self.deleted.emit)
        self.group_exit.start()

# --- APP PRINCIPAL DE HORARIOS ---
>>>>>>> Stashed changes
class ScheduleApp(QMainWindow):
    return_to_main = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aura :: Misiones")
        self.resize(800, 600)
<<<<<<< Updated upstream
        self.setStyleSheet(STYLES)
        self.tasks = TaskManager.load_tasks()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.layout = QVBoxLayout(main_widget)
        self.layout.setContentsMargins(20,20,20,20)

=======
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # CARGAR TEMA Y APLICAR GLOBALMENTE
        self.theme = ConfigManager.load_theme()
        bg_style = f"background-color: {self.theme['background']};"
        if self.theme.get('use_background') and self.theme.get('background_image'):
            bg_path = self.theme['background_image'].replace('\\', '/')
            bg_style = f"background-image: url('{bg_path}'); background-repeat: no-repeat; background-position: center; background-size: cover;"

        self.setStyleSheet(f"""
            QMainWindow {{ {bg_style} border: 1px solid {self.theme.get('border', '#333')}; }}
            QLabel {{ color: {self.theme['text']}; font-family: 'Segoe UI'; }}
            QLineEdit, QComboBox, QDateEdit {{
                background-color: {self.theme['secondary']}; color: {self.theme['text']}; 
                border: 1px solid {self.theme.get('border', '#444')}; padding: 8px; border-radius: 4px; font-family: 'Segoe UI';
            }}
            QPushButton {{
                background-color: {self.theme['secondary']}; color: {self.theme['accent']};
                border: 1px solid {self.theme['accent']}; padding: 8px; border-radius: 4px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {self.theme['accent']}22; }}
        """)
        
        self.tasks = TaskManager.load_tasks()
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Barra Personalizada
        self.title_bar = DraggableTitleBar(self, "AURA :: MISIONES")
        self.main_layout.addWidget(self.title_bar)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        
>>>>>>> Stashed changes
        # Header
        header = QHBoxLayout()
        btn_back = QPushButton("<< VOLVER")
        btn_back.setFixedSize(100, 30)
        btn_back.clicked.connect(self.go_back)
<<<<<<< Updated upstream
<<<<<<< Updated upstream
        
        lbl_title = QLabel("CENTRO DE MANDO")
        lbl_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #e0e0e0; margin-left: 10px;")
        
=======
        lbl_title = QLabel("CENTRO DE MANDO")
        lbl_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl_title.setStyleSheet(f"color: {self.theme['accent']};")
>>>>>>> Stashed changes
=======
        lbl_title = QLabel("CENTRO DE MANDO")
        lbl_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl_title.setStyleSheet(f"color: {self.theme['accent']};")
>>>>>>> Stashed changes
        header.addWidget(btn_back)
        header.addWidget(lbl_title)
        header.addStretch()
        self.layout.addLayout(header)

<<<<<<< Updated upstream
<<<<<<< Updated upstream
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

=======
=======
>>>>>>> Stashed changes
        creator_frame = QFrame()
        creator_frame.setStyleSheet(f"background-color: {self.theme['secondary']}; border-radius: 8px;")
        c_layout = QHBoxLayout(creator_frame)
        self.inp_title = QLineEdit()
        self.inp_title.setPlaceholderText("Nueva Misión...")
        self.inp_cat = QLineEdit()
        self.inp_cat.setPlaceholderText("Categoría")
        self.inp_cat.setFixedWidth(150)
        self.cmb_urgency = QComboBox()
        self.cmb_urgency.addItems(["BAJA", "MEDIA", "ALTA", "CRÍTICO"])
        self.cmb_urgency.setFixedWidth(100)
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
        self.inp_date = QDateEdit()
        self.inp_date.setDate(QDate.currentDate().addDays(1))
        self.inp_date.setCalendarPopup(True)
        self.inp_date.setFixedWidth(110)
<<<<<<< Updated upstream
<<<<<<< Updated upstream
        self.inp_date.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_add = QPushButton("AGREGAR")
        btn_add.clicked.connect(self.add_task)

=======
        btn_add = QPushButton("AGREGAR")
        btn_add.clicked.connect(self.add_task)
>>>>>>> Stashed changes
=======
        btn_add = QPushButton("AGREGAR")
        btn_add.clicked.connect(self.add_task)
>>>>>>> Stashed changes
        c_layout.addWidget(self.inp_title, 2)
        c_layout.addWidget(self.inp_cat, 1)
        c_layout.addWidget(self.cmb_urgency)
        c_layout.addWidget(self.inp_date)
        c_layout.addWidget(btn_add)
        
        self.layout.addWidget(creator_frame)

<<<<<<< Updated upstream
<<<<<<< Updated upstream
        # Lista
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.t_layout = QVBoxLayout(self.container)
        self.t_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.container)
<<<<<<< Updated upstream
<<<<<<< Updated upstream
        
        self.layout.addWidget(self.scroll)
        self.refresh()

    def add_task(self):
        if not self.inp_title.text(): return
=======
=======
>>>>>>> Stashed changes
        self.content_layout.addWidget(self.scroll)
        self.main_layout.addWidget(self.content_widget)
        
        self.refresh(animate=False)

    def add_task(self):
        if not self.inp_title.text():
            return
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
<<<<<<< Updated upstream
            self.t_layout.itemAt(i).widget().setParent(None)
            
        # Ordenar estrictamente por fecha de entrega
        sorted_tasks = sorted(self.tasks, key=lambda x: x['deadline'])

        for t in sorted_tasks:
            card = TaskCard(t)
            card.deleted.connect(lambda val=t: self.remove_task(val))
            self.t_layout.addWidget(card)
=======
=======
>>>>>>> Stashed changes
            widget = self.t_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        sorted_tasks = sorted(self.tasks, key=TaskManager.sort_key)
        for t in sorted_tasks:
            self.add_single_card(t, animate=animate)

    def add_single_card(self, t, animate=False):
        card = TaskCard(t, self.theme)
        card.deleted.connect(lambda val=t: self.remove_task(val))
        self.t_layout.addWidget(card)
        if animate:
            card.animate_entry()
        else:
            card.setFixedHeight(90)
            card.opacity_effect.setOpacity(1)
>>>>>>> Stashed changes

    def go_back(self):
        self.hide()
        self.return_to_main.emit()