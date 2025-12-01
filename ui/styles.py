"""
BittaraPhoto UI Styles
Centralized definition of colors, fonts, and stylesheets.
"""
import os
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPainterPath
from PyQt5.QtCore import Qt

class Colors:
    PRIMARY = "#2196F3"       # Ocean Blue
    PRIMARY_HOVER = "#1976D2" # Darker Blue
    SECONDARY = "#78909C"     # Slate Grey
    ACCENT = "#FFC107"        # Amber
    DESTRUCTIVE = "#EF5350"   # Soft Red
    BACKGROUND = "#F5F5F5"    # Off-White
    SURFACE = "#FFFFFF"       # White
    TEXT_PRIMARY = "#333333"  # Dark Grey
    TEXT_SECONDARY = "#757575"# Medium Grey
    TEXT_HINT = "#BDBDBD"     # Light Grey for hints
    BORDER = "#E0E0E0"        # Light Grey
    SUCCESS = "#4CAF50"       # Green

class Fonts:
    FAMILY = "Malgun Gothic"
    
    @staticmethod
    def title():
        return f"font-family: {Fonts.FAMILY}; font-size: 20px; font-weight: bold;"
    
    @staticmethod
    def heading():
        return f"font-family: {Fonts.FAMILY}; font-size: 14px; font-weight: bold;"
    
    @staticmethod
    def body():
        return f"font-family: {Fonts.FAMILY}; font-size: 12px;"
    
    @staticmethod
    def button():
        return f"font-family: {Fonts.FAMILY}; font-size: 12px; font-weight: bold;"

