class ReferenceFrame(QMainWindow):
    return_to_main = pyqtSignal()

    def __init__(self, title="Nuevo Marco"):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(400, 500)
        
        # Flags iniciales: Siempre encima, sin bordes de Windows
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.is_ghost_mode = False
        self._init_ui()
        
        # Control satelital propio para este marco
        self.ghost_ctrl = GhostControl()
        self.ghost_ctrl.unlock_requested.connect(self.toggle_ghost_mode)

    def _init_ui(self):
        self.container = QWidget()
        self.container.setObjectName("Container")
        self.setCentralWidget(self.container)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)

        # Barra de título con botón para añadir más marcos
        self.title_bar = TitleBar()
        self.btn_new_frame = QPushButton("+")
        self.btn_new_frame.setFixedSize(25, 25)
        self.btn_new_frame.clicked.connect(self.spawn_new_frame)
        self.title_bar.layout().insertWidget(2, self.btn_new_frame) # Insertar junto al título
        
        layout.addWidget(self.title_bar)

        # Canvas independiente para este marco
        self.scene = QGraphicsScene()
        self.view = CanvasView(self.scene)
        
        # Botonera de control
        btns = QHBoxLayout()
        self.btn_ghost = QPushButton("MODO GHOST")
        self.btn_ghost.clicked.connect(self.toggle_ghost_mode)
        btns.addWidget(self.btn_ghost)
        
        layout.addLayout(btns)
        layout.addWidget(self.view)
        self.setStyleSheet(_build_stylesheet())

    def spawn_new_frame(self):
        """Crea una instancia hermana totalmente independiente."""
        new_frame = ReferenceFrame(title="Capa Extra")
        new_frame.show()
        # Guardamos referencia para que no la destruya el recolector de basura
        if not hasattr(QApplication.instance(), 'frames'):
            QApplication.instance().frames = []
        QApplication.instance().frames.append(new_frame)

    def toggle_ghost_mode(self):
        """Aplica el modo fantasma SOLO a esta ventana."""
        self.is_ghost_mode = not self.is_ghost_mode
        
        if self.is_ghost_mode:
            self.setWindowOpacity(0.3)
            self.hide()
            # Esta bandera hace que Windows ignore los clics en ESTA ventana
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowTransparentForInput)
            self.show()
            
            geo = self.geometry()
            self.ghost_ctrl.move(geo.x() + (geo.width() // 2) - 80, geo.y() + 10)
            self.ghost_ctrl.show()
        else:
            self.setWindowOpacity(0.95)
            self.hide()
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowTransparentForInput)
            self.show()
            self.ghost_ctrl.hide()

    # (Debes incluir aquí también los métodos mousePressEvent, mouseMoveEvent 
    # y mouseReleaseEvent que ya tenías para poder mover cada marco de forma independiente)