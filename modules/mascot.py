import os
import random
import math
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect, QApplication
from PyQt6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QGuiApplication, QTransform
from modules.schedule_tool import TaskManager

class RafayelMascot(QWidget):
    def __init__(self):
        super().__init__()
        
        # --- CONFIGURACIÓN DE VENTANA ---
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool 
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Tamaño
        self.setFixedSize(200, 300)

        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # --- BURBUJA DE DIÁLOGO ---
        self.bubble = QLabel("")
        self.bubble.setWordWrap(True)
        self.bubble.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bubble.setStyleSheet("""
            QLabel {
                background-color: white; color: #333; border-radius: 10px;
                padding: 8px; font-family: 'Segoe UI'; font-size: 11px;
                border: 2px solid #7B68EE;
            }
        """)
        self.bubble.hide() 
        
        # --- IMAGEN ---
        self.image_lbl = QLabel()
        self.image_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Efectos de Transición (Opacidad)
        self.opacity_effect = QGraphicsOpacityEffect(self.image_lbl)
        self.image_lbl.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)
        
        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_anim.setDuration(550)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.layout.addWidget(self.bubble)
        self.layout.addWidget(self.image_lbl)
        
        # --- LÓGICA INTERNA ---
        self.is_reacting = False
        self.is_dragging = False
        self.drag_pos = QPoint()
        self.facing_right = True 
        
        self.image_paths = {
            "idle": "modules/assets/rafayel_idle.png",
            "walk": "modules/assets/rafayel_walk.png",
            "happy": "modules/assets/rafayel_happy.png",
            "angry": "modules/assets/rafayel_angry.png",
            "worry": "modules/assets/rafayel_worry.png",
            "sleep": "modules/assets/rafayel_sleep.png",
            "art":   "modules/assets/rafayel_art.png",
            "love":  "modules/assets/rafayel_love.png"
        }

        # --- BANCO DE DIÁLOGOS (300 INTERACCIONES) ---
        self.dialogues = {
            "idle": ["¿Y ahora qué?", "Observo... juzgo...", "Mmh.", "El mar me llama."],
            "walk": ["Estirando las piernas.", "Buscando un mejor ángulo.", "Caminando por aquí."],
            "sleep": ["Zzz...", "No hagas ruido.", "Soñando con Lemuria."],
            "angry": ["¡No me ignores!", "Tsk.", "Mi paciencia se agota."],
            
            # 1. TAREAS PENDIENTES (Nagging/Persuasivo)
            "pending_tasks": [
                f"¿{i} tareas pendientes? Mi lienzo tiene más orden que tu vida." for i in range(1, 20)
            ] + [
                "Ese color rojo en la agenda me da dolor de cabeza.",
                "¿Procrastinando? El arte no espera, y mis ganas de cenar tampoco.",
                "Si no terminas pronto, el mar se habrá retirado para cuando acabes.",
                "Tic-tac... el sonido de tu pereza es más fuerte que las olas.",
                "¿Otra tarea? A este paso seremos estatuas de sal antes de salir.",
                "Esa lista es... poco estética. Deshazte de ella trabajando.",
                "Me aburro de mirar esa notificación de urgencia. ¡Haz algo!",
                "Incluso mis bocetos fallidos tienen más progreso que tú hoy.",
                "¿Necesitas que te pinte un mapa para llegar al botón de 'Terminar'?",
                "¿Y si terminas eso y luego vamos a Lemuria? Oferta limitada.",
                "Esa tarea te mira con odio. Yo también si no la haces.",
                "¿Por qué el desorden te persigue? Termina esos pendientes.",
                "Un artista necesita paz, y tus tareas pendientes hacen mucho ruido.",
                "¿Vas a dejar que los plazos te devoren como un Kraken?",
                "Si yo puedo pintar obras maestras, tú puedes cerrar ese ticket.",
                "¡Trabaja! Quiero ver esa lista vacía para antes del atardecer.",
                "¿Es que acaso disfrutas ver el mundo arder en notificaciones?",
                "No me hables de inspiración si no puedes terminar lo básico.",
                "Mi pincel se seca esperando a que te dignes a ser productivo.",
                "¿Ves eso? Es el fantasma de las tareas que no hiciste ayer."
                # ... puedes seguir añadiendo variaciones hasta completar las 100
            ],

            # 2. USANDO REFERENCIAS (Modo Artista/Ego)
            "references": [
                "¿Buscando inspiración? Podrías simplemente mirarme a mí.",
                "Esa imagen tiene una paleta interesante... pero le falta alma.",
                "Ah, composición. Recuerda: la luz lo es todo.",
                "¿Referencias? Espero que busques algo a la altura de mis estándares.",
                "No te pierdas en los detalles, captura la esencia del momento.",
                "Esa referencia es aceptable, pero mis pinturas tienen más profundidad.",
                "¿Analizas la técnica o solo pierdes el tiempo mirando fotos?",
                "El arte es un lenguaje. ¿Qué intentas decir con esta búsqueda?",
                "Si necesitas ayuda con el color, mi tarifa es una cena de mariscos.",
                "Inspiración... es un pez escurridizo. Ten una buena red.",
                "No copies, reinterpreta. Aunque dudo que superes el original.",
                "Esa luz de mediodía es difícil de capturar. Suerte.",
                "¿Referencias de anatomía? Yo soy la perfección personificada.",
                "Veo que tienes buen gusto para las imágenes. Casi como el mío.",
                "¿Y si pintamos eso luego? Pero con más... estilo.",
                "La estética de esa foto es cuestionable. Sigue buscando.",
                "A veces la mejor referencia es el silencio del océano.",
                "¿Estás buscando texturas? Mi ropa es de seda pura, por si preguntas.",
                "Cuidado con el exceso de saturación. Es de novatos.",
                "Mira esa sombra. Eso es lo que separa a un artista de un aficionado."
                # ... puedes seguir añadiendo variaciones hasta completar las 100
            ],

            # 3. COMPLETAR TAREA (Elogio/Alivio)
            "task_completed": [
                "¡Por fin! Sentí como si hubiera pasado una eternidad.",
                "Buen trabajo. Ahora tengo tu atención total de nuevo.",
                "Una menos. A este paso cenaremos fuera hoy.",
                "Admito que tienes talento para terminar cosas... cuando quieres.",
                "¡Eso es! El lienzo de tu día se ve mucho más limpio ahora.",
                "¿Ves? No fue tan difícil. Hasta un pez fuera del agua lo lograba.",
                "Excelente. Te has ganado cinco minutos de mi compañía sin quejas.",
                "Un peso menos. Mi inspiración fluye mejor si no estás estresado.",
                "Mmh, no estuvo mal. Pero no te confíes, aún queda camino.",
                "¡Victoria! Deberíamos pintar un mural para conmemorar esto.",
                "Has logrado lo imposible. Estoy... casi impresionado.",
                "Esa tarea se fue al fondo del mar. Que no vuelva.",
                "Siento el alivio desde aquí. ¿Vamos por mariscos ahora?",
                "Bien hecho. Tu productividad es casi tan alta como mi ego.",
                "Limpiaste eso con estilo. Me gusta.",
                "Al fin podemos respirar. El ambiente estaba muy cargado.",
                "Eres más eficiente de lo que pareces. Sigue así.",
                "¿Ya terminaste? Pensé que te tomaría otra década.",
                "¡Perfecto! El orden ha vuelto al universo. O al menos a esta app.",
                "Tarea tachada. Es tan satisfactorio como un lienzo en blanco."
                # ... puedes seguir añadiendo variaciones hasta completar las 100
            ]
        }

        self.current_state = ""
        self.set_state("idle")
        
        # --- TIMERS ---
        self.behavior_timer = QTimer(self)
        self.behavior_timer.timeout.connect(self.decide_behavior)
        self.behavior_timer.start(6000) 

        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.check_tasks_background)
        self.status_timer.start(30000)
        
        self.top_timer = QTimer(self)
        self.top_timer.timeout.connect(self.force_on_top)
        self.top_timer.start(2000)

        # Posición Inicial
        screen = QGuiApplication.primaryScreen().geometry()
        self.move(screen.width() - 250, screen.height() - 350)

    # --- MÉTODOS DE INTERACCIÓN ---

    def notify_task_completed(self):
        """Reacción inmediata sin interrumpir drásticamente"""
        # Detenemos temporalmente el movimiento aleatorio para que hable
        self.behavior_timer.stop()
        if hasattr(self, 'move_anim') and self.move_anim.state() == QPropertyAnimation.State.Running:
            self.move_anim.pause() 
            
        self.set_state("happy")
        frases = self.dialogues.get("task_completed", ["¡Hecho!"])
        self.say(random.choice(frases))
        
        # Reiniciar el timer de comportamiento para que no cambie de estado justo después de hablar
        QTimer.singleShot(5000, self.behavior_timer.start)

    def react_to_context(self, context_name):
        self.is_reacting = True 
        self.behavior_timer.stop()
    
    # Cancelar cualquier ocultación programada previa si es posible
    # o simplemente asegurar que el nuevo mensaje sea persistente
        if context_name == "schedule":
            self.set_state("worry")
        # Usamos autohide=False para que el texto se quede mientras escribes
            self.say("¿Tantas tareas? Ánimo, estaré vigilando...", autohide=False)
        elif context_name == "reference":
            self.set_state("art")
            self.say("Busca algo digno de mi pincel.", autohide=False)


    def _end_reaction(self):
        self.is_reacting = False
        self.behavior_timer.start(6000)

    def force_on_top(self):
        self.raise_()
        self.activateWindow()

    def check_tasks_background(self):
        try:
            tasks = TaskManager.load_tasks()
            priority = TaskManager.get_smart_priority_color(tasks)
            if priority == "#ff0000": 
                self.set_state("angry")
                self.say(random.choice(self.dialogues["pending_tasks"]))
        except Exception as e:
            print(f"Error checking tasks: {e}")

    def decide_behavior(self):

        if self.is_reacting: 
            return
        
        if self.current_state == "sleep" and random.random() > 0.2:
            return 
        actions = ["walk", "walk", "walk", "idle", "idle", "sleep", "talk"]
        choice = random.choice(actions)
        if choice == "walk":
            self.start_smart_walk()
        elif choice == "talk":
            self.say_random_line()
        else:
            self.set_state(choice)

    def start_smart_walk(self):
        try:
            screen = QGuiApplication.primaryScreen().availableGeometry()
            current_pos = self.pos()
            max_x, max_y = screen.width() - self.width(), screen.height() - self.height()
            min_y = int(screen.height() / 2)
            target_x = random.randint(0, max_x if max_x > 0 else 100)
            target_y = random.randint(min_y if min_y < max_y else 0, max_y if max_y > 0 else 100)
            self.facing_right = target_x > current_pos.x()
            self.set_state("walk", force_update=True)
            dist = math.sqrt((target_x - current_pos.x())**2 + (target_y - current_pos.y())**2)
            duration = int(dist / 0.15)
            self.move_anim = QPropertyAnimation(self, b"pos")
            self.move_anim.setDuration(max(1000, duration))
            self.move_anim.setStartValue(current_pos)
            self.move_anim.setEndValue(QPoint(target_x, target_y))
            self.move_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
            self.move_anim.finished.connect(lambda: self.set_state("idle"))
            self.move_anim.start()
        except Exception as e:
            self.set_state("idle")

    def set_state(self, state, force_update=False):
        if state == self.current_state and not force_update: return
        self.fade_anim.stop()
        try: self.fade_anim.finished.disconnect() 
        except: pass
        self.fade_anim.setStartValue(self.opacity_effect.opacity())
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.finished.connect(lambda: self._swap_image(state))
        self.fade_anim.start()

    def _swap_image(self, state):
        try:
            self.current_state = state
            path = self.image_paths.get(state, self.image_paths["idle"])
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if self.facing_right:
                    pixmap = pixmap.transformed(QTransform().scale(-1, 1))
                self.image_lbl.setPixmap(pixmap.scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            if state != "talk": self.bubble.hide()
            self.fade_anim.setStartValue(0.0)
            self.fade_anim.setEndValue(1.0)
            try: self.fade_anim.finished.disconnect()
            except: pass
            self.fade_anim.start()
        except: pass

    def say_random_line(self):
        cat = self.current_state if self.current_state in self.dialogues else "idle"
        self.say(random.choice(self.dialogues[cat]))

    # En An/modules/mascot.py

    def say(self, text, autohide=True):
        self.bubble.setText(text)
        self.bubble.show()
        self.bubble.raise_()
    
    # Solo creamos el timer si autohide es True
        if autohide:
            QTimer.singleShot(5000, self.bubble.hide)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging, self.drag_pos = True, event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            if self.current_state == "walk":
                if hasattr(self, 'move_anim'): self.move_anim.stop()
                self.set_state("angry")
                self.say("¡Iba hacia allí!")
            else: self.say("¿Mmh?")
            self.raise_()

    def mouseMoveEvent(self, event):
        if self.is_dragging: self.move(event.globalPosition().toPoint() - self.drag_pos)

    def mouseReleaseEvent(self, event):
        self.is_dragging = False
        self.setCursor(Qt.CursorShape.ArrowCursor)