import sys
import json
import os
from typing import Optional, Dict, List, Any
from modules.schedule_tool import TaskManager
from modules.config_manager import ConfigManager
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGraphicsView, QGraphicsScene, 
                             QGraphicsPixmapItem, QGraphicsRectItem, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QWidget, QSystemTrayIcon, QMenu, QStyle, QLabel, 
                             QFrame, QGraphicsItem, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRectF, QEvent
from PyQt6.QtGui import (QPixmap, QPainter, QColor, QAction, QPen, QCursor, 
                         QBrush, QTransform, QMouseEvent, QFont)


def _load_ref_theme():
    """Load theme for reference module."""
    theme = ConfigManager.load_theme()
    return theme


# --- CONSTANTES DE CONFIGURACIÓN ---
class Config:
    RESIZE_MARGIN = 10
    HANDLE_SIZE = 12
    HEADER_HEIGHT = 35
    MIN_WINDOW_SIZE = 200

    @staticmethod
    def get_colors():
        theme = _load_ref_theme()
        return {
            'accent': theme['accent'],
            'bg_dark': theme['background'],
            'text': theme['text'],
            'secondary': theme['secondary'],
            'border': theme.get('border', '#333333'),
            'warn': '#d62828',
        }


def _build_stylesheet():
    """Build stylesheet dynamically from theme."""
    colors = Config.get_colors()
    return f"""
    QMainWindow {{ background: transparent; }}
    QWidget#Container {{ 
        background-color: {colors['bg_dark']}; 
        border: 1px solid {colors['accent']}; 
        border-radius: 8px; 
    }}
    QLabel {{ 
        color: {colors['accent']}; 
        font-family: 'Segoe UI', sans-serif; 
        font-weight: bold; 
    }}
    QPushButton {{ 
        background-color: {colors['secondary']}; 
        color: {colors['accent']}; 
        border: 1px solid {colors['accent']}; 
        padding: 5px; 
        border-radius: 4px; 
        font-weight: bold; 
    }}
    QPushButton:hover {{ background-color: {colors['accent']}33; color: white; }}
    """

# =============================================================================
# CLASES GRÁFICAS (EL LIENZO Y LAS IMÁGENES)
# =============================================================================

class ResizeHandle(QGraphicsRectItem):
    """
    Componente visual que representa el agarre para redimensionar una imagen.
    """
    def __init__(self, parent: 'ImageItem'):
        super().__init__(0, 0, Config.HANDLE_SIZE, Config.HANDLE_SIZE, parent)
        self.parent_item = parent
        colors = Config.get_colors()
        self.setBrush(QBrush(QColor(colors['accent'])))
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        
        self._start_pos: Optional[QPoint] = None
        self._start_scale: float = 1.0

    def mousePressEvent(self, event) -> None:
        """Inicia la operación de escalado."""
        self._start_pos = event.screenPos()
        self._start_scale = self.parent_item.scale()
        event.accept()

    def mouseMoveEvent(self, event) -> None:
        """Calcula el factor de escala basado en el delta del movimiento."""
        if not self._start_pos:
            return

        diff = event.screenPos() - self._start_pos
        # Usamos una constante de sensibilidad (200.0) para suavizar el zoom
        growth_factor = diff.x() / 200.0 
        new_scale = max(0.1, self._start_scale + growth_factor) # Evitamos escala negativa
        
        self.parent_item.setScale(new_scale)
        event.accept()

    def mouseReleaseEvent(self, event) -> None:
        self._start_pos = None
        super().mouseReleaseEvent(event)


