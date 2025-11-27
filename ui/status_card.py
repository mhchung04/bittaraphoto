from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
from .styles import Styles

class StatusCard(QFrame):
    """
    A unified status card widget to display Info, Success, and Error messages.
    Replaces ad-hoc QLabels and QFrames for status updates.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hide() # Initially hidden
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # Label
        self.label = QLabel()
        self.label.setWordWrap(True)
        layout.addWidget(self.label)
        
    def show_info(self, message):
        """Display an informational message (Blue)"""
        self.setStyleSheet(Styles.STATUS_CARD_INFO)
        self.label.setText(message)
        self.show()
        
    def show_success(self, message):
        """Display a success message (Green)"""
        self.setStyleSheet(Styles.STATUS_CARD_SUCCESS)
        self.label.setText(message)
        self.show()
        
    def show_error(self, message):
        """Display an error message (Red)"""
        self.setStyleSheet(Styles.STATUS_CARD_ERROR)
        self.label.setText(message)
        self.show()
        
    def clear(self):
        """Hide the card"""
        self.label.clear()
        self.hide()
