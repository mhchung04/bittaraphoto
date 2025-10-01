"""
사진 선택 및 인쇄 프로그램 - Multi Mode
리팩토링된 버전: UI 컴포넌트를 ui 패키지로 분리
"""

import sys
from PyQt5.QtWidgets import QApplication

# UI 컴포넌트 import (새로운 모듈에서)
try:
    from ui import MultiWindow
except ImportError:
    # 이전 버전과의 호환성을 위해 기존 클래스 사용
    print("[WARNING] UI 모듈을 찾을 수 없습니다. 기존 클래스를 사용합니다.")
    # 기존 클래스 로드를 위한 fallback (여기서는 구현하지 않음)
    raise


def run_multi_mode():
    """Multi 모드 실행 함수"""
    app = QApplication(sys.argv)
    window = MultiWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(run_multi_mode())