class ImageItem(QGraphicsPixmapItem):
    """
    Entidad principal que representa una imagen en el tablero.
    Maneja su propia lógica de renderizado, menú y transformación.
    """
    def __init__(self, pixmap: QPixmap, path: str = ""):
        super().__init__(pixmap)
        self.file_path = path
        self.is_flipped = False
        
        # Configuraciones de optimización de Qt
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.setFlags(
            QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable | 
            QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsPixmapItem.GraphicsItemFlag.ItemIsFocusable
        )
        
        # Escalar imagen si es muy grande al inicio
        if pixmap.width() > 500:
            self.setScale(500 / pixmap.width())

        # Composición: La imagen "tiene un" Handle
        self.handle = ResizeHandle(self)
        self._update_handle_position()

    def _update_handle_position(self) -> None:
        """Recalcula la posición del handle para que siempre esté en la esquina inferior derecha."""
        rect = self.pixmap().rect()
        # Ajustamos restando el tamaño del handle para que quede dentro
        x = rect.width() - Config.HANDLE_SIZE
        y = rect.height() - Config.HANDLE_SIZE
        self.handle.setPos(x, y)

    def paint(self, painter, option, widget) -> None:
        """Sobrescribe el pintado para agregar indicadores visuales de selección."""
        super().paint(painter, option, widget)
        if self.isSelected():
            colors = Config.get_colors()
            painter.setPen(QPen(QColor(colors['accent']), 2, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self.boundingRect())

    def contextMenuEvent(self, event) -> None:
        """Construye y ejecuta el menú contextual."""
        menu = QMenu()
        colors = Config.get_colors()
        menu.setStyleSheet(f"QMenu {{ background-color: #222; color: {colors['accent']}; border: 1px solid {colors['accent']}; }}")
        
        # Mapeo de acciones a métodos
        actions = [
            ("Reflejar (Espejo)", self.flip_image),
            ("Traer al Frente", lambda: self.setZValue(self.zValue() + 1)),
            ("Enviar al Fondo", lambda: self.setZValue(self.zValue() - 1)),
            ("Resetear Tamaño", lambda: self.setScale(1.0)),
            ("SEPARATOR", None),
            ("ELIMINAR", self.delete_self)
        ]

        for text, func in actions:
            if text == "SEPARATOR":
                menu.addSeparator()
            else:
                action = QAction(text, menu)
                action.triggered.connect(func)
                menu.addAction(action)

        menu.exec(event.screenPos())
        event.accept()

    def flip_image(self) -> None:
        """Aplica una transformación de matriz para invertir la imagen."""
        self.is_flipped = not self.is_flipped
        
        # Lógica matemática para pivotar sobre el centro
        center = self.boundingRect().center()
        transform = QTransform()
        transform.translate(center.x(), center.y())
        transform.scale(-1 if self.is_flipped else 1, 1)
        transform.translate(-center.x(), -center.y())
        
        self.setTransform(transform)

    def delete_self(self) -> None:
        if self.scene():
            self.scene().removeItem(self)

    def serialize(self) -> Dict[str, Any]:
        """Retorna el estado del objeto para guardado JSON."""
        return {
            "path": self.file_path,
            "x": self.pos().x(),
            "y": self.pos().y(),
            "scale": self.scale(),
            "z": self.zValue(),
            "flipped": self.is_flipped
        }


class CanvasView(QGraphicsView):
    """
    Vista optimizada para manejar el arrastre y soltado de archivos.
    """
    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setAcceptDrops(True)
        # Optimizaciones de viewport
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.MinimalViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("background: transparent; border: none;")
        
        # Lienzo virtual infinito
        self.setSceneRect(-10000, -10000, 20000, 20000)

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls(): event.accept()
        else: event.ignore()

    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasUrls(): event.accept()
        else: event.ignore()

    def dropEvent(self, event) -> None:
        """Maneja la entrada de archivos."""
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.exists(file_path):
                self._add_image_to_scene(file_path, event.position().toPoint())

    def _add_image_to_scene(self, path: str, pos: QPoint) -> None:
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            item = ImageItem(pixmap, path)
            # Mapeamos la coordenada de la vista a la coordenada de la escena
            scene_pos = self.mapToScene(pos)
            item.setPos(scene_pos)
            self.scene().addItem(item)

    def keyPressEvent(self, event) -> None:
        """Manejo centralizado de eliminación con teclado."""
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            for item in self.scene().selectedItems():
                if isinstance(item, ImageItem):
                    item.delete_self()
        else:
            super().keyPressEvent(event)

# =============================================================================
# COMPONENTES DE UI (BARRA TÍTULO Y BOTÓN FANTASMA)
# =============================================================================

class GhostControl(QWidget):
    """Botón flotante satelital para recuperar el control."""
    unlock_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(160, 50)
        
        layout = QVBoxLayout(self)
        btn = QPushButton("🔓 DESBLOQUEAR")
        btn.setStyleSheet("background-color: #d62828; color: white; border: 2px solid white; border-radius: 6px; font-weight: bold;")
        btn.clicked.connect(self.unlock_requested.emit)
        layout.addWidget(btn)

# --- NUEVO: CLASES PARA EL RADAR DE TAREAS (HUD) ---

class TaskPopup(QWidget):
    """El menú desplegable flotante que muestra las tareas."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        colors = Config.get_colors()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.container = QFrame()
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['bg_dark']};
                border: 1px solid {colors['accent']};
                border-radius: 6px;
            }}
            QLabel {{ color: {colors['text']}; font-family: 'Segoe UI'; }}
        """)
        
        self.inner_layout = QVBoxLayout(self.container)
        self.inner_layout.setSpacing(5)
        self.inner_layout.setContentsMargins(10, 10, 10, 10)
        
        # Cargar Tareas
        tasks = TaskManager.load_tasks()
        
        if not tasks:
            lbl = QLabel("✨ Todo limpio. Eres libre.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.inner_layout.addWidget(lbl)
        else:
            # Ordenar por urgencia
            priority_order = {"CRÍTICO": 0, "ALTA": 1, "MEDIA": 2, "BAJA": 3}
            sorted_tasks = sorted(tasks, key=lambda x: priority_order.get(x.get('urgency', 'BAJA'), 3))
            
            # Mostrar solo las top 5 para no saturar
            for task in sorted_tasks[:5]: 
                self.add_task_row(task)
            
            if len(sorted_tasks) > 5:
                more_lbl = QLabel(f"... y {len(sorted_tasks)-5} más")
                more_lbl.setStyleSheet("color: #666; font-size: 10px; margin-top: 5px;")
                more_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.inner_layout.addWidget(more_lbl)

        layout.addWidget(self.container)

    def add_task_row(self, task):
        """Crea una fila visual: [BarraColor] [Icono] [Texto]"""
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)
        
        # 1. Barra de Urgencia
        urgency = task.get("urgency", "BAJA")
        colors = Config.get_colors()
        urgency_colors = {"CRÍTICO": "#ff0000", "ALTA": "#ff9900", "MEDIA": "#ffff00", "BAJA": colors['accent']}
        color = urgency_colors.get(urgency, "#888")
        
        bar = QFrame()
        bar.setFixedSize(4, 25) # Barra vertical delgada
        bar.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
        
        # 2. Icono (Basado en categoría o genérico)
        cat = task.get("category", "General").lower()
        icon_text = "📝"
        if "comisión" in cat or "trabajo" in cat: icon_text = "💼"
        elif "urgente" in cat: icon_text = "🔥"
        elif "casa" in cat or "personal" in cat: icon_text = "🏠"
        
        icon = QLabel(icon_text)
        icon.setStyleSheet("font-size: 14px; border: none; background: transparent;")
        
        # 3. Texto Abreviado
        full_title = task.get("title", "Misión")
        abbr_title = (full_title[:18] + '..') if len(full_title) > 18 else full_title
        
        lbl_text = QLabel(abbr_title)
        lbl_text.setStyleSheet("font-size: 12px; font-weight: bold; border: none; background: transparent;")
        
        row_layout.addWidget(bar)
        row_layout.addWidget(icon)
        row_layout.addWidget(lbl_text)
        row_layout.addStretch()
        
        self.inner_layout.addWidget(row)

