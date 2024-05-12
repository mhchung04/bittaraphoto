import sys
import os
import shutil
import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                           QWidget, QFileDialog, QLineEdit, QLabel, QHBoxLayout,
                           QFrame, QSizePolicy, QSpacerItem, QMessageBox)
from PyQt5.QtGui import QFont, QDragEnterEvent, QDropEvent, QPixmap, QImage, QPainter
from PyQt5.QtCore import Qt
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PIL import Image

class DropArea(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.setLineWidth(2)
        self.setMidLineWidth(1)
        self.setMinimumSize(300, 150)  # 최소 크기 설정
        self.setAcceptDrops(True)  # 드롭 활성화

        # 점선 테두리 스타일 설정
        self.setStyleSheet("""
            DropArea {
                border: 2px dashed #aaa;
                border-radius: 5px;
                background-color: #f8f8f8;
            }
            DropArea:hover {
                border-color: #007ACC;
            }
        """)

        # 안내 텍스트 추가
        layout = QVBoxLayout(self)
        layout.setSpacing(10)  # 간격 줄이기

        self.label = QLabel("여기에 사진을 드롭하세요")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Arial", 14))
        self.label.setStyleSheet("color: #555;")
        layout.addWidget(self.label)

        # 파일 선택 버튼
        self.select_btn = QPushButton("또는 파일 선택하기")
        self.select_btn.setFont(QFont("Arial", 12))
        layout.addWidget(self.select_btn)

        self.parent_window = parent

    def dragEnterEvent(self, event: QDragEnterEvent):
        # 부모 창의 가공 상태 확인
        if hasattr(self.parent_window, 'processed_file') and self.parent_window.processed_file:
            # 이미 가공이 완료된 상태면 드래그 무시
            event.ignore()
            return

        # 드래그된 객체가 URL을 가지고 있는지 확인
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                DropArea {
                    border: 2px dashed #007ACC;
                    border-radius: 5px;
                    background-color: #e6f3ff;
                }
            """)

    def dragLeaveEvent(self, event):
        # 원래 스타일로 복원
        self.setStyleSheet("""
            DropArea {
                border: 2px dashed #aaa;
                border-radius: 5px;
                background-color: #f8f8f8;
            }
            DropArea:hover {
                border-color: #007ACC;
            }
        """)

    def dropEvent(self, event: QDropEvent):
        # 부모 창의 가공 상태 확인
        if hasattr(self.parent_window, 'processed_file') and self.parent_window.processed_file:
            # 이미 가공이 완료된 상태면 드롭 무시
            QMessageBox.warning(self.parent_window, "경고", "이미 이미지 가공이 완료되었습니다.\n새 이미지를 추가하려면 먼저 '사진 초기화' 버튼을 누르세요.")
            event.ignore()
            return

        # URL을 가진 드롭 이벤트 처리
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                    self.label.setText(f"선택된 파일: {os.path.basename(file_path)}")
                    # 부모 창의 메서드 호출하여 이미지 준비 (즉시 처리하지 않음)
                    if hasattr(self.parent_window, 'prepare_image'):
                        self.parent_window.prepare_image(file_path)
                    break

            # 스타일 원래대로 복원
            self.setStyleSheet("""
                DropArea {
                    border: 2px dashed #aaa;
                    border-radius: 5px;
                    background-color: #f8f8f8;
                }
                DropArea:hover {
                    border-color: #007ACC;
                }
            """)

            event.acceptProposedAction()


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

        # 선택된 파일 경로 초기화
        self.selected_file = None
        self.processed_file = None
        self.created_folder = None

    def on_resize(self, event):
        """창 크기가 변경될 때 종료 버튼 위치 조정"""
        # 종료 버튼 위치 재조정
        self.exit_button.move(self.width() - 70, 10)
        # 기본 이벤트 처리 호출
        super().resizeEvent(event)

    def reset_image(self):
        """사진 초기화 버튼을 눌렀을 때 실행되는 메서드"""
        if not self.selected_file:
            # 이미 초기 상태이면 아무 작업 하지 않음
            return

        # 확인 메시지
        reply = QMessageBox.question(self, '사진 초기화 확인',
                                     "현재 선택된 사진을 초기화하시겠습니까?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.No:
            return

        # 가공된 폴더가 있으면 그 안의 파일 삭제
        if self.created_folder and os.path.exists(self.created_folder):
            try:
                files = os.listdir(self.created_folder)
                for file in files:
                    # 이전 원본 복사본과 가공된 이미지 삭제
                    if file.startswith("copy_") or file.startswith("processed_"):
                        file_path = os.path.join(self.created_folder, file)
                        os.remove(file_path)
                        print(f"파일 삭제됨: {file_path}")
            except Exception as e:
                print(f"파일 삭제 오류: {e}")
                # 삭제 실패해도 계속 진행

        # 선택된 파일과 가공된 파일 정보 초기화
        self.selected_file = None
        self.processed_file = None

        # UI 초기화 (폴더 번호 관련 부분은 그대로 유지)
        self.drop_area.label.setText("여기에 사진을 드롭하세요")
        self.drop_area.label.setStyleSheet("color: #555;")

        self.preview_label.setText("이미지 미리보기")
        self.preview_label.setPixmap(QPixmap())

        self.processed_label.setText("가공 후 미리보기")
        self.processed_label.setPixmap(QPixmap())

        # 상태 메시지 초기화 (추가)
        self.status_message.setText("")

        # 버튼 상태 초기화
        self.process_button.setEnabled(False)
        self.print_button.setEnabled(False)

        print("사진이 초기화되었습니다.")
        QMessageBox.information(self, "알림", "사진이 초기화되었습니다.")

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

        # 파일 다이얼로그 열기
        file, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file:
            self.prepare_image(file)

    def prepare_image(self, file_path):
        """이미지를 준비하고 미리보기 표시 (즉시 처리하지 않음)"""
        # 이미 가공이 완료된 상태인지 확인
        if self.processed_file:
            QMessageBox.warning(self, "경고", "이미 이미지 가공이 완료되었습니다.\n새 이미지를 추가하려면 먼저 '사진 초기화' 버튼을 누르세요.")
            return

        self.selected_file = file_path
        print(f"선택된 파일: {file_path}")
        self.drop_area.label.setText(f"선택된 파일: {os.path.basename(file_path)}")

        # 폴더 번호 확인
        folder_number_text = self.folder_input.text().strip()
        if not folder_number_text or not folder_number_text.isdigit():
            # 유효한 폴더 번호가 없을 경우 알림
            print("유효한 폴더 번호를 먼저 입력해주세요.")
            self.drop_area.label.setText("폴더 번호를 먼저 입력해주세요!")
            self.drop_area.label.setStyleSheet("color: red;")
            QMessageBox.warning(self, "경고", "유효한 폴더 번호를 먼저 입력해주세요.")
            return

        # 미리보기 이미지 표시
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            # 미리보기 크기에 맞게 이미지 크기 조정
            preview_width = self.preview_frame.width() - 20  # 여백 고려
            preview_height = self.preview_frame.height() - 20  # 여백 고려
            pixmap = pixmap.scaled(preview_width, preview_height,
                                   Qt.KeepAspectRatio, Qt.SmoothTransformation)

            self.preview_label.setPixmap(pixmap)
            self.preview_label.setAlignment(Qt.AlignCenter)
            self.process_button.setEnabled(True)  # 가공하기 버튼 활성화

            # 성공 메시지 표시 (추가)
            self.status_message.setText("원본 이미지를 성공적으로 불러왔습니다.")
            self.status_message.setStyleSheet("color: #007700; margin: 10px 0px;")

            # 가공된 이미지 미리보기 초기화
            self.processed_label.setText("가공 후 미리보기")
            self.processed_label.setAlignment(Qt.AlignCenter)
            self.print_button.setEnabled(False)  # 인쇄 버튼 비활성화
        else:
            self.preview_label.setText("이미지를 불러올 수 없습니다")
            self.preview_label.setAlignment(Qt.AlignCenter)
            self.process_button.setEnabled(False)
            # 오류 메시지 표시
            self.status_message.setText("이미지를 불러오는데 실패했습니다.")
            self.status_message.setStyleSheet("color: #FF0000; margin: 10px 0px;")

    # process_selected_image 메서드에서 수정할 부분
    def process_selected_image(self):
        """가공하기 버튼을 눌렀을 때 실행되는 메서드"""
        if not self.selected_file:
            QMessageBox.warning(self, "경고", "먼저 이미지를 선택해주세요.")
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
            # 추가 시작 - 다른 레이블 초기화하고 생성된 폴더 메시지만 표시
            folder_name = os.path.basename(self.created_folder)
            self.folder_exists_label.setText(f"'{folder_name}' 폴더가 생성되었습니다.")
            self.folder_exists_label.setStyleSheet("color: green;")
            self.new_folder_label.setText("")
            self.last_folder_time_label.setText("")
            # 추가 끝

        processed_path = self.process_and_save(self.selected_file, self.created_folder)

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

                # 가공 완료 메시지 설정 (추가)
                folder_name = os.path.basename(self.created_folder)
                self.status_message.setText(f"가공이 성공적으로 완료되었습니다.\n'{folder_name}' 폴더에 저장되었습니다.")
                self.status_message.setStyleSheet("color: #007700; margin: 10px 0px;")
            else:
                self.processed_label.setText("가공된 이미지를 표시할 수 없습니다")
                # 실패 메시지 설정
                self.status_message.setText("가공된 이미지를 표시할 수 없습니다.")
                self.status_message.setStyleSheet("color: #FF0000; margin: 10px 0px;")
        else:
            self.processed_label.setText("가공된 이미지를 표시할 수 없습니다")
            # 실패 메시지 설정
            self.status_message.setText("이미지 가공에 실패했습니다.")
            self.status_message.setStyleSheet("color: #FF0000; margin: 10px 0px;")

        # 대신 파일 이름을 계속 표시하면서 녹색으로 강조
        file_name = os.path.basename(self.selected_file)
        self.drop_area.label.setText(f"선택된 파일: {file_name}")
        self.drop_area.label.setStyleSheet("color: green;")

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

    def process_and_save(self, file, folder_path):
        processed_image_path = None

        # 이전 파일이 있으면 삭제
        try:
            old_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            for old_file in old_files:
                # 이전 원본 복사본과 가공된 이미지 삭제
                if old_file.startswith("copy_") or old_file.startswith("processed_"):
                    old_file_path = os.path.join(folder_path, old_file)
                    os.remove(old_file_path)
                    print(f"이전 파일 삭제됨: {old_file_path}")
        except Exception as e:
            print(f"이전 파일 삭제 오류: {e}")
            # 삭제 실패해도 계속 진행

        # 이미지 가공 (이 함수 안에서 가공 방법을 선택할 수 있음)
        try:
            processed_image_path = self.process_image(file, folder_path)
            print(f"가공된 이미지 저장됨: {processed_image_path}")
        except Exception as e:
            print(f"이미지 가공 오류: {e}")
            QMessageBox.critical(self, "오류", f"이미지 가공 중 오류가 발생했습니다: {str(e)}")

        # 현재 파일 복사본 저장
        try:
            file_copy_path = os.path.join(folder_path, "copy_" + os.path.basename(file))
            shutil.copy(file, file_copy_path)
            print(f"파일 복사본 저장됨: {file_copy_path}")
        except Exception as e:
            print(f"파일 복사 오류: {e}")
            QMessageBox.critical(self, "오류", f"파일 복사 중 오류가 발생했습니다: {str(e)}")

        return processed_image_path

    def process_image(self, file, folder_path):
        # 이곳에 원하는 이미지 가공 코드를 추가하세요
        image = Image.open(file)
        processed_image = image.convert("L")  # 예시: 흑백 변환
        processed_image_path = os.path.join(folder_path, "processed_" + os.path.basename(file))
        processed_image.save(processed_image_path)
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

        # 폴더 입력 필드 다시 활성화 - 이 부분 추가
        self.folder_input.setEnabled(True)
        self.folder_input.setStyleSheet("")  # 원래 스타일로 복원

        self.folder_exists_label.setText("")
        self.new_folder_label.setText("")
        self.last_folder_time_label.setText("")

        self.drop_area.label.setText("여기에 사진을 드롭하세요")
        self.drop_area.label.setStyleSheet("color: #555;")

        self.preview_label.setText("이미지 미리보기")
        self.preview_label.setPixmap(QPixmap())

        self.processed_label.setText("가공 후 미리보기")
        self.processed_label.setPixmap(QPixmap())

        # 상태 메시지 초기화 (추가)
        self.status_message.setText("")

        # 버튼 상태 초기화
        self.process_button.setEnabled(False)
        self.print_button.setEnabled(False)

        # 내부 변수 초기화
        self.selected_file = None
        self.processed_file = None
        self.created_folder = None
        self.previous_folder_number = None
        self.is_first_check = True  # 첫 번째 체크 상태도 재설정

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