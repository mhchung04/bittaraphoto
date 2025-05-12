import sys
import os
import shutil
import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                           QWidget, QFileDialog, QLineEdit, QLabel, QHBoxLayout,
                           QFrame, QSizePolicy, QSpacerItem, QMessageBox, QComboBox,
                           QDialog)  # QComboBox와 QDialog 추가
from PyQt5.QtGui import QFont, QDragEnterEvent, QDropEvent, QPixmap, QImage, QPainter
from PyQt5.QtCore import Qt
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PIL import Image


class DropZone(QLabel):
    """개별 드롭 존"""

    def __init__(self, zone_id, parent_drop_area):
        super().__init__()
        self.zone_id = zone_id
        self.parent_drop_area = parent_drop_area
        self.setAcceptDrops(True)

        # 기본 스타일 설정
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Arial", 12))
        self.setMinimumSize(280, 120)
        self.setText(f"사진 {zone_id + 1}\n드롭하세요")

        # 점선 테두리 스타일
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 8px;
                background-color: #f8f8f8;
                color: #555;
                padding: 10px;
                margin: 5px;
            }
        """)

    def dragEnterEvent(self, event):
        # 부모 창의 가공 상태 확인
        if hasattr(self.parent_drop_area.parent_window,
                   'processed_file') and self.parent_drop_area.parent_window.processed_file:
            event.ignore()
            return

        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            # 해당 영역만 하이라이트
            self.setStyleSheet("""
                QLabel {
                    border: 3px dashed #007ACC;
                    border-radius: 8px;
                    background-color: #e6f3ff;
                    color: #007ACC;
                    padding: 10px;
                    margin: 5px;
                    font-weight: bold;
                }
            """)

    def dragLeaveEvent(self, event):
        # 원래 스타일로 복원 (파일이 있는지 확인)
        if hasattr(self.parent_drop_area.parent_window, 'selected_files'):
            if self.parent_drop_area.parent_window.selected_files[self.zone_id] is not None:
                # 파일이 있는 경우 - 초록색 스타일 유지
                self.setStyleSheet("""
                    QLabel {
                        border: 2px solid #4CAF50;
                        border-radius: 8px;
                        background-color: #e8f5e8;
                        color: #2e7d32;
                        padding: 10px;
                        margin: 5px;
                        font-weight: bold;
                    }
                """)
            else:
                # 파일이 없는 경우 - 기본 스타일
                self.setStyleSheet("""
                    QLabel {
                        border: 2px dashed #aaa;
                        border-radius: 8px;
                        background-color: #f8f8f8;
                        color: #555;
                        padding: 10px;
                        margin: 5px;
                    }
                """)

    def dropEvent(self, event):
        # 부모 창의 가공 상태 확인
        if hasattr(self.parent_drop_area.parent_window,
                   'processed_file') and self.parent_drop_area.parent_window.processed_file:
            QMessageBox.warning(self.parent_drop_area.parent_window, "경고",
                                "이미 이미지 가공이 완료되었습니다.\n새 이미지를 추가하려면 먼저 '사진 초기화' 버튼을 누르세요.")
            event.ignore()
            return

        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                    # 파일 선택 완료 스타일
                    self.setText(f"사진 {self.zone_id + 1}\n{os.path.basename(file_path)}")
                    self.setStyleSheet("""
                        QLabel {
                            border: 2px solid #4CAF50;
                            border-radius: 8px;
                            background-color: #e8f5e8;
                            color: #2e7d32;
                            padding: 10px;
                            margin: 5px;
                            font-weight: bold;
                        }
                    """)

                    # 부모 창의 메서드 호출
                    if hasattr(self.parent_drop_area.parent_window, 'prepare_image'):
                        self.parent_drop_area.parent_window.prepare_image(file_path, self.zone_id)
                    break

            event.acceptProposedAction()


class DropArea(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 전체 프레임 스타일을 단순화
        self.setFrameStyle(QFrame.NoFrame)
        self.setLineWidth(0)
        self.setMinimumSize(600, 320)
        self.setAcceptDrops(False)  # 개별 존에서만 드롭 처리

        # 전체 배경 스타일
        self.setStyleSheet("""
            DropArea {
                background-color: #fafafa;
                border-radius: 10px;
            }
        """)

        # 4분할 레이아웃 생성
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 제목 라벨
        title_label = QLabel("이미지 드롭 영역 (4개)")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #333; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        # 상단 행
        top_layout = QHBoxLayout()
        top_layout.setSpacing(5)

        self.zone1 = DropZone(0, self)
        self.zone2 = DropZone(1, self)

        top_layout.addWidget(self.zone1)
        top_layout.addWidget(self.zone2)

        # 하단 행
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(5)

        self.zone3 = DropZone(2, self)
        self.zone4 = DropZone(3, self)

        bottom_layout.addWidget(self.zone3)
        bottom_layout.addWidget(self.zone4)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)

        # 파일 선택 버튼 (최소한으로 설계)
        self.select_btn = QPushButton("또는 파일 선택")
        self.select_btn.setFont(QFont("Arial", 11))  # 폰트 크기 약간 키움
        self.select_btn.setFixedSize(140, 32)  # 크기 약간 키움
        self.select_btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #888;
                        border: 1px solid #ccc;
                        padding: 3px 8px;
                        border-radius: 3px;
                        font-size: 10px;
                        margin-top: 8px;
                    }
                    QPushButton:hover {
                        color: #555;
                        border-color: #aaa;
                    }
                    QPushButton:pressed {
                        background-color: #f0f0f0;
                    }
                """)
        main_layout.addWidget(self.select_btn, 0, Qt.AlignCenter)  # 중앙 정렬

        self.parent_window = parent
        self.labels = [self.zone1, self.zone2, self.zone3, self.zone4]  # 호환성 유지

    def reset_zones(self):
        """모든 드롭 존을 초기 상태로 리셋"""
        for i, zone in enumerate([self.zone1, self.zone2, self.zone3, self.zone4]):
            zone.setText(f"사진 {i + 1}\n드롭하세요")
            zone.setStyleSheet("""
                QLabel {
                    border: 2px dashed #aaa;
                    border-radius: 8px;
                    background-color: #f8f8f8;
                    color: #555;
                    padding: 10px;
                    margin: 5px;
                }
            """)

    # 기존 메서드들 (호환성 유지)
    def dragEnterEvent(self, event):
        pass  # 개별 존에서 처리

    def dragLeaveEvent(self, event):
        pass  # 개별 존에서 처리

    def dropEvent(self, event):
        pass  # 개별 존에서 처리


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("사진 선택 및 인쇄")
        self.setGeometry(100, 100, 700, 700)  # 창 크기 증가

        # 추가: 첫 번째 체크 상태 관리 변수
        self.is_first_check = True

        # 종료 버튼을 우측 상단에 배치 (요구사항 3)
        self.exit_button = QPushButton("종료", self)
        self.exit_button.setFont(QFont("Arial", 10))
        self.exit_button.setStyleSheet("background-color: #bbbbbb; color: black; padding: 5px;")
        self.exit_button.clicked.connect(self.close_application)
        # 버튼 크기와 위치 설정
        self.exit_button.setFixedSize(60, 30)
        self.exit_button.move(self.width() - 70, 10)  # 우측 상단에 배치

        # 창 크기가 변경될 때 종료 버튼 위치 조정
        self.resizeEvent = self.on_resize

        # 메인 레이아웃 설정
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)  # 전체 간격 줄이기

        # 폴더 번호 입력을 위한 가로 레이아웃 생성 (라벨과 입력창을 나란히 배치)
        folder_layout = QHBoxLayout()

        # 폴더 번호 입력 라벨
        self.folder_label = QLabel("폴더 번호 입력:")
        self.folder_label.setFont(QFont("Arial", 16))
        folder_layout.addWidget(self.folder_label)

        # 폴더 번호 입력 필드
        self.folder_input = QLineEdit()
        self.folder_input.setFont(QFont("Arial", 16))
        self.folder_input.textChanged.connect(self.check_folder_exists)
        folder_layout.addWidget(self.folder_input)

        # 가로 레이아웃을 메인 레이아웃에 추가
        main_layout.addLayout(folder_layout)

        # 정보 표시를 위한 영역 생성 (간격을 좁게 설정)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)  # 간격 최소화

        # 폴더 존재 여부 표시
        self.folder_exists_label = QLabel("")  # 초기에는 빈 텍스트로 설정
        self.folder_exists_label.setFont(QFont("Arial", 12))
        info_layout.addWidget(self.folder_exists_label)

        # 새 폴더 생성 예상 정보 표시
        self.new_folder_label = QLabel("")  # 초기에는 빈 텍스트로 설정
        self.new_folder_label.setFont(QFont("Arial", 12))
        self.new_folder_label.setStyleSheet("color: blue;")
        info_layout.addWidget(self.new_folder_label)

        # 마지막 폴더 생성 시간 표시
        self.last_folder_time_label = QLabel("")
        self.last_folder_time_label.setFont(QFont("Arial", 12))
        self.last_folder_time_label.setStyleSheet("color: purple;")
        info_layout.addWidget(self.last_folder_time_label)

        # 정보 영역을 메인 레이아웃에 추가
        main_layout.addLayout(info_layout)

        # 사이 공간 최소화
        main_layout.addSpacerItem(QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # 드롭 영역 추가
        self.drop_area = DropArea(self)
        main_layout.addWidget(self.drop_area)
        # 파일 선택 버튼 이벤트 연결
        self.drop_area.select_btn.clicked.connect(self.select_image)

        # 상태 메시지 영역 추가 (새로 추가)
        self.status_message = QLabel("")
        self.status_message.setFont(QFont("Arial", 12))
        self.status_message.setAlignment(Qt.AlignCenter)
        self.status_message.setStyleSheet("color: #007700; margin: 10px 0px;")
        self.status_message.setWordWrap(True)  # 긴 텍스트 자동 줄바꿈
        main_layout.addWidget(self.status_message)

        # 이미지 미리보기 영역 추가
        preview_layout = QHBoxLayout()  # 가로 레이아웃으로 변경

        # 원본 이미지 미리보기 프레임
        self.preview_frame = QFrame()
        self.preview_frame.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.preview_frame.setLineWidth(1)
        self.preview_frame.setMinimumSize(250, 200)
        self.preview_frame.setStyleSheet("background-color: #f0f0f0;")

        preview_frame_layout = QVBoxLayout(self.preview_frame)
        preview_title = QLabel("원본 이미지")
        preview_title.setAlignment(Qt.AlignCenter)
        preview_title.setFont(QFont("Arial", 12, QFont.Bold))

        self.preview_label = QLabel("이미지 미리보기")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFont(QFont("Arial", 11))

        preview_frame_layout.addWidget(preview_title)
        preview_frame_layout.addWidget(self.preview_label)

        # 가공된 이미지 미리보기 프레임
        self.processed_frame = QFrame()
        self.processed_frame.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.processed_frame.setLineWidth(1)
        self.processed_frame.setMinimumSize(250, 200)
        self.processed_frame.setStyleSheet("background-color: #f0f0f0;")

        processed_frame_layout = QVBoxLayout(self.processed_frame)
        processed_title = QLabel("가공된 이미지")
        processed_title.setAlignment(Qt.AlignCenter)
        processed_title.setFont(QFont("Arial", 12, QFont.Bold))

        self.processed_label = QLabel("가공 후 미리보기")
        self.processed_label.setAlignment(Qt.AlignCenter)
        self.processed_label.setFont(QFont("Arial", 11))

        processed_frame_layout.addWidget(processed_title)
        processed_frame_layout.addWidget(self.processed_label)

        # 두 프레임을 가로 레이아웃에 추가
        preview_layout.addWidget(self.preview_frame)
        preview_layout.addWidget(self.processed_frame)

        main_layout.addLayout(preview_layout)

        # 버튼 생성
        # 버튼 생성
        button_layout = QHBoxLayout()

        # 가공하기 버튼 추가 (위치 변경됨)
        self.process_button = QPushButton("가공하기")
        self.process_button.setFont(QFont("Arial", 14))
        self.process_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        self.process_button.setEnabled(False)  # 초기에는 비활성화
        self.process_button.clicked.connect(self.process_selected_image)
        button_layout.addWidget(self.process_button)

        # 사진 초기화 버튼 추가 (위치 변경됨)
        self.reset_image_button = QPushButton("사진 초기화")
        self.reset_image_button.setFont(QFont("Arial", 14))
        self.reset_image_button.setStyleSheet("background-color: #FF9800; color: white; padding: 8px;")
        self.reset_image_button.clicked.connect(self.reset_image)
        button_layout.addWidget(self.reset_image_button)

        # 인쇄 버튼
        self.print_button = QPushButton("인쇄")
        self.print_button.setFont(QFont("Arial", 14))
        self.print_button.setEnabled(False)  # 초기에는 비활성화
        self.print_button.clicked.connect(self.print_image)
        button_layout.addWidget(self.print_button)

        # 초기화 버튼 -> 새로 만들기로 이름 변경 및 위치 이동 (요구사항 2)
        self.reset_button = QPushButton("새로 만들기")
        self.reset_button.setFont(QFont("Arial", 14))
        self.reset_button.setStyleSheet("background-color: #f44336; color: white; padding: 8px;")
        self.reset_button.clicked.connect(self.reset_application)
        button_layout.addWidget(self.reset_button)

        main_layout.addLayout(button_layout)

        # QWidget에 레이아웃 설정
        container = QWidget()
        container.setLayout(main_layout)

        # 창에 컨테이너 위젯을 설정
        self.setCentralWidget(container)

        # 선택된 파일들 초기화 (4개 파일을 저장할 리스트)
        self.selected_files = [None, None, None, None]  # 4개 위치별 파일
        self.processed_file = None
        self.created_folder = None

        # 프레임 선택을 위한 레이아웃 추가
        frame_layout = QHBoxLayout()
        frame_label = QLabel("프레임 선택:")
        frame_label.setFont(QFont("Arial", 14))
        frame_layout.addWidget(frame_label)

        self.frame_combo = QComboBox()
        self.frame_combo.setFont(QFont("Arial", 14))
        self.frame_combo.addItem("프레임 1", "01.png")  # 첫 번째 프레임
        self.frame_combo.addItem("프레임 2", "02.png")  # 두 번째 프레임
        self.frame_combo.addItem("프레임 3", "03.png")  # 세 번째 프레임
        self.frame_combo.addItem("프레임 없음", "none")  # 프레임 없음 옵션
        # 나중에 다른 프레임 추가 가능
        frame_layout.addWidget(self.frame_combo)

        # 프레임 미리보기 버튼
        self.preview_frame_btn = QPushButton("프레임 미리보기")
        self.preview_frame_btn.setFont(QFont("Arial", 12))
        self.preview_frame_btn.clicked.connect(self.show_frame_preview)  # 메소드 이름 변경
        frame_layout.addWidget(self.preview_frame_btn)

        # 레이아웃에 추가
        main_layout.addLayout(frame_layout)

        # 선택된 프레임 변수 초기화
        self.selected_frame = "01.png"

        # 프레임 콤보박스 이벤트 연결
        self.frame_combo.currentIndexChanged.connect(self.on_frame_changed)

    # 메소드 이름 변경
    def show_frame_preview(self):
        """선택된 프레임 미리보기"""
        if self.selected_frame == "none":
            QMessageBox.information(self, "프레임 미리보기", "선택된 프레임이 없습니다.")
            return

        frame_path = os.path.join(os.getcwd(), 'frame', self.selected_frame)
        if not os.path.exists(frame_path):
            QMessageBox.warning(self, "오류", f"프레임 파일을 찾을 수 없습니다: {frame_path}")
            return

        # 프레임 이미지 표시
        pixmap = QPixmap(frame_path)
        if not pixmap.isNull():
            preview_width = 300
            preview_height = 300
            pixmap = pixmap.scaled(preview_width, preview_height,
                                   Qt.KeepAspectRatio, Qt.SmoothTransformation)

            # 간단한 미리보기 창 생성
            preview_dialog = QDialog(self)
            preview_dialog.setWindowTitle("프레임 미리보기")
            preview_layout = QVBoxLayout()

            frame_preview = QLabel()
            frame_preview.setPixmap(pixmap)
            frame_preview.setAlignment(Qt.AlignCenter)

            close_btn = QPushButton("닫기")
            close_btn.clicked.connect(preview_dialog.close)

            preview_layout.addWidget(frame_preview)
            preview_layout.addWidget(close_btn)

            preview_dialog.setLayout(preview_layout)
            preview_dialog.exec_()

    def on_frame_changed(self, index):
        """프레임 선택이 변경되었을 때 호출"""
        self.selected_frame = self.frame_combo.currentData()
        print(f"선택된 프레임: {self.selected_frame}")

        # 이미 이미지들이 선택되어 있다면 가공하기 버튼 활성화
        if any(file is not None for file in self.selected_files):
            # 4개 모두 선택되었을 때만 활성화
            if all(file is not None for file in self.selected_files):
                self.process_button.setEnabled(True)
                self.status_message.setText("새로운 프레임이 선택되었습니다. 가공하기 버튼을 눌러 이미지를 재가공하세요.")
                self.status_message.setStyleSheet("color: #007ACC; margin: 10px 0px;")
            else:
                filled_count = sum(1 for file in self.selected_files if file is not None)
                self.status_message.setText(f"새로운 프레임이 선택되었습니다. {filled_count}/4개 이미지가 준비되었습니다.")
                self.status_message.setStyleSheet("color: #007ACC; margin: 10px 0px;")
                self.process_button.setEnabled(False)

    def preview_frame(self):
        """선택된 프레임 미리보기"""
        if self.selected_frame == "none":
            QMessageBox.information(self, "프레임 미리보기", "선택된 프레임이 없습니다.")
            return

        frame_path = os.path.join(os.getcwd(), 'frame', self.selected_frame)
        if not os.path.exists(frame_path):
            QMessageBox.warning(self, "오류", f"프레임 파일을 찾을 수 없습니다: {frame_path}")
            return

        # 프레임 이미지 표시
        pixmap = QPixmap(frame_path)
        if not pixmap.isNull():
            preview_width = 300
            preview_height = 300
            pixmap = pixmap.scaled(preview_width, preview_height,
                                   Qt.KeepAspectRatio, Qt.SmoothTransformation)

            # 간단한 미리보기 창 생성
            preview_dialog = QDialog(self)
            preview_dialog.setWindowTitle("프레임 미리보기")
            preview_layout = QVBoxLayout()

            frame_preview = QLabel()
            frame_preview.setPixmap(pixmap)
            frame_preview.setAlignment(Qt.AlignCenter)

            close_btn = QPushButton("닫기")
            close_btn.clicked.connect(preview_dialog.close)

            preview_layout.addWidget(frame_preview)
            preview_layout.addWidget(close_btn)

            preview_dialog.setLayout(preview_layout)
            preview_dialog.exec_()

    def on_resize(self, event):
        """창 크기가 변경될 때 종료 버튼 위치 조정"""
        # 종료 버튼 위치 재조정
        self.exit_button.move(self.width() - 70, 10)
        # 기본 이벤트 처리 호출
        super().resizeEvent(event)

    def reset_image(self):
        """사진 초기화 버튼을 눌렀을 때 실행되는 메서드"""
        if not any(file is not None for file in self.selected_files):
            # 이미 초기 상태이면 아무 작업 하지 않음
            return

        # 확인 메시지
        reply = QMessageBox.question(self, '사진 초기화 확인',
                                     "현재 선택된 사진들을 초기화하시겠습니까?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.No:
            return

        # 가공된 폴더가 있으면 그 안의 파일 삭제
        if self.created_folder and os.path.exists(self.created_folder):
            try:
                files = os.listdir(self.created_folder)
                for file in files:
                    # 이전 원본 복사본과 가공된 이미지 삭제
                    if file.startswith("copy") or file.startswith("processed_"):
                        file_path = os.path.join(self.created_folder, file)
                        os.remove(file_path)
                        print(f"파일 삭제됨: {file_path}")
            except Exception as e:
                print(f"파일 삭제 오류: {e}")
                # 삭제 실패해도 계속 진행

        # 선택된 파일들과 가공된 파일 정보 초기화
        self.selected_files = [None, None, None, None]
        self.processed_file = None

        # 새로운 드롭 영역 초기화
        self.drop_area.reset_zones()

        # 미리보기 초기화
        self.preview_label.setText("이미지 미리보기")
        self.preview_label.setPixmap(QPixmap())

        self.processed_label.setText("가공 후 미리보기")
        self.processed_label.setPixmap(QPixmap())

        # 상태 메시지 초기화
        self.status_message.setText("")

        # 버튼 상태 초기화
        self.process_button.setEnabled(False)
        self.print_button.setEnabled(False)

        print("사진들이 초기화되었습니다.")
        QMessageBox.information(self, "알림", "사진들이 초기화되었습니다.")

    def keyPressEvent(self, event):
        """키 이벤트 처리"""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # 엔터 키 눌림, 현재 포커스된 위젯 확인
            focused_widget = QApplication.focusWidget()
            if focused_widget == self.folder_input and not self.folder_input.text().strip() == "":
                # 폴더 입력 필드에 포커스가 있고 텍스트가 있으면
                folder_number_text = self.folder_input.text().strip()
                if folder_number_text.isdigit():
                    # 폴더 존재 여부 확인하고 실제 생성될 폴더 이름 가져오기
                    actual_folder_name = self.get_actual_folder_name(folder_number_text)

                    # 확인 메시지에 실제 폴더 이름 표시
                    reply = QMessageBox.question(self, '폴더 번호 확인',
                                                 f"폴더 이름을 '{actual_folder_name}'로 설정하시겠습니까?\n설정 후에는 변경할 수 없습니다.",
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

                    if reply == QMessageBox.Yes:
                        # 확인 시 텍스트 필드 비활성화
                        self.folder_input.setEnabled(False)
                        self.folder_input.setStyleSheet("background-color: #e0e0e0;")
                        self.check_folder_exists()  # 폴더 존재 여부 다시 확인
                        # 폴더 즉시 생성
                        self.create_folder(actual_folder_name)
                        # 추가 시작 - 다른 레이블 초기화하고 생성된 폴더 메시지만 표시
                        folder_name = os.path.basename(actual_folder_name)
                        self.folder_exists_label.setText(f"'{folder_name}' 폴더가 생성되었습니다.")
                        self.folder_exists_label.setStyleSheet("color: green;")
                        self.new_folder_label.setText("")
                        self.last_folder_time_label.setText("")
                        # 추가 끝
                    else:
                        # 취소 시 텍스트 필드 내용 비우기
                        self.folder_input.clear()

        # 기본 키 이벤트 처리
        super().keyPressEvent(event)

    def get_actual_folder_name(self, folder_number_text):
        """실제 생성될 폴더 이름을 반환하는 메서드"""
        folder_name = folder_number_text
        folder_path = os.path.join(os.getcwd(), folder_name)

        if os.path.exists(folder_path):
            # 이미 폴더가 존재하면 언더바 폴더 이름 계산
            base_folder_name = folder_name
            existing_folders = [d for d in os.listdir(os.getcwd())
                                if os.path.isdir(os.path.join(os.getcwd(), d)) and
                                d.startswith(base_folder_name + "_")]

            if existing_folders:
                # 숫자 부분만 추출하여 가장 큰 번호 찾기
                max_num = 0
                for folder in existing_folders:
                    try:
                        suffix = folder[len(base_folder_name) + 1:]
                        if suffix.isdigit():
                            num = int(suffix)
                            if num > max_num:
                                max_num = num
                    except:
                        continue

                folder_name = f"{base_folder_name}_{max_num + 1}"
            else:
                # 첫 번째 언더바 폴더 생성
                folder_name = f"{base_folder_name}_1"

        return folder_name

    # 이 위치(get_actual_folder_name 메서드 뒤)에 다음 메서드 추가
    def create_folder(self, folder_name):
        """폴더를 즉시 생성하는 메서드"""
        folder_path = os.path.join(os.getcwd(), folder_name)
        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path)
                self.created_folder = folder_path
                # 상태 메시지와 레이블 모두 업데이트 - 수정 시작
                self.status_message.setText(f"'{folder_name}' 폴더가 생성되었습니다.")
                self.status_message.setStyleSheet("color: #007700; margin: 10px 0px;")

                # 다른 레이블 초기화
                self.folder_exists_label.setText(f"'{folder_name}' 폴더가 생성되었습니다.")
                self.folder_exists_label.setStyleSheet("color: green;")
                self.new_folder_label.setText("")
                self.last_folder_time_label.setText("")
                # 수정 끝

                print(f"폴더 생성됨: {folder_path}")
            except Exception as e:
                self.status_message.setText(f"폴더 생성 중 오류가 발생했습니다: {str(e)}")
                self.status_message.setStyleSheet("color: #FF0000; margin: 10px 0px;")
                print(f"폴더 생성 오류: {e}")
        else:
            self.created_folder = folder_path
            # 이미 존재하는 폴더 메시지도 수정 - 수정 시작
            self.status_message.setText(f"'{folder_name}' 폴더를 사용합니다.")
            self.status_message.setStyleSheet("color: #007700; margin: 10px 0px;")

            # 다른 레이블 초기화 및 설정
            self.folder_exists_label.setText(f"'{folder_name}' 폴더가 사용됩니다.")
            self.folder_exists_label.setStyleSheet("color: green;")
            self.new_folder_label.setText("")
            self.last_folder_time_label.setText("")
            # 수정 끝

    def check_folder_exists(self):
        # 현재 폴더 번호 저장
        previous_folder_number = self.folder_input.text().strip() if hasattr(self, 'previous_folder_number') else None

        folder_number_text = self.folder_input.text().strip()  # 입력된 번호 가져오기 및 공백 제거

        # Enter 키가 눌렸는지 확인 (사용자가 폴더 번호 입력을 완료했는지)
        '''
        if not previous_folder_number and folder_number_text and folder_number_text.isdigit():
            # 유효한 숫자를 처음 입력한 경우, 확인 메시지
            reply = QMessageBox.question(self, '폴더 번호 확인',
                                         f"폴더 번호를 '{folder_number_text}'로 설정하시겠습니까?\n설정 후에는 변경할 수 없습니다.",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                # 확인 시 텍스트 필드 비활성화
                self.folder_input.setEnabled(False)
                self.folder_input.setStyleSheet("background-color: #e0e0e0;")  # 배경색 회색으로 변경
                self.previous_folder_number = folder_number_text
            else:
                # 취소 시 텍스트 필드 내용 비우기
                self.folder_input.clear()
                return
        '''

        # 폴더 번호가 변경되면 created_folder 초기화
        if previous_folder_number != folder_number_text:
            self.created_folder = None
            self.previous_folder_number = folder_number_text

        # 모든 레이블 초기화 - 이 부분 수정
        self.folder_exists_label.setText("")
        self.new_folder_label.setText("")
        self.last_folder_time_label.setText("")

        # 폴더가 이미 생성된 경우 관련 메시지만 표시하고 다른 메시지는 표시하지 않도록 수정
        if self.created_folder and os.path.exists(self.created_folder):
            folder_name = os.path.basename(self.created_folder)
            self.folder_exists_label.setText(f"'{folder_name}' 폴더가 생성되었습니다.")
            self.folder_exists_label.setStyleSheet("color: green;")
            return  # 폴더가 이미 생성된 경우 더 이상 진행하지 않음
        # 여기까지 수정

        if not folder_number_text:  # 빈 입력인 경우
            return

        if folder_number_text.isdigit():  # 숫자가 입력된 경우에만 체크
            folder_number = int(folder_number_text)  # 숫자로 변환
            folder_name = str(folder_number)
            folder_path = os.path.join(os.getcwd(), folder_name)

            if os.path.exists(folder_path):  # 폴더가 존재하면
                self.folder_exists_label.setText("이미 있는 이름입니다.")
                self.folder_exists_label.setStyleSheet("color: red;")

                # 마지막 폴더 생성 시간 표시
                folder_creation_time = os.path.getctime(folder_path)
                time_str = datetime.datetime.fromtimestamp(folder_creation_time).strftime('%Y-%m-%d %H:%M:%S')
                self.last_folder_time_label.setText(f"'{folder_name}' 폴더 생성 시간: {time_str}")

                # 새로 생성될 폴더 이름 계산
                base_folder_name = folder_name
                existing_folders = [d for d in os.listdir(os.getcwd())
                                    if os.path.isdir(os.path.join(os.getcwd(), d)) and
                                    d.startswith(base_folder_name + "_")]

                # 언더바 폴더가 이미 있으면 마지막 번호 + 1로 표시
                if existing_folders:
                    # 숫자 부분만 추출하여 가장 큰 번호 찾기
                    max_num = 0
                    max_folder = None
                    for folder in existing_folders:
                        try:
                            suffix = folder[len(base_folder_name) + 1:]
                            if suffix.isdigit():
                                num = int(suffix)
                                if num > max_num:
                                    max_num = num
                                    max_folder = folder
                        except:
                            continue

                    # 마지막 언더바 폴더의 생성 시간도 표시
                    if max_folder:
                        max_folder_path = os.path.join(os.getcwd(), max_folder)
                        max_folder_creation_time = os.path.getctime(max_folder_path)
                        max_time_str = datetime.datetime.fromtimestamp(max_folder_creation_time).strftime(
                            '%Y-%m-%d %H:%M:%S')
                        self.last_folder_time_label.setText(f"'{max_folder}' 폴더 생성 시간: {max_time_str}")

                    new_folder_name = f"{base_folder_name}_{max_num + 1}"
                    self.new_folder_label.setText(f"'{new_folder_name}'에 새로 생성됩니다.")
                else:
                    # 첫 번째 언더바 폴더 생성
                    new_folder_name = f"{base_folder_name}_1"
                    self.new_folder_label.setText(f"'{new_folder_name}'에 새로 생성됩니다.")
            else:
                self.folder_exists_label.setText("새로운 이름입니다.")
                self.folder_exists_label.setStyleSheet("color: green;")
                self.new_folder_label.setText(f"'{folder_name}'에 새로 생성됩니다.")
        else:
            self.folder_exists_label.setText("유효한 번호를 입력해주세요.")
            self.folder_exists_label.setStyleSheet("color: orange;")

    def select_image(self):
        # 이미 가공이 완료된 상태인지 확인
        if self.processed_file:
            QMessageBox.warning(self, "경고", "이미 이미지 가공이 완료되었습니다.\n새 이미지를 추가하려면 먼저 '사진 초기화' 버튼을 누르세요.")
            return

        folder_number_text = self.folder_input.text().strip()  # 입력된 번호 가져오기

        if not folder_number_text.isdigit() or not folder_number_text:  # 숫자가 아니거나 입력이 없다면
            print("유효한 번호를 입력해주세요.")
            QMessageBox.warning(self, "경고", "유효한 폴더 번호를 먼저 입력해주세요.")
            return

        # 여러 파일 선택 다이얼로그 열기
        files, _ = QFileDialog.getOpenFileNames(self, "Select Images (최대 4개)", "",
                                                "Image Files (*.png *.jpg *.jpeg *.bmp)")

        if files:
            # 최대 4개까지만 처리
            files = files[:4]

            # 각 파일을 순서대로 슬롯에 배치
            for i, file_path in enumerate(files):
                self.prepare_image(file_path, i)
                # 새로운 드롭 영역 업데이트
                zone = [self.drop_area.zone1, self.drop_area.zone2, self.drop_area.zone3, self.drop_area.zone4][i]
                zone.setText(f"사진 {i + 1}\n{os.path.basename(file_path)}")
                zone.setStyleSheet("""
                    QLabel {
                        border: 2px solid #4CAF50;
                        border-radius: 8px;
                        background-color: #e8f5e8;
                        color: #2e7d32;
                        padding: 10px;
                        margin: 5px;
                        font-weight: bold;
                    }
                """)

    def prepare_image(self, file_path, slot_index):
        """이미지를 준비하고 미리보기 표시 (4개 슬롯 중 하나에 배치)"""
        # 이미 가공이 완료된 상태인지 확인
        if self.processed_file:
            QMessageBox.warning(self, "경고", "이미 이미지 가공이 완료되었습니다.\n새 이미지를 추가하려면 먼저 '사진 초기화' 버튼을 누르세요.")
            return

        # 해당 슬롯에 파일 저장
        self.selected_files[slot_index] = file_path
        print(f"슬롯 {slot_index + 1}에 선택된 파일: {file_path}")

        # 폴더 번호 확인
        folder_number_text = self.folder_input.text().strip()
        if not folder_number_text or not folder_number_text.isdigit():
            # 유효한 폴더 번호가 없을 경우 알림
            print("유효한 폴더 번호를 먼저 입력해주세요.")
            QMessageBox.warning(self, "경고", "유효한 폴더 번호를 먼저 입력해주세요.")
            return

        # 미리보기 업데이트
        self.update_preview()

        # 모든 슬롯이 채워졌는지 확인하여 가공하기 버튼 활성화
        if all(file is not None for file in self.selected_files):
            self.process_button.setEnabled(True)
            self.status_message.setText("4개 이미지가 모두 준비되었습니다. 가공하기 버튼을 누르세요.")
            self.status_message.setStyleSheet("color: #007700; margin: 10px 0px;")
        else:
            filled_count = sum(1 for file in self.selected_files if file is not None)
            self.status_message.setText(f"{filled_count}/4개 이미지가 준비되었습니다.")
            self.status_message.setStyleSheet("color: #007ACC; margin: 10px 0px;")
            self.process_button.setEnabled(False)

    def update_preview(self):
        """4분할 미리보기 업데이트"""
        # 미리보기 프레임 크기
        preview_width = self.preview_frame.width() - 20
        preview_height = self.preview_frame.height() - 40  # 제목 공간 고려

        # 각 셀 크기 (2x2 그리드)
        cell_width = preview_width // 2
        cell_height = preview_height // 2

        # 새로운 4분할 이미지 생성
        preview_image = QPixmap(preview_width, preview_height)
        preview_image.fill(Qt.lightGray)

        painter = QPainter(preview_image)

        positions = [
            (0, 0),  # 좌상
            (cell_width, 0),  # 우상
            (0, cell_height),  # 좌하
            (cell_width, cell_height)  # 우하
        ]

        for i, file_path in enumerate(self.selected_files):
            x, y = positions[i]

            if file_path and os.path.exists(file_path):
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    # 각 셀에 맞게 크기 조정
                    scaled_pixmap = pixmap.scaled(cell_width - 2, cell_height - 2,
                                                  Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    # 중앙 정렬을 위한 오프셋 계산
                    offset_x = (cell_width - scaled_pixmap.width()) // 2
                    offset_y = (cell_height - scaled_pixmap.height()) // 2
                    painter.drawPixmap(x + offset_x, y + offset_y, scaled_pixmap)
            else:
                # 빈 슬롯 표시
                painter.setPen(Qt.darkGray)
                painter.drawRect(x + 1, y + 1, cell_width - 2, cell_height - 2)
                painter.drawText(x + 10, y + cell_height // 2, f"이미지 {i + 1}")

        # 격자 그리기
        painter.setPen(Qt.black)
        painter.drawLine(cell_width, 0, cell_width, preview_height)  # 세로선
        painter.drawLine(0, cell_height, preview_width, cell_height)  # 가로선

        painter.end()

        self.preview_label.setPixmap(preview_image)
        self.preview_label.setAlignment(Qt.AlignCenter)

    # process_selected_image 메서드에서 수정할 부분
    def process_selected_image(self):
        """가공하기 버튼을 눌렀을 때 실행되는 메서드"""
        # 4개 파일이 모두 선택되었는지 확인
        if not all(file is not None for file in self.selected_files):
            QMessageBox.warning(self, "경고", "4개 이미지를 모두 선택해주세요.")
            return

        folder_number_text = self.folder_input.text().strip()
        if not folder_number_text or not folder_number_text.isdigit():
            QMessageBox.warning(self, "경고", "유효한 폴더 번호를 입력해주세요.")
            return

        # 폴더 번호가 고정되지 않았으면 고정 확인
        if self.folder_input.isEnabled():
            reply = QMessageBox.question(self, '폴더 번호 확인',
                                         f"폴더 번호를 '{folder_number_text}'로 설정하시겠습니까?\n설정 후에는 변경할 수 없습니다.",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                # 확인 시 텍스트 필드 비활성화
                self.folder_input.setEnabled(False)
                self.folder_input.setStyleSheet("background-color: #e0e0e0;")  # 배경색 회색으로 변경
            else:
                # 취소 시 처리 중단
                return

        # 폴더가 없으면 생성
        if not self.created_folder or not os.path.exists(self.created_folder):
            actual_folder_name = self.get_actual_folder_name(folder_number_text)
            self.create_folder(actual_folder_name)
            folder_name = os.path.basename(self.created_folder)
            self.folder_exists_label.setText(f"'{folder_name}' 폴더가 생성되었습니다.")
            self.folder_exists_label.setStyleSheet("color: green;")
            self.new_folder_label.setText("")
            self.last_folder_time_label.setText("")

        # 4개 파일 처리
        processed_path = self.process_and_save(self.selected_files, self.created_folder)

        # 가공된 이미지 미리보기 표시
        if processed_path and os.path.exists(processed_path):
            self.processed_file = processed_path  # 가공된 파일 경로 저장
            pixmap = QPixmap(processed_path)
            if not pixmap.isNull():
                # 미리보기 크기에 맞게 이미지 크기 조정
                preview_width = self.processed_frame.width() - 20  # 여백 고려
                preview_height = self.processed_frame.height() - 20  # 여백 고려
                pixmap = pixmap.scaled(preview_width, preview_height,
                                       Qt.KeepAspectRatio, Qt.SmoothTransformation)

                self.processed_label.setPixmap(pixmap)
                self.processed_label.setAlignment(Qt.AlignCenter)
                self.print_button.setEnabled(True)  # 인쇄 버튼 활성화

                # 가공 완료 메시지 설정
                folder_name = os.path.basename(self.created_folder)
                frame_name = self.frame_combo.currentText()  # 현재 선택된 프레임 이름 표시
                self.status_message.setText(f"{frame_name}로 가공이 성공적으로 완료되었습니다.\n'{folder_name}' 폴더에 저장되었습니다.")
                self.status_message.setStyleSheet("color: #007700; margin: 10px 0px;")
            else:
                self.processed_label.setText("가공된 이미지를 표시할 수 없습니다")
                self.status_message.setText("가공된 이미지를 표시할 수 없습니다.")
                self.status_message.setStyleSheet("color: #FF0000; margin: 10px 0px;")
        else:
            self.processed_label.setText("가공된 이미지를 표시할 수 없습니다")
            self.status_message.setText("이미지 가공에 실패했습니다.")
            self.status_message.setStyleSheet("color: #FF0000; margin: 10px 0px;")

        # 가공 후 버튼 상태 조정
        self.process_button.setEnabled(False)  # 가공 후 버튼 비활성화

    def create_folder_and_save(self, file, folder_number):
        # 폴더 이름을 사용자 입력으로 지정
        base_folder_name = str(folder_number)
        folder_name = base_folder_name
        folder_path = os.path.join(os.getcwd(), folder_name)

        # 폴더가 이미 존재하면 언더바로 새로운 폴더 생성
        if os.path.exists(folder_path):
            # 현재 존재하는 언더바 폴더들 확인
            existing_folders = [d for d in os.listdir(os.getcwd())
                                if os.path.isdir(os.path.join(os.getcwd(), d)) and
                                d.startswith(base_folder_name + "_")]

            # 언더바 폴더가 이미 있으면 마지막 번호 + 1로 생성
            if existing_folders:
                # 숫자 부분만 추출하여 가장 큰 번호 찾기
                max_num = 0
                for folder in existing_folders:
                    try:
                        # base_folder_name_숫자 형식에서 숫자 부분 추출
                        suffix = folder[len(base_folder_name) + 1:]
                        if suffix.isdigit():
                            num = int(suffix)
                            if num > max_num:
                                max_num = num
                    except:
                        continue

                folder_name = f"{base_folder_name}_{max_num + 1}"
            else:
                # 첫 번째 언더바 폴더 생성
                folder_name = f"{base_folder_name}_1"

        folder_path = os.path.join(os.getcwd(), folder_name)
        os.makedirs(folder_path, exist_ok=True)
        self.created_folder = folder_path  # 생성된 폴더 경로 저장

        print(f"폴더 생성됨: {folder_path}")

        # 가공한 파일과 복사본을 그 폴더에 저장
        processed_path = self.process_and_save(file, folder_path)

        # 가공된 이미지 경로 반환
        return processed_path

    def process_and_save(self, files, folder_path):
        processed_image_path = None

        # 이전 파일이 있으면 삭제
        try:
            old_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            for old_file in old_files:
                # 이전 원본 복사본과 가공된 이미지 삭제
                if old_file.startswith("copy") or old_file.startswith("processed_"):
                    old_file_path = os.path.join(folder_path, old_file)
                    os.remove(old_file_path)
                    print(f"파일 삭제됨: {old_file_path}")
        except Exception as e:
            print(f"파일 삭제 오류: {e}")
            # 삭제 실패해도 계속 진행

        # 이미지 가공
        try:
            processed_image_path = self.process_image(files, folder_path)
            if processed_image_path:
                print(f"가공된 이미지 저장됨: {processed_image_path}")
        except Exception as e:
            print(f"이미지 가공 오류: {e}")
            QMessageBox.critical(self, "오류", f"이미지 가공 중 오류가 발생했습니다: {str(e)}")

        # 현재 파일들을 copy1_, copy2_, copy3_, copy4_ 형식으로 저장
        try:
            for i, file_path in enumerate(files):
                if file_path and os.path.exists(file_path):
                    base_name = os.path.basename(file_path)
                    copy_filename = f"copy{i + 1}_{base_name}"
                    file_copy_path = os.path.join(folder_path, copy_filename)
                    shutil.copy(file_path, file_copy_path)
                    print(f"파일 복사본 저장됨: {file_copy_path}")
        except Exception as e:
            print(f"파일 복사 오류: {e}")
            QMessageBox.critical(self, "오류", f"파일 복사 중 오류가 발생했습니다: {str(e)}")

        return processed_image_path

    def process_image(self, files, folder_path):
        # 가공 파일명 생성 (첫 번째 파일명 기준)
        base_name = os.path.basename(files[0]) if files[0] else "image.jpg"
        processed_image_path = os.path.join(folder_path, "processed_" + base_name)

        # 프레임 없음 옵션 처리
        if self.selected_frame == "none":
            # 단순 복사 또는 품질 향상 처리 (첫 번째 이미지만)
            if files[0]:
                image = Image.open(files[0])
                image.save(processed_image_path, quality=100)
            return processed_image_path

        # processing.py의 함수 사용하여 프레임에 4개 이미지 삽입
        try:
            from processing import insert_images_into_frame
            frame_path = os.path.join(os.getcwd(), 'frame', self.selected_frame)

            # 프레임 폴더가 없으면 생성
            os.makedirs(os.path.dirname(frame_path), exist_ok=True)

            # 프레임 이미지가 없으면 단순 복사로 폴백
            if not os.path.exists(frame_path):
                QMessageBox.warning(self, "경고", "프레임 이미지를 찾을 수 없어 원본을 그대로 사용합니다.")
                if files[0]:
                    shutil.copy(files[0], processed_image_path)
            else:
                # 4개 이미지를 위한 photo_regions 생성
                photo_regions = []

                # 프레임에 따라 다른 파라미터 설정
                if self.selected_frame == "03.png":  # 프레임 3
                    # 4개 영역 좌표 설정 (예시 - 실제 프레임에 맞게 조정 필요)
                    regions = [
                        (0, 0, 500, 525),  # 좌상
                        (500, 0, 1000, 525),  # 우상
                        (0, 525, 500, 1050),  # 좌하
                        (500, 525, 1000, 1050)  # 우하
                    ]
                else:  # 프레임 1과 2
                    # 기본 4개 영역 좌표 설정
                    regions = [
                        (30, 30, 500, 525),  # 좌상
                        (500, 30, 970, 525),  # 우상
                        (30, 525, 500, 1020),  # 좌하
                        (500, 525, 970, 1020)  # 우하
                    ]

                # 실제 파일이 있는 경우만 photo_regions에 추가
                for i, file_path in enumerate(files):
                    if file_path and os.path.exists(file_path):
                        photo_regions.append((file_path, regions[i]))

                # 최소 1개 이미지가 있는 경우에만 처리
                if photo_regions:
                    insert_images_into_frame(photo_regions, frame_path, processed_image_path)
                    self.status_message.setText(f"이미지가 '{self.selected_frame}' 프레임으로 가공되었습니다.")
                else:
                    QMessageBox.warning(self, "경고", "처리할 이미지가 없습니다.")
                    return None

        except Exception as e:
            error_msg = f"이미지 가공 중 오류가 발생했습니다: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "오류", error_msg)
            # 오류 발생 시 첫 번째 원본 복사
            if files[0]:
                shutil.copy(files[0], processed_image_path)
            self.status_message.setText("오류로 인해 원본 이미지가 그대로 사용되었습니다.")
            self.status_message.setStyleSheet("color: #FF0000; margin: 10px 0px;")

        return processed_image_path

    def print_image(self):
        if not self.processed_file or not os.path.exists(self.processed_file):
            QMessageBox.warning(self, "경고", "인쇄할 이미지가 없습니다. 먼저 이미지를 가공해주세요.")
            return

        # 인쇄할 이미지 로드
        image = QImage(self.processed_file)
        if image.isNull():
            QMessageBox.critical(self, "오류", "이미지를 인쇄용으로 로드할 수 없습니다.")
            return

        # 프린터 설정
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.NativeFormat)

        # 프린트 대화상자 표시
        print_dialog = QPrintDialog(printer, self)
        print_dialog.setWindowTitle("이미지 인쇄")

        if print_dialog.exec_() == QPrintDialog.Accepted:
            # 인쇄 작업 시작
            painter = QPainter()
            if painter.begin(printer):
                # 프린터 페이지에 맞게 이미지 크기 조정
                rect = painter.viewport()
                image_size = image.size()
                image_size.scale(rect.size(), Qt.KeepAspectRatio)
                painter.setViewport(rect.x(), rect.y(), image_size.width(), image_size.height())
                painter.setWindow(image.rect())

                # 이미지 그리기
                painter.drawImage(0, 0, image)
                painter.end()
                QMessageBox.information(self, "성공", "이미지 인쇄가 시작되었습니다.")
            else:
                QMessageBox.critical(self, "오류", "인쇄 작업을 시작할 수 없습니다.")

        print("인쇄 중...")

    def reset_application(self):
        """초기화 버튼을 눌렀을 때 실행되는 메서드"""
        # 확인 메시지
        reply = QMessageBox.question(self, '초기화 확인',
                                     "정말로 현재 작업을 초기화하시겠습니까?\n생성된 폴더와 파일은 삭제되지 않습니다.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.No:
            return

        # UI 초기화
        self.folder_input.clear()

        # 폴더 입력 필드 다시 활성화
        self.folder_input.setEnabled(True)
        self.folder_input.setStyleSheet("")  # 원래 스타일로 복원

        self.folder_exists_label.setText("")
        self.new_folder_label.setText("")
        self.last_folder_time_label.setText("")

        # 새로운 드롭 영역 초기화
        self.drop_area.reset_zones()

        # 미리보기 초기화
        self.preview_label.setText("이미지 미리보기")
        self.preview_label.setPixmap(QPixmap())

        self.processed_label.setText("가공 후 미리보기")
        self.processed_label.setPixmap(QPixmap())

        # 상태 메시지 초기화
        self.status_message.setText("")

        # 버튼 상태 초기화
        self.process_button.setEnabled(False)
        self.print_button.setEnabled(False)

        # 내부 변수 초기화
        self.selected_files = [None, None, None, None]
        self.processed_file = None
        self.created_folder = None
        self.previous_folder_number = None
        self.is_first_check = True  # 첫 번째 체크 상태도 재설정

        # 프레임 선택 초기화
        self.frame_combo.setCurrentIndex(0)  # 기본 프레임으로 복원
        self.selected_frame = "01.png"

        print("애플리케이션이 초기화되었습니다.")
        QMessageBox.information(self, "알림", "모든 작업이 초기화되었습니다.")

    def close_application(self):
        reply = QMessageBox.question(self, '종료 확인',
                                     "정말로 종료하시겠습니까?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            print("애플리케이션 종료")
            sys.exit()


def main():
    app = QApplication(sys.argv)
    window = Window()  # GUI 초기화
    window.show()  # 창 표시
    sys.exit(app.exec_())  # 이벤트 루프 시작

if __name__ == "__main__":
    main()