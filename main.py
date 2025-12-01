"""
사진 선택 및 인쇄 프로그램 - 메인 엔트리 포인트
"""

import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MultiWindow
from ui.styles import Styles


def main():
    """메인 실행 함수"""
    app = QApplication(sys.argv)
    
    # 리소스 초기화
    Styles.init_resources()
    
    # 메인 윈도우 실행 (기존 MultiWindow 사용)
    window = MultiWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()