class Styles:
    # Main Window Background
    MAIN_WINDOW = f"""
        QMainWindow {{
            background-color: {Colors.BACKGROUND};
        }}
    """

    # Buttons
    BTN_PRIMARY = f"""
        QPushButton {{
            background-color: {Colors.PRIMARY};
            color: white;
            border-radius: 4px;
            padding: 6px 12px;
            font-family: "{Fonts.FAMILY}";
            font-size: 12px;
            font-weight: bold;
            border: none;
        }}
        QPushButton:hover {{
            background-color: {Colors.PRIMARY_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {Colors.PRIMARY};
        }}
    """

    BTN_SECONDARY = f"""
        QPushButton {{
            background-color: {Colors.SURFACE};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.BORDER};
            border-radius: 4px;
            padding: 6px 12px;
            font-family: "{Fonts.FAMILY}";
            font-size: 12px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #F0F0F0;
            border-color: #BDBDBD;
        }}
        QPushButton:disabled {{
            background-color: #F5F5F5;
            color: #BDBDBD;
            border: 1px solid #E0E0E0;
        }}
    """

    BTN_DESTRUCTIVE = f"""
        QPushButton {{
            background-color: {Colors.DESTRUCTIVE};
            color: white;
            border-radius: 4px;
            padding: 6px 12px;
            font-family: "{Fonts.FAMILY}";
            font-size: 12px;
            font-weight: bold;
            border: none;
        }}
        QPushButton:hover {{
            background-color: #D32F2F;
        }}
    """
    
    BTN_ACCENT = f"""
        QPushButton {{
            background-color: {Colors.ACCENT};
            color: white;
            border-radius: 4px;
            padding: 6px 12px;
            font-family: "{Fonts.FAMILY}";
            font-size: 12px;
            font-weight: bold;
            border: none;
        }}
        QPushButton:hover {{
            background-color: #FFA000;
        }}
    """

    BTN_ICON = f"""
        QPushButton {{
            background-color: transparent;
            border: none;
            border-radius: 4px;
        }}
        QPushButton:hover {{
            background-color: rgba(0, 0, 0, 0.05);
        }}
    """
    
    BTN_SUCCESS = f"""
        QPushButton {{
            background-color: #4CAF50;
            color: white;
            border-radius: 4px;
            padding: 6px 12px;
            font-family: "{Fonts.FAMILY}";
            font-size: 14px;
            font-weight: bold;
            border: none;
        }}
        QPushButton:hover {{
            background-color: #45a049;
        }}
        QPushButton:disabled {{
            background-color: #A5D6A7;
            color: #E8F5E9;
        }}
    """

    BTN_TOGGLE = f"""
        QPushButton {{
            background-color: {Colors.SURFACE};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.BORDER};
            border-radius: 4px;
            padding: 8px 16px;
            font-family: "{Fonts.FAMILY}";
            font-size: 12px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #F5F5F5;
        }}
        QPushButton:checked {{
            background-color: {Colors.PRIMARY};
            color: white;
            border: 1px solid {Colors.PRIMARY};
        }}
    """

    # Inputs
    INPUT = f"""
        QLineEdit, QSpinBox {{
            border: 1px solid {Colors.BORDER};
            border-radius: 4px;
            padding: 4px 8px;
            background-color: {Colors.SURFACE};
            font-family: "{Fonts.FAMILY}";
            font-size: 12px;
            color: {Colors.TEXT_PRIMARY};
        }}
        QComboBox {{
            border: 1px solid {Colors.BORDER};
            border-radius: 4px;
            padding: 4px 8px;
            background-color: {Colors.SURFACE};
            font-family: "{Fonts.FAMILY}";
            font-size: 12px;
            color: {Colors.TEXT_PRIMARY};
            min-height: 20px;
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 0px;
            border-top-right-radius: 3px;
            border-bottom-right-radius: 3px;
        }}
        QComboBox::down-arrow {{
            image: url(arrow_down.png);
            width: 12px;
            height: 12px;
            margin-right: 6px;
        }}
        QComboBox QAbstractItemView {{
            border: 1px solid {Colors.BORDER};
            selection-background-color: #E3F2FD;
            selection-color: {Colors.TEXT_PRIMARY};
            background-color: {Colors.SURFACE};
            outline: none;
        }}
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
            border: 2px solid {Colors.PRIMARY};
        }}
        QLineEdit:disabled, QSpinBox:disabled, QComboBox:disabled {{
            background-color: #F5F5F5;
            color: {Colors.TEXT_SECONDARY};
            border: 1px solid {Colors.BORDER};
            border-radius: 4px;
            padding: 4px 8px;
            font-family: "{Fonts.FAMILY}";
            font-size: 12px;
        }}
        QLineEdit[readOnly="true"] {{
            background-color: #F5F5F5;
            color: {Colors.TEXT_SECONDARY};
            border: 1px solid {Colors.BORDER};
            border-radius: 4px;
            padding: 4px 8px;
            font-family: "{Fonts.FAMILY}";
            font-size: 12px;
        }}
    """

    # Status Labels
    STATUS_LABEL = f"""
        QLabel {{
            font-family: "{Fonts.FAMILY}";
            font-size: 12px;
            padding: 4px;
        }}
    """
    
    STATUS_SUCCESS = "color: #2E7D32; font-weight: bold;" # Green
    STATUS_ERROR = "color: #C62828; font-weight: bold;"   # Red
    STATUS_INFO = f"color: {Colors.PRIMARY};"             # Blue
    
    # Status Cards (Unified UI)
    STATUS_CARD_INFO = f"""
        QFrame {{
            background-color: #E3F2FD; /* Light Blue */
            border: 1px solid #90CAF9;
            border-radius: 6px;
        }}
        QLabel {{
            color: #0D47A1; /* Dark Blue Text */
            font-family: "{Fonts.FAMILY}";
            font-size: 12px;
            border: none;
            background: transparent;
        }}
    """

    STATUS_CARD_SUCCESS = f"""
        QFrame {{
            background-color: #E8F5E9; /* Light Green */
            border: 1px solid #A5D6A7;
            border-radius: 6px;
        }}
        QLabel {{
            color: #1B5E20; /* Dark Green Text */
            font-family: "{Fonts.FAMILY}";
            font-size: 12px;
            border: none;
            background: transparent;
        }}
    """

    STATUS_CARD_ERROR = f"""
        QFrame {{
            background-color: #FFEBEE; /* Light Red */
            border: 1px solid #EF9A9A;
            border-radius: 6px;
        }}
        QLabel {{
            color: #B71C1C; /* Dark Red Text */
            font-family: "{Fonts.FAMILY}";
            font-size: 12px;
            border: none;
            background: transparent;
        }}
    """
    
    # Processed Frame
    PROCESSED_FRAME = f"""
        QFrame {{
            background-color: {Colors.SURFACE};
            border: 1px solid {Colors.BORDER};
            border-radius: 8px;
        }}
    """
    
    LABEL_TITLE = f"font-family: '{Fonts.FAMILY}'; font-size: 12px; font-weight: bold; color: {Colors.TEXT_PRIMARY};"
    LABEL_SUBTITLE = f"font-family: '{Fonts.FAMILY}'; font-size: 11px; color: {Colors.TEXT_SECONDARY};"

    # GroupBox / Cards
    GROUP_BOX = f"""
        QGroupBox {{
            background-color: {Colors.SURFACE};
            border: 1px solid {Colors.BORDER};
            border-radius: 8px;
            margin-top: 1.2em;
            font-family: "{Fonts.FAMILY}";
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px;
            color: {Colors.TEXT_PRIMARY};
            font-weight: bold;
            font-size: 12px;
        }}
    """
    
    # List Widget
    LIST_WIDGET = f"""
        QListWidget {{
            background-color: {Colors.SURFACE};
            border: 1px solid {Colors.BORDER};
            border-radius: 4px;
            outline: none;
        }}
        QListWidget::item {{
            border-radius: 4px;
            padding: 5px;
        }}
        QListWidget::item:selected {{
            background-color: #E3F2FD;
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.PRIMARY};
        }}
        QListWidget::item:hover {{
            background-color: #F5F5F5;
        }}
    """
    
    # Scroll Area
    SCROLL_AREA = f"""
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        QScrollBar:vertical {{
            border: none;
            background: #F5F5F5;
            width: 10px;
            margin: 0px 0px 0px 0px;
        }}
        QScrollBar::handle:vertical {{
            background: #BDBDBD;
            min-height: 20px;
            border-radius: 5px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
    """
    
    # Tab Widget
    TAB_WIDGET = f"""
        QTabWidget::pane {{
            border: 1px solid {Colors.BORDER};
            border-radius: 4px;
            background-color: {Colors.SURFACE};
        }}
        QTabBar::tab {{
            background-color: #E0E0E0;
            color: {Colors.TEXT_SECONDARY};
            border: 1px solid {Colors.BORDER};
            border-bottom-color: {Colors.BORDER};
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 8px 16px;
            margin-right: 2px;
            font-family: "{Fonts.FAMILY}";
            font-weight: bold;
        }}
        QTabBar::tab:selected {{
            background-color: {Colors.SURFACE};
            color: {Colors.PRIMARY};
            border-bottom-color: {Colors.SURFACE};
        }}
        QTabBar::tab:hover {{
            background-color: #F5F5F5;
        }}
    """

    @staticmethod
    def init_resources():
        """필요한 리소스 파일 생성 (아이콘 등)"""
        if not os.path.exists("arrow_down.png"):
            try:
                pixmap = QPixmap(12, 12)
                pixmap.fill(Qt.transparent)
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.Antialiasing)
                
                # Draw triangle pointing down
                path = QPainterPath()
                # Center is 6,6. Size approx 8x5
                # Top-Left: 2, 4
                # Top-Right: 10, 4
                # Bottom: 6, 9
                path.moveTo(3, 4)
                path.lineTo(9, 4)
                path.lineTo(6, 8)
                path.closeSubpath()
                
                painter.fillPath(path, QColor(Colors.TEXT_SECONDARY))
                painter.end()
                pixmap.save("arrow_down.png")
                print("Created arrow_down.png")
            except Exception as e:
                print(f"Failed to create resource: {e}")