class TaskRadar(QPushButton):
    """El Ojo que todo lo ve (y te juzga por tus fechas de entrega)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(34, 34) # Un poco más grande para el borde
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.popup = None
        self.setText("👁️") 
        
        # Timer para actualizar el estado cada minuto (por si pasa medianoche)
        self.update_status()

    def update_status(self):
        """Consulta el color INTELIGENTE."""
        tasks = TaskManager.load_tasks()
        
        # CAMBIO AQUÍ: Usamos la nueva función "smart"
        smart_color = TaskManager.get_smart_priority_color(tasks)
        
        if smart_color:
            # Fondo sutil del mismo color
            bg_color = f"{smart_color}22"
            
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg_color};
                    border: 3px solid {smart_color}; 
                    border-radius: 17px;
                    color: {smart_color};
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {smart_color}44;
                    border: 3px solid {smart_color};
                }}
            """)
            
            # Tooltip dinámico
            if smart_color == "#ff0000": self.setToolTip("¡HAY TAREAS VENCIDAS!")
            elif smart_color == "#ff4500": self.setToolTip("¡TIENES ENTREGAS PARA HOY!")
            elif smart_color == "#ff0040": self.setToolTip("Prioridad CRÍTICA detectada")
            else: self.setToolTip(f"Estado de Prioridad: {smart_color}")
            
        else:
            self.setStyleSheet("""
                QPushButton { 
                    background-color: rgba(0,0,0,0.3);
                    border: 2px solid #444; 
                    border-radius: 17px; 
                    color: #666; 
                }
            """)
            self.setToolTip("Sin tareas pendientes")

    def enterEvent(self, event):
        if self.popup: self.popup.close()
        # Recargar datos frescos al pasar el mouse
        self.update_status() 
        
        self.popup = TaskPopup(self)
        global_pos = self.mapToGlobal(QPoint(0, self.height() + 5))
        self.popup.move(global_pos)
        self.popup.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.popup:
            self.popup.close()
            self.popup = None
        super().leaveEvent(event)

