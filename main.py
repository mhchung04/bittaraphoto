"""
사진 선택 및 인쇄 프로그램 - 메인 런처
Multi Mode와 Single Mode를 선택할 수 있는 런처입니다.
"""

import sys
import os


def main():
    """메인 런처 함수"""
    print("=== 사진 선택 및 인쇄 프로그램 ===")
    print("현재 Multi Mode (4개 이미지)만 지원됩니다.")
    print("Single Mode는 추후 추가될 예정입니다.\n")

    # 현재는 Multi Mode만 실행
    try:
        import multi
        print("Multi Mode를 시작합니다...")
        exit_code = multi.run_multi_mode()
        sys.exit(exit_code)
    except ImportError as e:
        print(f"오류: multi.py 모듈을 찾을 수 없습니다: {e}")
        print("multi.py 파일이 같은 폴더에 있는지 확인해주세요.")
        input("엔터 키를 눌러 종료...")
        sys.exit(1)
    except Exception as e:
        print(f"예상치 못한 오류가 발생했습니다: {e}")
        input("엔터 키를 눌러 종료...")
        sys.exit(1)


def run_multi_mode():
    """Multi Mode 직접 실행 (하위 호환성)"""
    try:
        import multi
        return multi.run_multi_mode()
    except ImportError as e:
        print(f"오류: multi.py 모듈을 찾을 수 없습니다: {e}")
        return 1


def run_single_mode():
    """Single Mode 실행 (추후 구현 예정)"""
    print("Single Mode는 아직 구현되지 않았습니다.")
    print("추후 업데이트에서 제공될 예정입니다.")
    return 1


if __name__ == "__main__":
    main()