import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MultiWindow
from ui.styles import Styles

def run_multi_mode():
    """Multi 모드 실행 함수"""
    app = QApplication(sys.argv)
    
    # 리소스 초기화
    Styles.init_resources()
    
    window = MultiWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(run_multi_mode())