class TitleBar(QFrame):
    menu_requested = pyqtSignal()
    close_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(Config.HEADER_HEIGHT)
        colors = Config.get_colors()
        self.setStyleSheet(f"background-color: rgba(0, 0, 0, 0.6); border-bottom: 1px solid {colors['accent']};")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 5, 0)
        layout.setSpacing(10)
        
        self.radar = TaskRadar()
        
        self.title = QLabel("ANYA :: REFERENCE")
        self.title.setStyleSheet(f"color: {colors['accent']}; font-weight: bold; border: none; background: transparent;")
        
        self.btn_menu = QPushButton("MENU")
        self.btn_menu.setFixedSize(60, 20)
        self.btn_menu.clicked.connect(self.menu_requested.emit)
        
        self.btn_close = QPushButton("X")
        self.btn_close.setFixedSize(25, 25)
        self.btn_close.setStyleSheet(f"color: {colors['accent']}; border: none; font-size: 14px; background: transparent;")
        self.btn_close.clicked.connect(self.close_requested.emit)
        
        layout.addWidget(self.radar)
        layout.addWidget(self.title)
        layout.addStretch()
        layout.addWidget(self.btn_menu)
        layout.addWidget(self.btn_close)

    # Método para refrescar el radar si volvemos de guardar algo
    def refresh_radar(self):
        self.radar.update_status()

# =============================================================================
# VENTANA PRINCIPAL (LÓGICA DE SISTEMA)
# =============================================================================

