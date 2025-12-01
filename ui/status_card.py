from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
from .styles import Styles

class StatusCard(QFrame):
    """
    A unified status card widget to display Info, Success, and Error messages.
    Replaces ad-hoc QLabels and QFrames for status updates.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.hide() # Initially hidden -> Removed to keep layout stable
        self.setFixedHeight(80) # Fixed height for approx 3 lines
        
        # Default style to invisible/empty but taking space? 
        # Or just transparent background?
        # Let's keep it visible but empty style if needed, or just apply a default style.
        # For now, we'll just set the size.
        self.setStyleSheet("background-color: transparent;")
        
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
        """Reset the card content but keep it visible to maintain layout"""
        self.label.clear()
        self.setStyleSheet("background-color: transparent;")
        # self.hide() # Do not hide, to maintain fixed height layout
