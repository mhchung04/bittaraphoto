from PyQt5.QtWidgets import QLabel, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from .styles import Colors, Fonts

class ToastMessage(QLabel):
    def __init__(self, parent, text, type="info", duration=3000):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        # Determine style based on type
        # Using RGBA for transparency (alpha ~ 0.85 -> 215)
        bg_color = "rgba(51, 51, 51, 215)" # Default dark
        text_color = "white"
        
        if type == "success":
            bg_color = "rgba(76, 175, 80, 215)" # Green
        elif type == "error":
            bg_color = "rgba(239, 83, 80, 215)" # Red
        elif type == "info":
            bg_color = "rgba(33, 150, 243, 215)" # Blue
        elif type == "warning":
            bg_color = "rgba(255, 193, 7, 215)" # Amber
            
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                padding: 8px 16px;
                border-radius: 16px;
                font-family: '{Fonts.FAMILY}';
                font-size: 13px;
                font-weight: bold;
            }}
        """)
        self.setText(text)
        self.setAlignment(Qt.AlignCenter)
        self.adjustSize()
        
        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fade_out)
        self.timer.start(duration)
        
        # Animation
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()
        
    def fade_out(self):
        self.anim.setDirection(QPropertyAnimation.Backward)
        self.anim.setEndValue(0)
        self.anim.finished.connect(self.close)
        self.anim.start()

    @staticmethod
    def show_toast(parent, text, type="info", duration=3000, y_offset=100, anchor_widget=None, center_x=False, position="bottom"):
        """
        Show a toast message.
        :param parent: Parent widget
        :param text: Message text
        :param type: 'info', 'success', 'error', 'warning'
        :param duration: Duration in ms
        :param y_offset: Offset from bottom if no anchor
        :param anchor_widget: Widget to anchor the toast to (e.g. input field)
        :param center_x: If True, center horizontally in parent regardless of anchor
        :param position: 'top' or 'bottom' relative to anchor (default: 'bottom')
        """
        # Remove existing toasts to prevent stacking/spam
        for child in parent.children():
            if isinstance(child, ToastMessage):
                child.close()
                
        toast = ToastMessage(parent, text, type, duration)
        
        if anchor_widget:
            # Position relative to anchor widget
            global_pos = anchor_widget.mapTo(parent, QPoint(0, 0))
            
            if center_x:
                x = (parent.width() - toast.width()) // 2
            else:
                x = global_pos.x() + (anchor_widget.width() - toast.width()) // 2
            
            if position == "top":
                y = global_pos.y() - toast.height() - 10 # 10px padding above
            else:
                y = global_pos.y() + anchor_widget.height() + 10 # 10px padding below
            
            # Ensure it doesn't go off screen (basic check)
            if x < 10: x = 10
            if x + toast.width() > parent.width() - 10: x = parent.width() - toast.width() - 10
            
            toast.move(x, y)
        else:
            # Position at bottom center
            parent_rect = parent.rect()
            x = (parent_rect.width() - toast.width()) // 2
            y = parent_rect.height() - y_offset
            toast.move(x, y)
            
        toast.show()