class ReferenceFrame(QMainWindow):
    return_to_main = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Anya Reference Tool")
        self.resize(500, 600)
        
        # Configuración de ventana sin bordes
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setMouseTracking(True)

        # Estado
        self.is_ghost_mode = False
        self._drag_pos: Optional[QPoint] = None
        self._resize_edge: Optional[Qt.Edge] = None

        self._init_ui()
        self._init_system_tray()
        
        # Control Satelital
        self.ghost_ctrl = GhostControl()
        self.ghost_ctrl.unlock_requested.connect(self.toggle_ghost_mode)

    def _init_ui(self):
        """Construye la interfaz gráfica."""
        self.container = QWidget()
        self.container.setObjectName("Container")
        self.container.setMouseTracking(True) # Crítico para el redimensionamiento
        self.setCentralWidget(self.container)
        
        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Barra Título
        self.title_bar = TitleBar()
        self.title_bar.menu_requested.connect(self._go_home)
        self.title_bar.close_requested.connect(self.close)
        main_layout.addWidget(self.title_bar)

        # 2. Área de Contenido
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Botonera
        controls = QHBoxLayout()
        btn_load = QPushButton("CARGAR"); btn_load.clicked.connect(self.load_session)
        btn_save = QPushButton("GUARDAR"); btn_save.clicked.connect(self.save_session)
        btn_new_layer = QPushButton("＋ NUEVA CAPA")
        btn_new_layer.clicked.connect(self.spawn_new_layer)
        
        self.btn_ghost = QPushButton("MODO FANTASMA")
        self.btn_ghost.clicked.connect(self.toggle_ghost_mode)
        
        controls.addWidget(btn_save)
        controls.addWidget(btn_load)
        controls.addWidget(btn_new_layer)
        controls.addWidget(self.btn_ghost)
        
        # Scene & View
        self.scene = QGraphicsScene()
        self.view = CanvasView(self.scene)
        
        content_layout.addLayout(controls)
        content_layout.addWidget(self.view)
        
        main_layout.addWidget(content_widget)
        self.setStyleSheet(_build_stylesheet())


    def spawn_new_layer(self):
        """Crea una ventana de referencia totalmente independiente."""
        # Creamos una nueva instancia de la clase actual
        new_layer = ReferenceFrame()
        
        # Importante: Para que Windows no la cierre, la guardamos en la aplicación
        if not hasattr(QApplication.instance(), 'extra_layers'):
            QApplication.instance().extra_layers = []
        QApplication.instance().extra_layers.append(new_layer)
        
        # La movemos un poco para que no tape a la anterior
        new_layer.move(self.x() + 50, self.y() + 50)
        new_layer.show()
        
    def closeEvent(self, event):
        """Se ejecuta cuando se llama a self.close()"""
        
        # End the reference context
        from modules.mascot import MascotManager
        mascot = MascotManager.get_mascot()
        if mascot and mascot.current_context == "reference":
            mascot.end_context()
        
        # 1. Eliminar referencias en la lista global para permitir Garbage Collection
        app = QApplication.instance()
        if hasattr(app, 'extra_layers') and self in app.extra_layers:
            app.extra_layers.remove(self)
        
        # 2. Cerrar controles satelitales si están abiertos
        if hasattr(self, 'ghost_ctrl'):
            self.ghost_ctrl.close()
            
        event.accept()

    def _init_system_tray(self):
        """Inicializa el icono en la barra de tareas."""
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DesktopIcon))
        
        menu = QMenu()
        menu.addAction("Restaurar Ventana", self.toggle_ghost_mode)
        menu.addAction("Salir", QApplication.instance().quit)
        self.tray.setContextMenu(menu)
        self.tray.show()

    def _go_home(self):
        # End the reference context
        from modules.mascot import MascotManager
        mascot = MascotManager.get_mascot()
        if mascot and mascot.current_context == "reference":
            mascot.end_context()
        self.hide()
        self.return_to_main.emit()

    # --- LÓGICA DE MODO FANTASMA ---
    def toggle_ghost_mode(self):
        """Toggle single ghost mode - makes entire window transparent and click-through."""
        self.is_ghost_mode = not self.is_ghost_mode

        if self.is_ghost_mode:
            self.btn_ghost.setText("DESACTIVAR FANTASMA")
            
            # Apply full window transparency
            self.setWindowOpacity(0.3)
            
            # Hide and reshow with click-through flag
            self.hide()
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowTransparentForInput)
            self.show()
            
            # Show unlock control button
            geo = self.geometry()
            self.ghost_ctrl.move(geo.x() + (geo.width() // 2) - 80, geo.y() + 10)
            self.ghost_ctrl.show()
        else:
            # Reset to normal mode
            self.btn_ghost.setText("ACTIVAR MODO FANTASMA")
            
            self.setWindowOpacity(0.95)
            self.hide()
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowTransparentForInput)
            self.show()
            self.ghost_ctrl.hide()




    # --- LÓGICA DE REDIMENSIONAMIENTO (OPTIMIZADA) ---
    # Aquí eliminamos la "sopa de ifs" usando lógica de regiones
    
    def _get_resize_edges(self, pos: QPoint) -> Qt.Edge:
        """Determina qué borde se está tocando usando banderas binarias."""
        edges = Qt.Edge(0)
        rect = self.rect()
        m = Config.RESIZE_MARGIN
        
        if pos.x() < m: edges |= Qt.Edge.LeftEdge
        if pos.x() > rect.width() - m: edges |= Qt.Edge.RightEdge
        if pos.y() < m: edges |= Qt.Edge.TopEdge
        if pos.y() > rect.height() - m: edges |= Qt.Edge.BottomEdge
        
        return edges

    def _get_cursor_shape(self, edges: Qt.Edge) -> Qt.CursorShape:
        """Devuelve el cursor correcto basado en los bordes activos."""
        if edges == (Qt.Edge.LeftEdge | Qt.Edge.TopEdge): return Qt.CursorShape.SizeFDiagCursor
        if edges == (Qt.Edge.RightEdge | Qt.Edge.BottomEdge): return Qt.CursorShape.SizeFDiagCursor
        if edges == (Qt.Edge.RightEdge | Qt.Edge.TopEdge): return Qt.CursorShape.SizeBDiagCursor
        if edges == (Qt.Edge.LeftEdge | Qt.Edge.BottomEdge): return Qt.CursorShape.SizeBDiagCursor
        if edges & (Qt.Edge.LeftEdge | Qt.Edge.RightEdge): return Qt.CursorShape.SizeHorCursor
        if edges & (Qt.Edge.TopEdge | Qt.Edge.BottomEdge): return Qt.CursorShape.SizeVerCursor
        return Qt.CursorShape.ArrowCursor

    def mousePressEvent(self, event: QMouseEvent):
        if self.is_ghost_mode: return
        
        # 1. Verificar si estamos moviendo desde la barra título
        # (MapToGlobal y MapFromGlobal son costosos, usamos geometría local relativa)
        if self.childAt(event.pos()) == self.title_bar or self.title_bar.geometry().contains(event.pos()):
            self._drag_pos = event.globalPosition().toPoint()
            self._resize_edge = None
            return

        # 2. Verificar redimensionamiento
        edges = self._get_resize_edges(event.pos())
        if edges != Qt.Edge(0):
            self._resize_edge = edges
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_ghost_mode: return

        # A. Solo cambiar cursor si no estamos arrastrando
        if not self._drag_pos:
            edges = self._get_resize_edges(event.pos())
            self.setCursor(self._get_cursor_shape(edges))
            return

        # B. Ejecutar movimiento o resize
        delta = event.globalPosition().toPoint() - self._drag_pos
        geo = self.geometry()

        if self._resize_edge:
            # Lógica compacta de redimensionamiento
            if self._resize_edge & Qt.Edge.LeftEdge: geo.setLeft(geo.left() + delta.x())
            if self._resize_edge & Qt.Edge.RightEdge: geo.setRight(geo.right() + delta.x())
            if self._resize_edge & Qt.Edge.BottomEdge: geo.setBottom(geo.bottom() + delta.y())
            # Top edge es tricky con la barra de título, a veces se bloquea a propósito en UI moderna, 
            # pero si lo quieres:
            if self._resize_edge & Qt.Edge.TopEdge: geo.setTop(geo.top() + delta.y())

            if geo.width() > Config.MIN_WINDOW_SIZE and geo.height() > Config.MIN_WINDOW_SIZE:
                self.setGeometry(geo)
                self._drag_pos = event.globalPosition().toPoint()
        else:
            # Mover ventana
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        self._resize_edge = None
        if not self.is_ghost_mode:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    # --- PERSISTENCIA (GUARDAR / CARGAR) ---
    def save_session(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar Sesión", "", "Anya Files (*.json)")
        if not path: return
        
        data = {
            "window": {"x": self.x(), "y": self.y(), "w": self.width(), "h": self.height()},
            "items": [item.serialize() for item in self.scene.items() if isinstance(item, ImageItem)]
        }
        try:
            with open(path, 'w') as f: json.dump(data, f, indent=2)
        except Exception as e: print(f"Error guardando: {e}")

    def load_session(self):
        path, _ = QFileDialog.getOpenFileName(self, "Cargar Sesión", "", "Anya Files (*.json)")
        if not path: return
        
        try:
            with open(path, 'r') as f: data = json.load(f)
            
            # Restaurar ventana
            if "window" in data:
                w_data = data["window"]
                self.setGeometry(w_data["x"], w_data["y"], w_data["w"], w_data["h"])
            
            # Restaurar items
            self.scene.clear()
            for item_data in data.get("items", []):
                if os.path.exists(item_data["path"]):
                    img = ImageItem(QPixmap(item_data["path"]), item_data["path"])
                    img.setPos(item_data["x"], item_data["y"])
                    img.setScale(item_data["scale"])
                    img.setZValue(item_data["z"])
                    if item_data["flipped"]: img.flip_image()
                    self.scene.addItem(img)
        except Exception as e: print(f"Error cargando: {e}")