from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from .styles import Styles, Fonts, Colors

class MessageBox(QDialog):
    """
    Custom Styled Message Box to replace native QMessageBox.
    Provides static methods: question, information, warning, critical.
    """
    
    # Return codes
    Yes = 1
    No = 0
    Ok = 1
    Cancel = 0

    def __init__(self, title, text, type="info", buttons=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setStyleSheet(Styles.MAIN_WINDOW)
        self.setMinimumWidth(350)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Content Layout (Icon + Text)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        # Icon (Text-based for now, can be replaced with QIcon)
        icon_label = QLabel()
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 24px; border-radius: 20px;")
        
        if type == "question":
            icon_label.setText("❓")
            icon_label.setStyleSheet(icon_label.styleSheet() + "background-color: #E3F2FD; color: #1976D2;")
        elif type == "warning":
            icon_label.setText("⚠")
            icon_label.setStyleSheet(icon_label.styleSheet() + "background-color: #FFF3E0; color: #F57C00;")
        elif type == "critical":
            icon_label.setText("❌")
            icon_label.setStyleSheet(icon_label.styleSheet() + "background-color: #FFEBEE; color: #D32F2F;")
        else: # info
            icon_label.setText("ℹ")
            icon_label.setStyleSheet(icon_label.styleSheet() + "background-color: #E8F5E9; color: #388E3C;")
            
        content_layout.addWidget(icon_label)
        
        # Message Text
        text_label = QLabel(text)
        text_label.setWordWrap(True)
        text_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-family: '{Fonts.FAMILY}'; font-size: 13px;")
        content_layout.addWidget(text_label, 1) # Stretch
        
        layout.addLayout(content_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.setSpacing(10)
        
        self.result_code = 0
        
        if buttons == "yes_no":
            self.yes_btn = QPushButton("예")
            self.yes_btn.setStyleSheet(Styles.BTN_PRIMARY)
            self.yes_btn.setFixedWidth(80)
            self.yes_btn.clicked.connect(self.on_yes)
            
            self.no_btn = QPushButton("아니오")
            self.no_btn.setStyleSheet(Styles.BTN_SECONDARY)
            self.no_btn.setFixedWidth(80)
            self.no_btn.clicked.connect(self.on_no)
            
            btn_layout.addWidget(self.yes_btn)
            btn_layout.addWidget(self.no_btn)
            
        elif buttons == "ok_cancel":
            self.ok_btn = QPushButton("확인")
            self.ok_btn.setStyleSheet(Styles.BTN_PRIMARY)
            self.ok_btn.setFixedWidth(80)
            self.ok_btn.clicked.connect(self.on_ok)
            
            self.cancel_btn = QPushButton("취소")
            self.cancel_btn.setStyleSheet(Styles.BTN_SECONDARY)
            self.cancel_btn.setFixedWidth(80)
            self.cancel_btn.clicked.connect(self.on_cancel)
            
            btn_layout.addWidget(self.ok_btn)
            btn_layout.addWidget(self.cancel_btn)
            
        else: # ok only
            self.ok_btn = QPushButton("확인")
            self.ok_btn.setStyleSheet(Styles.BTN_PRIMARY)
            self.ok_btn.setFixedWidth(80)
            self.ok_btn.clicked.connect(self.on_ok)
            
            btn_layout.addWidget(self.ok_btn)
            
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def on_yes(self):
        self.result_code = MessageBox.Yes
        self.accept()

    def on_no(self):
        self.result_code = MessageBox.No
        self.reject()
        
    def on_ok(self):
        self.result_code = MessageBox.Ok
        self.accept()
        
    def on_cancel(self):
        self.result_code = MessageBox.Cancel
        self.reject()

    @staticmethod
    def question(parent, title, text, buttons=None, defaultButton=None):
        # buttons argument is kept for compatibility but ignored in simple implementation
        # We assume Yes/No for question
        dlg = MessageBox(title, text, type="question", buttons="yes_no", parent=parent)
        if dlg.exec_() == QDialog.Accepted:
            return MessageBox.Yes
        return MessageBox.No

    @staticmethod
    def information(parent, title, text):
        dlg = MessageBox(title, text, type="info", buttons="ok", parent=parent)
        dlg.exec_()

    @staticmethod
    def warning(parent, title, text):
        dlg = MessageBox(title, text, type="warning", buttons="ok", parent=parent)
        dlg.exec_()

    @staticmethod
    def critical(parent, title, text):
        dlg = MessageBox(title, text, type="critical", buttons="ok", parent=parent)
        dlg.exec_()
