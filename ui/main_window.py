import sys
import os
import shutil
import datetime
import io
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                           QWidget, QFileDialog, QLineEdit, QLabel, QHBoxLayout,
                           QFrame, QSizePolicy, QSpacerItem, QMessageBox, QComboBox,
                           QDialog, QButtonGroup)
from PyQt5.QtGui import QFont, QDragEnterEvent, QDropEvent, QPixmap, QImage, QPainter, QColor
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PIL import Image as PILImage
from .drop_area import SingleDropArea, MultiDropArea
from .frame_manager import FrameManager
from .drop_area import SingleDropArea, MultiDropArea
from .frame_manager import FrameManager
from .settings_dialog import SettingsDialog
from .settings_manager import SettingsManager
from .styles import Styles, Colors, Fonts
from .message_box import MessageBox
from .status_card import StatusCard
from .toast_message import ToastMessage



class FolderManager:
    """폴더 관리 클래스: 이름 생성, 중복 확인, 생성"""
    
    def __init__(self, base_path=None):
        self.base_path = base_path or os.getcwd()
        self.created_folder = None
        self.previous_folder_number = None

    def get_actual_folder_name(self, folder_number_text):
        """실제 생성될 폴더 이름을 반환"""
        folder_name = folder_number_text
        folder_path = os.path.join(self.base_path, folder_name)

        if os.path.exists(folder_path):
            base_folder_name = folder_name
            existing_folders = [d for d in os.listdir(self.base_path)
                                if os.path.isdir(os.path.join(self.base_path, d)) and
                                d.startswith(base_folder_name + "_")]

            if existing_folders:
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
                folder_name = f"{base_folder_name}_1"

        return folder_name

    def create_folder(self, folder_name):
        """폴더 생성"""
        folder_path = os.path.join(self.base_path, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            self.created_folder = folder_path
            return True, folder_path, "created"
        else:
            self.created_folder = folder_path
            return True, folder_path, "existing"

    def check_availability(self, folder_number_text):
        """폴더 이름 가용성 확인"""
        if not folder_number_text:
            return None

        if not folder_number_text.isdigit():
            return {"status": "invalid", "message": "유효한 번호를 입력해주세요."}

        folder_name = str(folder_number_text)
        folder_path = os.path.join(self.base_path, folder_name)

        if os.path.exists(folder_path):
            folder_creation_time = os.path.getctime(folder_path)
            time_str = datetime.datetime.fromtimestamp(folder_creation_time).strftime('%Y-%m-%d %H:%M:%S')
            
            # 다음 가능한 이름 찾기
            actual_name = self.get_actual_folder_name(folder_name)
            
            return {
                "status": "exists",
                "message": "이미 있는 이름입니다.",
                "creation_time": time_str,
                "next_name": actual_name
            }
        else:
            return {
                "status": "available",
                "message": "새로운 이름입니다.",
                "next_name": folder_name
            }


class ImageProcessor:
    """이미지 처리 클래스: 가공 로직 연결"""
    
    def __init__(self):
        pass

    def process_images(self, files, frame_name, frame_manager, output_folder, expand_pixels=0):
        """이미지 가공 실행"""
        try:
            from processing import insert_images_into_frame
            
            base_name = os.path.basename(files[0]) if files[0] else "image.jpg"
            processed_image_path = os.path.join(output_folder, "processed_" + base_name)

            if frame_name == "none":
                if files[0]:
                    image = PILImage.open(files[0])
                    image.save(processed_image_path, quality=100)
                return processed_image_path

            frame_path = os.path.join(os.getcwd(), 'frame', frame_name)
            os.makedirs(os.path.dirname(frame_path), exist_ok=True)

            if not os.path.exists(frame_path):
                print(f"[WARNING] 프레임 이미지를 찾을 수 없음: {frame_path}")
                if files[0]:
                    shutil.copy(files[0], processed_image_path)
                return processed_image_path

            # FrameManager를 통해 영역 정보 가져오기
            # frame_name은 파일명(01.png)이므로, 이를 이용해 데이터를 찾음
            # FrameManager 구조상 get_frame_by_name은 '4컷 - 파란색' 같은 이름을 받음
            # 따라서 파일명으로 이름을 찾거나, 파일명으로 직접 데이터를 찾아야 함.
            # 여기서는 FrameManager의 get_all_frames를 순회하여 찾거나, MultiWindow에서 넘겨주는 방식 고려
            # 일단 MultiWindow에서 frame_data를 넘겨주는 것이 더 깔끔할 수 있으나,
            # 여기서는 frame_manager를 이용해 직접 찾도록 구현
            
            frames = frame_manager.get_all_frames()
            frame_data = next((f for f in frames if f['filename'] == frame_name), None)
            
            if frame_data:
                regions = frame_data.get('regions', [])
            else:
                regions = []

            photo_regions = []
            for i, file_path in enumerate(files):
                if file_path and os.path.exists(file_path):
                    if i < len(regions):
                        photo_regions.append((file_path, regions[i]))

            if photo_regions:
                insert_images_into_frame(photo_regions, frame_path, processed_image_path, expand_pixels=expand_pixels)
                return processed_image_path
            else:
                return None

        except Exception as e:
            print(f"[ERROR] 이미지 가공 중 오류: {e}")
            raise e


class PrintManager:
    """인쇄 관리 클래스"""
    
    def __init__(self):
        pass

    def print_image(self, image_path, parent_widget):
        """이미지 인쇄"""
        if not image_path or not os.path.exists(image_path):
            MessageBox.warning(parent_widget, "경고", "인쇄할 이미지가 없습니다.")
            return False

        try:
            # PIL을 통해 이미지 로드 시도
            pil_image = PILImage.open(image_path)
            qimage = ImageUtils.pil_to_qimage(pil_image)

            if qimage.isNull():
                qimage = QImage(image_path)

            if qimage.isNull():
                MessageBox.critical(parent_widget, "오류", "이미지를 인쇄용으로 로드할 수 없습니다.")
                return False

            # 프린터 설정
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.NativeFormat)

            print_dialog = QPrintDialog(printer, parent_widget)
            print_dialog.setWindowTitle("이미지 인쇄")

            if print_dialog.exec_() == QPrintDialog.Accepted:
                painter = QPainter()
                if painter.begin(printer):
                    rect = painter.viewport()
                    image_size = qimage.size()
                    image_size.scale(rect.size(), Qt.KeepAspectRatio)
                    painter.setViewport(rect.x(), rect.y(), image_size.width(), image_size.height())
                    painter.setWindow(qimage.rect())

                    painter.drawImage(0, 0, qimage)
                    painter.end()
                    return True
                else:
                    MessageBox.critical(parent_widget, "오류", "인쇄 작업을 시작할 수 없습니다.")
                    return False
            return False

        except Exception as e:
            print(f"[ERROR] 인쇄 중 오류: {e}")
            MessageBox.critical(parent_widget, "오류", f"인쇄 중 오류가 발생했습니다: {e}")
            return False


class ImageUtils:
    """이미지 변환 및 처리 유틸리티 클래스"""

    @staticmethod
    def pil_to_qpixmap(pil_image):
        """PIL 이미지를 QPixmap으로 변환"""
        try:
            if pil_image.mode == 'RGBA':
                background = PILImage.new('RGB', pil_image.size, (255, 255, 255))
                background.paste(pil_image, mask=pil_image.split()[-1])
                pil_image = background
            elif pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')

            byte_array = io.BytesIO()
            pil_image.save(byte_array, format='PNG')
            byte_array.seek(0)

            qimage = QImage()
            qimage.loadFromData(byte_array.getvalue())

            if qimage.isNull():
                print(f"[DEBUG] ImageUtils: QImage 변환 실패")
                return QPixmap()

            qpixmap = QPixmap.fromImage(qimage)
            print(f"[DEBUG] ImageUtils: PIL → QPixmap 변환 성공")
            return qpixmap

        except Exception as e:
            print(f"[DEBUG] ImageUtils: PIL → QPixmap 변환 오류: {e}")
            return QPixmap()

    @staticmethod
    def pil_to_qimage(pil_image):
        """PIL 이미지를 QImage로 변환"""
        try:
            if pil_image.mode == 'RGBA':
                background = PILImage.new('RGB', pil_image.size, (255, 255, 255))
                background.paste(pil_image, mask=pil_image.split()[-1])
                pil_image = background
            elif pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')

            byte_array = io.BytesIO()
            pil_image.save(byte_array, format='PNG')
            byte_array.seek(0)

            qimage = QImage()
            qimage.loadFromData(byte_array.getvalue())

            return qimage

        except Exception as e:
            print(f"[DEBUG] ImageUtils: PIL → QImage 변환 오류: {e}")
            return QImage()

    @staticmethod
    def load_and_resize_with_pil(image_path, target_width, target_height):
        """PIL을 통해 이미지를 로드하고 크기 조정"""
        try:
            print(f"[DEBUG] ImageUtils: PIL로 이미지 로드 시작: {image_path}")

            pil_image = PILImage.open(image_path)
            print(f"[DEBUG] ImageUtils: PIL 이미지 로드 성공, 원본 크기: {pil_image.size}")

            pil_image.thumbnail((target_width, target_height), PILImage.Resampling.LANCZOS)
            print(f"[DEBUG] ImageUtils: PIL 리사이즈 완료: {pil_image.size}")

            pixmap = ImageUtils.pil_to_qpixmap(pil_image)

            if pixmap.isNull():
                print(f"[DEBUG] ImageUtils: QPixmap 변환 실패")
                return None

            print(f"[DEBUG] ImageUtils: 최종 QPixmap 크기: {pixmap.width()}x{pixmap.height()}")
            return pixmap

        except Exception as e:
            print(f"[DEBUG] ImageUtils: 이미지 로드 오류: {e}")
            return None


class MultiWindow(QMainWindow):
    """Multi 모드 메인 윈도우 (4개 이미지 처리)"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bittara Photo")
        # 전체 윈도우 크기 증가 (가공된 이미지 박스가 잘리지 않도록)
        self.setGeometry(100, 100, 620, 780)  # 세로 크기 증가: 630 → 780

        # 추가: 첫 번째 체크 상태 관리 변수
        self.is_first_check = True

        # 종료 버튼 제거됨



        # 메인 레이아웃 설정
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)

        # 상단 컨트롤 행 (루트 폴더, 설정)
        top_control_layout = QHBoxLayout()
        
        top_control_layout.addStretch()  # 우측 정렬을 위해 왼쪽에 여백 추가
        
        # 루트 폴더 열기 버튼
        self.root_folder_btn = QPushButton("📁 루트 폴더 열기")
        self.root_folder_btn.setStyleSheet(Styles.BTN_SECONDARY)
        self.root_folder_btn.clicked.connect(self.open_root_folder)
        top_control_layout.addWidget(self.root_folder_btn)
        
        # 설정 버튼 (상단으로 이동)
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(32, 32)
        self.settings_btn.setStyleSheet(Styles.BTN_ICON)
        self.settings_btn.setToolTip("설정")
        self.settings_btn.clicked.connect(self.open_settings)
        top_control_layout.addWidget(self.settings_btn)
        
        main_layout.addLayout(top_control_layout)

        # 폴더 번호 입력을 위한 가로 레이아웃
        folder_container = QWidget()
        folder_layout = QHBoxLayout(folder_container)
        folder_layout.setContentsMargins(0, 0, 0, 0)

        # 폴더 번호 입력 라벨
        self.folder_label = QLabel("폴더 번호:")
        self.folder_label.setStyleSheet(Styles.LABEL_TITLE)
        folder_layout.addWidget(self.folder_label)

        # 폴더 번호 입력 필드
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("장부 번호를 입력하세요.")
        self.folder_input.setStyleSheet(Styles.INPUT)
        self.folder_input.textChanged.connect(self.check_folder_exists)
        folder_layout.addWidget(self.folder_input)
        
        # 폴더 열기 버튼 (입력창 옆)
        self.open_folder_btn = QPushButton("📂 폴더 열기")
        self.open_folder_btn.setStyleSheet(Styles.BTN_SECONDARY)
        self.open_folder_btn.clicked.connect(self.open_current_folder)
        self.open_folder_btn.setEnabled(False) # 초기에는 비활성화
        folder_layout.addWidget(self.open_folder_btn)

        main_layout.addWidget(folder_container)



        # 상태 카드 (Unified UI) - 폴더용 제거됨 (Toast로 대체)
        # self.folder_status_card = StatusCard()
        # main_layout.addWidget(self.folder_status_card)

        # 사이 공간 최소화
        main_layout.addSpacerItem(QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # 모드 선택 버튼 추가
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(10)

        mode_label = QLabel("모드 선택:")
        mode_label.setStyleSheet(Styles.LABEL_TITLE)
        mode_layout.addWidget(mode_label)

        # 모드 선택 버튼 그룹 설정 (상호 배타적 선택 보장)
        self.mode_group = QButtonGroup(self)
        self.mode_group.setExclusive(True)

        self.four_cut_button = QPushButton("네컷 모드")
        self.four_cut_button.setCheckable(True)
        self.four_cut_button.setChecked(True)  # 기본값: 네컷 모드
        self.four_cut_button.setStyleSheet(Styles.BTN_TOGGLE)
        self.four_cut_button.clicked.connect(self.select_four_cut_mode)
        self.mode_group.addButton(self.four_cut_button)
        mode_layout.addWidget(self.four_cut_button)

        self.single_cut_button = QPushButton("한컷 모드")
        self.single_cut_button.setCheckable(True)
        self.single_cut_button.setStyleSheet(Styles.BTN_TOGGLE)
        self.single_cut_button.clicked.connect(self.select_single_cut_mode)
        self.mode_group.addButton(self.single_cut_button)
        mode_layout.addWidget(self.single_cut_button)

        mode_layout.addStretch()
        main_layout.addLayout(mode_layout)

        # 드롭 영역을 위한 고정 컨테이너 생성
        self.drop_container = QWidget()
        self.drop_container.setFixedHeight(280)  # 240(DropArea) + 40(Button) = 280
        self.drop_container_layout = QVBoxLayout(self.drop_container)
        self.drop_container_layout.setContentsMargins(0, 0, 0, 0)
        self.drop_container_layout.setSpacing(0) # 간격 제거 (드롭 영역과 버튼 사이)

        # 초기 드롭 영역 설정 (Placeholder)
        self.drop_area = MultiDropArea(self)
        self.drop_container_layout.addWidget(self.drop_area)
        
        # 파일 선택 버튼 (고정)
        self.select_file_button = QPushButton("또는 파일 선택")
        self.select_file_button.setStyleSheet(Styles.BTN_SECONDARY)
        self.select_file_button.setFixedHeight(40)
        self.select_file_button.clicked.connect(self.select_image)
        self.drop_container_layout.addWidget(self.select_file_button)

        main_layout.addWidget(self.drop_container)

        # 상태 메시지 영역 (가공용)
        # 상태 메시지 영역 (가공용)
        self.processing_status_card = StatusCard()

        main_layout.addWidget(self.processing_status_card)

        # 가공된 이미지 미리보기 영역
        # 버튼 생성 (가공, 초기화, 새로 만들기)
        action_layout = QHBoxLayout()
        
        # 사진 초기화 버튼
        self.reset_image_button = QPushButton("사진 초기화")
        self.reset_image_button.setStyleSheet(Styles.BTN_ACCENT)
        self.reset_image_button.clicked.connect(self.reset_image)
        action_layout.addWidget(self.reset_image_button)

        # 가공하기 버튼
        self.process_button = QPushButton("가공하기")
        self.process_button.setStyleSheet(Styles.BTN_SUCCESS)
        self.process_button.setEnabled(False)
        self.process_button.clicked.connect(self.process_selected_image)
        action_layout.addWidget(self.process_button)

        # 새로 만들기 버튼
        self.reset_button = QPushButton("전체 초기화")
        self.reset_button.setStyleSheet(Styles.BTN_DESTRUCTIVE)
        self.reset_button.clicked.connect(self.reset_application)
        action_layout.addWidget(self.reset_button)
        
        main_layout.addLayout(action_layout)

        # 분할 레이아웃 (좌: 프레임 미리보기 / 우: 가공된 이미지)
        split_layout = QHBoxLayout()
        split_layout.setSpacing(15)

        # [좌측] 프레임 미리보기 및 선택
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 프레임 미리보기 프레임
        self.frame_preview_frame = QFrame()
        self.frame_preview_frame.setStyleSheet(Styles.PROCESSED_FRAME)
        frame_preview_layout = QVBoxLayout(self.frame_preview_frame)
        
        frame_title = QLabel("프레임 미리보기")
        frame_title.setAlignment(Qt.AlignCenter)
        frame_title.setStyleSheet(Styles.LABEL_TITLE)
        frame_preview_layout.addWidget(frame_title)
        
        self.frame_preview_label = QLabel("프레임 선택 대기")
        self.frame_preview_label.setAlignment(Qt.AlignCenter)
        self.frame_preview_label.setMinimumHeight(200)
        self.frame_preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        frame_preview_layout.addWidget(self.frame_preview_label, 0, Qt.AlignCenter)
        
        left_layout.addWidget(self.frame_preview_frame)
        
        # 프레임 선택 (미리보기 하단)
        frame_select_layout = QHBoxLayout()
        # frame_label = QLabel("프레임:")
        # frame_label.setStyleSheet(Styles.LABEL_TITLE)
        # frame_select_layout.addWidget(frame_label)

        self.frame_combo = QComboBox()
        self.frame_combo.setStyleSheet(Styles.INPUT)
        frame_select_layout.addWidget(self.frame_combo)

        # 설정 버튼 제거됨 (상단으로 이동)
        
        left_layout.addLayout(frame_select_layout)
        
        split_layout.addWidget(left_container, 1) # 비율 1

        # [우측] 가공된 이미지 및 인쇄
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # 가공된 이미지 프레임
        self.processed_frame = QFrame()
        self.processed_frame.setStyleSheet(Styles.PROCESSED_FRAME)
        processed_frame_layout = QVBoxLayout(self.processed_frame)
        
        processed_title = QLabel("가공된 이미지")
        processed_title.setAlignment(Qt.AlignCenter)
        processed_title.setStyleSheet(Styles.LABEL_TITLE)
        processed_frame_layout.addWidget(processed_title)

        self.processed_label = QLabel("이미지가 여기에 표시됩니다")
        self.processed_label.setAlignment(Qt.AlignCenter)
        self.processed_label.setStyleSheet(Styles.LABEL_SUBTITLE)
        self.processed_label.setMinimumHeight(200)
        self.processed_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        processed_frame_layout.addWidget(self.processed_label, 0, Qt.AlignCenter)
        
        right_layout.addWidget(self.processed_frame)
        
        # 인쇄 버튼 (이미지 하단)
        self.print_button = QPushButton("인쇄")
        self.print_button.setStyleSheet(Styles.BTN_PRIMARY)
        self.print_button.setEnabled(False)
        self.print_button.clicked.connect(self.print_image)
        right_layout.addWidget(self.print_button)

        split_layout.addWidget(right_container, 1) # 비율 1

        main_layout.addLayout(split_layout)

        # QWidget에 레이아웃 설정
        container = QWidget()
        container.setLayout(main_layout)

        # 창에 컨테이너 위젯을 설정
        self.setCentralWidget(container)

        # 선택된 파일들 초기화 (4개 파일을 저장할 리스트)
        self.selected_files = [None, None, None, None]
        self.processed_file = None
        self.created_folder = None

        # 선택된 프레임 변수 초기화
        self.selected_frame = "01.png"

        # 프레임 콤보박스 이벤트 연결
        self.frame_combo.currentIndexChanged.connect(self.on_frame_changed)

        # 모드 관련 변수 초기화
        self.current_mode = "four_cut"  # 기본값: 네컷 모드

        # 프레임 매니저 초기화 및 콤보박스 설정
        self.frame_manager = FrameManager()
        
        # 헬퍼 클래스 초기화
        self.folder_manager = FolderManager()
        self.image_processor = ImageProcessor()
        self.print_manager = PrintManager()
        self.settings_manager = SettingsManager()
        
        self.update_frame_combo()
        self.apply_aspect_ratio()
        self.update_print_button_ui()
        
        # 초기 상태 메시지 설정 (모든 초기화가 끝난 후 설정해야 덮어씌워지지 않음)
        self.processing_status_card.show_success("준비됨")

    def update_frame_combo(self, suppress_status=False):
        """프레임 콤보박스 목록 업데이트"""
        current_text = self.frame_combo.currentText()
        self.frame_combo.blockSignals(True)
        self.frame_combo.clear()
        
        frames = self.frame_manager.get_all_frames()
        for frame in frames:
            self.frame_combo.addItem(frame['name'], frame['filename'])
            
        self.frame_combo.addItem("프레임 없음", "none")
        
        # 이전 선택 복원 시도
        index = self.frame_combo.findText(current_text)
        if index >= 0:
            self.frame_combo.setCurrentIndex(index)
        else:
            self.frame_combo.setCurrentIndex(0)
            
        self.frame_combo.blockSignals(False)
        # 데이터 갱신을 위해 강제 호출
        self.on_frame_changed(self.frame_combo.currentIndex(), suppress_status)

    def open_settings(self):
        """설정 다이얼로그 열기"""
        dialog = SettingsDialog(self.frame_manager, self.settings_manager, self)
        dialog.exec_()
        self.update_frame_combo(suppress_status=True)
        self.update_print_button_ui()

    def open_root_folder(self):
        """루트 폴더(기본 저장 경로) 열기"""
        base_path = self.folder_manager.base_path
        if os.path.exists(base_path):
            os.startfile(base_path)
        else:
            ToastMessage.show_toast(self, "루트 폴더를 찾을 수 없습니다.", type="error", anchor_widget=self.root_folder_btn)

    def open_current_folder(self):
        """현재 작업 중인 폴더 열기"""
        if self.created_folder and os.path.exists(self.created_folder):
            os.startfile(self.created_folder)
        else:
            # 폴더가 아직 생성되지 않았거나 찾을 수 없는 경우
            folder_number_text = self.folder_input.text().strip()
            if folder_number_text:
                # 입력된 번호로 폴더 경로 추정
                potential_path = os.path.join(self.folder_manager.base_path, folder_number_text)
                if os.path.exists(potential_path):
                    os.startfile(potential_path)
                else:
                    ToastMessage.show_toast(self, "폴더가 존재하지 않습니다.", type="warning", anchor_widget=self.open_folder_btn)
            else:
                ToastMessage.show_toast(self, "폴더가 지정되지 않았습니다.", type="warning", anchor_widget=self.open_folder_btn)

    def select_four_cut_mode(self):
        """네컷 모드 선택"""
        # 버튼 상태 강제 유지 (토글 해제 방지)
        self.four_cut_button.setChecked(True)
        
        if self.current_mode == "four_cut":
            return

        # 기존 작업 확인
        if any(file is not None for file in self.selected_files) or self.processed_file:
            reply = MessageBox.question(self, '모드 변경 확인',
                                         "모드를 변경하면 현재 작업이 초기화됩니다.\n계속하시겠습니까?")
            if reply == MessageBox.No:
                # 버튼 상태 되돌리기 (QButtonGroup이 자동으로 처리하지만, 로직상 취소 시 복구 필요)
                self.single_cut_button.setChecked(True)
                return

        self.current_mode = "four_cut"

        # 드롭 영역 재구성
        self.setup_drop_area()

        # 작업 초기화
        self.reset_work_without_folder()

        print("[DEBUG] 네컷 모드로 변경됨")

    def select_single_cut_mode(self):
        """한컷 모드 선택"""
        # 버튼 상태 강제 유지 (토글 해제 방지)
        self.single_cut_button.setChecked(True)

        if self.current_mode == "single_cut":
            return

        # 기존 작업 확인
        if any(file is not None for file in self.selected_files) or self.processed_file:
            reply = MessageBox.question(self, '모드 변경 확인',
                                         "모드를 변경하면 현재 작업이 초기화됩니다.\n계속하시겠습니까?")
            if reply == MessageBox.No:
                # 버튼 상태 되돌리기
                self.four_cut_button.setChecked(True)
                return

        self.current_mode = "single_cut"

        # 드롭 영역 재구성
        self.setup_drop_area()

        # 작업 초기화
        self.reset_work_without_folder()

        print("[DEBUG] 한컷 모드로 변경됨")

    def setup_drop_area(self):
        """모드에 따른 드롭 영역 설정"""
        # 기존 드롭 영역 제거
        if hasattr(self, 'drop_area') and self.drop_area:
            self.drop_container_layout.removeWidget(self.drop_area)
            self.drop_area.setParent(None)
            self.drop_area.deleteLater()

        # 새 드롭 영역 생성
        if self.current_mode == "four_cut":
            self.drop_area = MultiDropArea(self)
            self.selected_files = [None, None, None, None]  # 4개 슬롯
        else:  # single_cut
            self.drop_area = SingleDropArea(self)
            self.selected_files = [None]  # 1개 슬롯

        # 컨테이너에 새 드롭 영역 추가 (버튼 위인 0번 인덱스에 삽입)
        self.drop_container_layout.insertWidget(0, self.drop_area)

        print(f"[DEBUG] 드롭 영역이 {self.current_mode} 모드로 교체됨")

    def reset_work_without_folder(self):
        """폴더 정보는 유지하고 작업만 초기화"""
        # 선택된 파일들과 가공된 파일 정보 초기화
        if self.current_mode == "four_cut":
            self.selected_files = [None, None, None, None]
        else:
            self.selected_files = [None]
        self.processed_file = None

        # 드롭 영역 초기화
        self.drop_area.reset_zones()

        # 가공된 이미지 초기화 (helper 사용)
        self.clear_processed_view()

        # 상태 메시지 초기화
        if not self.folder_input.isReadOnly():
            self.processing_status_card.show_success("준비됨")
        else:
            if self.current_mode == "four_cut":
                self.processing_status_card.show_info("이미지를 선택해주세요. (0/4)")
            else:
                self.processing_status_card.show_info("이미지를 선택해주세요.")

        # 버튼 상태 초기화
        self.process_button.setEnabled(False)
        self.print_button.setEnabled(False)
        
        # 폴더 열기 버튼 비활성화 (폴더가 확정되지 않은 상태로 간주하거나, 유지)
        # 여기서는 폴더 정보는 유지되므로 버튼 상태도 유지해야 함.
        # 하지만 reset_work_without_folder는 보통 모드 전환 시 호출되므로,
        # 폴더가 확정된 상태라면 버튼을 활성화 유지해야 함.
        if self.folder_input.isReadOnly():
            self.open_folder_btn.setEnabled(True)
        else:
            self.open_folder_btn.setEnabled(False)





    def apply_aspect_ratio(self):
        """설정된 비율에 따라 미리보기 영역 크기 조정"""
        ratio_str = self.settings_manager.get("preview_aspect_ratio", "3:2")
        
        # 비율 파싱
        try:
            w_ratio, h_ratio = map(int, ratio_str.split(":"))
        except:
            w_ratio, h_ratio = 3, 2
            
        # 기준 너비 (레이아웃에 따라 다를 수 있지만 대략적인 값 사용)
        base_width = 280
        target_height = int(base_width * (h_ratio / w_ratio))
        
        # 크기 고정 (흰 여백 제거를 위해 FixedSize 사용)
        # Expanding 정책이 있으면 레이아웃이 늘려버리므로 고정 크기로 변경
        self.frame_preview_label.setFixedSize(base_width, target_height)
        self.processed_label.setFixedSize(base_width, target_height)
        
        # 현재 표시된 이미지도 업데이트
        self.update_frame_preview()
        if self.processed_file:
            # 가공된 이미지가 있으면 다시 로드 (비율에 맞춰)
            self.load_processed_preview()

    def update_frame_preview(self):
        """선택된 프레임 미리보기 업데이트"""
        if not hasattr(self, 'frame_preview_label'):
            return

        if self.selected_frame == "none" or not self.selected_frame:
            self.frame_preview_label.setText("프레임 없음")
            self.frame_preview_label.setPixmap(QPixmap())
            return

        frame_path = os.path.join(os.getcwd(), 'frame', self.selected_frame)
        if not os.path.exists(frame_path):
            self.frame_preview_label.setText("프레임 파일 없음")
            return

        pixmap = QPixmap(frame_path)
        if not pixmap.isNull():
            # 미리보기 크기 제한 (너비 기준)
            target_width = 280
            
            # 비율 설정 가져오기
            ratio_str = self.settings_manager.get("preview_aspect_ratio", "3:2")
            try:
                w_ratio, h_ratio = map(int, ratio_str.split(":"))
            except:
                w_ratio, h_ratio = 3, 2
                
            target_height = int(target_width * (h_ratio / w_ratio))
            
            # Scaled to height as well to enforce ratio if needed, 
            # but usually we just scale to width and let height adjust or crop?
            # User said "rendering ratio", implying the container shape.
            # We should scale the image to fit within the target box while keeping aspect ratio,
            # or fill it? Usually "preview" implies seeing the whole thing.
            # But if the frame itself is not 3:2, forcing it might distort it.
            # However, the user said "Frames are mostly 3:2".
            # So we just scale to width, and the height will naturally follow if the image is 3:2.
            # If the image is NOT 3:2, we should probably still fit it in the box.
            
            pixmap = pixmap.scaled(target_width, target_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.frame_preview_label.setPixmap(pixmap)
        else:
            self.frame_preview_label.setText("이미지 로드 실패")

    def on_frame_changed(self, index, suppress_status=False):
        """프레임 선택이 변경되었을 때 호출"""
        self.selected_frame = self.frame_combo.currentData()
        print(f"선택된 프레임: {self.selected_frame}")
        
        self.update_frame_preview()
        
        # 상태 메시지 업데이트 억제 (설정 변경 시 등)
        if suppress_status:
            return

        # 프레임 변경 시 가공된 이미지 초기화
        self.clear_processed_view()

        if any(file is not None for file in self.selected_files):
            if all(file is not None for file in self.selected_files):
                self.process_button.setEnabled(True)
                self.processing_status_card.show_info("새로운 프레임이 선택되었습니다. 가공하기 버튼을 눌러 이미지를 재가공하세요.")
            else:
                filled_count = sum(1 for file in self.selected_files if file is not None)
                self.processing_status_card.show_info(f"새로운 프레임이 선택되었습니다. {filled_count}/4개 이미지가 준비되었습니다.")
                self.process_button.setEnabled(False)

    def keyPressEvent(self, event):
        """키 이벤트 처리"""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            focused_widget = QApplication.focusWidget()
            if focused_widget == self.folder_input and not self.folder_input.text().strip() == "":
                folder_number_text = self.folder_input.text().strip()
                
                # 가용성 체크를 먼저 수행하여 올바른 이름을 가져옴
                check_result = self.folder_manager.check_availability(folder_number_text)
                
                if check_result and check_result['status'] != 'invalid':
                    actual_folder_name = check_result['next_name']
                    
                    reply = MessageBox.question(self, '폴더 번호 확인',
                                                 f"폴더 이름을 '{actual_folder_name}'로 설정하시겠습니까?\n설정 후에는 변경할 수 없습니다.")
                    if reply == MessageBox.Yes:
                        self.folder_input.setReadOnly(True) # setEnabled(False) 대신 setReadOnly(True) 사용
                        self.folder_input.setText(actual_folder_name) # 실제 생성된 폴더 이름으로 업데이트
                        # 스타일 강제 업데이트 (readOnly 상태 반영을 위해)
                        self.folder_input.setStyleSheet(Styles.INPUT)
                        
                        self.create_folder(actual_folder_name)
                    else:
                        self.folder_input.clear()
                        # self.folder_status_card.clear()
        super().keyPressEvent(event)


    def create_folder(self, folder_name):
        """폴더를 즉시 생성하는 메서드"""
        success, folder_path, status = self.folder_manager.create_folder(folder_name)
        if success:
            self.created_folder = folder_path
            if status == "created":
                ToastMessage.show_toast(self, f"'{folder_name}' 폴더가 생성되었습니다.", type="success", anchor_widget=self.folder_input, center_x=True, position="top")
                print(f"폴더 생성됨: {folder_path}")
            else: # existing
                ToastMessage.show_toast(self, f"'{folder_name}' 폴더를 사용합니다.", type="success", anchor_widget=self.folder_input, center_x=True, position="top")
            
            # 폴더 열기 버튼 활성화
            self.open_folder_btn.setEnabled(True)
            
            # 폴더 생성/확인 후 이미지 선택 안내
            if self.current_mode == "four_cut":
                self.processing_status_card.show_info("이미지를 선택해주세요. (0/4)")
            else:
                self.processing_status_card.show_info("이미지를 선택해주세요.")
        else:
            # FolderManager.create_folder는 현재 실패 케이스가 없지만(예외 발생 시 crash), 
            # 추후 확장을 위해 남겨둠. 실제로는 try-except가 FolderManager 내부에 없으므로 
            # 여기서 에러 처리를 하거나 FolderManager를 보강해야 함.
            # 현재 구현상 FolderManager는 에러를 raise할 것임.
            pass

    def check_folder_exists(self):
        """폴더 이름 입력 시 실시간 피드백"""
        folder_number_text = self.folder_input.text().strip()

        if not folder_number_text:
            # self.folder_status_card.clear()
            return
            
        # FolderManager를 통해 상태 확인
        result = self.folder_manager.check_availability(folder_number_text)
        
        if not result:
             # self.folder_status_card.clear()
             return

        if result['status'] == 'invalid':
            ToastMessage.show_toast(self, result['message'], type="error", anchor_widget=self.folder_input, center_x=True, position="top")
            
        elif result['status'] == 'exists':
            msg = f"'{folder_number_text}' 폴더가 이미 존재합니다. (엔터: '{result['next_name']}' 생성)"
            ToastMessage.show_toast(self, msg, type="warning", anchor_widget=self.folder_input, duration=4000, center_x=True, position="top")
            
        elif result['status'] == 'available':
            msg = f"새로운 폴더입니다. (엔터: '{folder_number_text}' 생성)"
            ToastMessage.show_toast(self, msg, type="info", anchor_widget=self.folder_input, center_x=True, position="top")
            
            self.previous_folder_number = folder_number_text

    def prepare_image(self, file_path, slot_index):
        """이미지를 준비하고 상태 업데이트 - 모드별 처리"""
        print(f"[DEBUG] prepare_image 호출됨: 파일={file_path}, 슬롯={slot_index}, 모드={self.current_mode}")

        # 가공 상태 확인 - 이미 가공된 상태라면 초기화 후 진행
        if self.processed_file:
            print(f"[DEBUG] prepare_image: 기존 가공 이미지 초기화")
            self.clear_processed_view()

        # 폴더 번호 확인 및 생성
        folder_number_text = self.folder_input.text().strip()
        if not folder_number_text:
            print(f"[DEBUG] prepare_image: 폴더 번호가 비어있음")
            return

        # 폴더가 없으면 생성 (또는 확인)
        if not self.created_folder or not os.path.exists(self.created_folder):
            actual_folder_name = self.folder_manager.get_actual_folder_name(folder_number_text)
            self.create_folder(actual_folder_name)

        # 파일 즉시 복사
        try:
            base_name = os.path.basename(file_path)
            copy_filename = f"copy{slot_index + 1}_{base_name}"
            target_path = os.path.join(self.created_folder, copy_filename)
            
            # 기존에 같은 슬롯에 파일이 있었다면 삭제 (덮어쓰기 전 정리)
            # 하지만 슬롯 인덱스로 관리되므로 덮어쓰기가 됨.
            # 다만 이름이 다를 수 있으므로, 기존 슬롯의 파일을 확인해서 삭제해야 함.
            # self.selected_files[slot_index]에 이전 파일 경로가 있다면 삭제
            if self.current_mode == "four_cut":
                if 0 <= slot_index < 4 and self.selected_files[slot_index]:
                    if os.path.exists(self.selected_files[slot_index]):
                        try:
                            os.remove(self.selected_files[slot_index])
                            print(f"[DEBUG] 이전 파일 삭제됨: {self.selected_files[slot_index]}")
                        except Exception as e:
                            print(f"[ERROR] 이전 파일 삭제 실패: {e}")
            else:
                 if slot_index == 0 and self.selected_files[0]:
                    if os.path.exists(self.selected_files[0]):
                        try:
                            os.remove(self.selected_files[0])
                            print(f"[DEBUG] 이전 파일 삭제됨: {self.selected_files[0]}")
                        except Exception as e:
                            print(f"[ERROR] 이전 파일 삭제 실패: {e}")

            shutil.copy(file_path, target_path)
            print(f"[DEBUG] 파일 복사됨: {target_path}")
            
            # 저장할 경로는 복사된 파일의 경로
            final_path = target_path

        except Exception as e:
            print(f"[ERROR] 파일 복사 실패: {e}")
            MessageBox.critical(self, "오류", f"파일 복사 중 오류가 발생했습니다: {e}")
            return

        # 파일 경로 저장 (슬롯 인덱스 검증)
        if self.current_mode == "four_cut":
            if 0 <= slot_index < 4:
                self.selected_files[slot_index] = final_path
                max_files = 4
            else:
                print(f"[DEBUG] prepare_image: 잘못된 슬롯 인덱스 (네컷): {slot_index}")
                return
        else:  # single_cut
            if slot_index == 0:
                self.selected_files[0] = final_path
                max_files = 1
            else:
                print(f"[DEBUG] prepare_image: 잘못된 슬롯 인덱스 (한컷): {slot_index}")
                return

        print(f"[DEBUG] prepare_image: 슬롯 {slot_index + 1}에 파일 저장됨")

        # 상태 업데이트
        filled_count = sum(1 for file in self.selected_files if file is not None)
        print(f"[DEBUG] prepare_image: 채워진 슬롯 수: {filled_count}/{max_files}")

        if all(file is not None for file in self.selected_files):
            self.process_button.setEnabled(True)
            if self.current_mode == "four_cut":
                self.processing_status_card.show_success("4개 이미지가 모두 준비되었습니다. 가공하기 버튼을 누르세요.")
            else:
                self.processing_status_card.show_success("이미지가 준비되었습니다. 가공하기 버튼을 누르세요.")
        else:
            if self.current_mode == "four_cut":
                self.processing_status_card.show_info(f"{filled_count}/4개 이미지가 준비되었습니다.")
            else:
                self.processing_status_card.show_info("이미지를 선택해주세요.")
            self.process_button.setEnabled(False)

        print(f"[DEBUG] prepare_image 완료")

    def remove_image(self, slot_index):
        """이미지 삭제 처리"""
        print(f"[DEBUG] remove_image 호출됨: 슬롯={slot_index}")
        
        if 0 <= slot_index < len(self.selected_files):
            # 파일 삭제 로직 추가
            file_path = self.selected_files[slot_index]
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"[DEBUG] 파일 삭제됨: {file_path}")
                except Exception as e:
                    print(f"[ERROR] 파일 삭제 실패: {e}")

            self.selected_files[slot_index] = None
            
            # 상태 업데이트
            filled_count = sum(1 for file in self.selected_files if file is not None)
            max_files = 4 if self.current_mode == "four_cut" else 1
            
            print(f"[DEBUG] remove_image: 남은 파일 수: {filled_count}/{max_files}")
            
            # 상태 메시지 업데이트
            if self.current_mode == "four_cut":
                self.processing_status_card.show_info(f"{filled_count}/4개 이미지가 준비되었습니다.")
            else:
                self.processing_status_card.show_info("이미지를 선택해주세요.")
                
            # 버튼 비활성화
            # 버튼 비활성화
            self.process_button.setEnabled(False)
            
            # 가공된 이미지 초기화
            self.clear_processed_view()

    def clear_processed_view(self):
        """가공된 이미지 뷰 초기화"""
        self.processed_file = None
        self.processed_label.setText("가공 후 미리보기")
        self.processed_label.setPixmap(QPixmap())
        self.print_button.setEnabled(False)
        self.processing_status_card.show_info("이미지가 변경되었습니다. 다시 가공해주세요.")

    def select_image(self):
        """파일 선택 버튼 - 모드별 처리"""
        print(f"[DEBUG] select_image 호출됨, 모드: {self.current_mode}")

        # 가공 상태 확인
        if self.processed_file:
            ToastMessage.show_toast(self, "이미 가공이 완료되었습니다. '사진 초기화'를 먼저 해주세요.", type="warning", anchor_widget=self.select_file_button)
            return

        # 폴더 번호 검증
        folder_number_text = self.folder_input.text().strip()
        if not folder_number_text:
            ToastMessage.show_toast(self, "폴더 번호를 먼저 입력해주세요.", type="warning", anchor_widget=self.folder_input, center_x=True)
            return

        # 파일 선택 다이얼로그
        if self.current_mode == "four_cut":
            files, _ = QFileDialog.getOpenFileNames(self, "Select Images (최대 4개)", "",
                                                    "Image Files (*.png *.jpg *.jpeg *.bmp)")
            max_files = 4
        else:  # single_cut
            files, _ = QFileDialog.getOpenFileNames(self, "Select Image (1개)", "",
                                                    "Image Files (*.png *.jpg *.jpeg *.bmp)")
            max_files = 1

        if files:
            files = files[:max_files]  # 최대 개수만큼만 처리
            print(f"[DEBUG] select_image: {len(files)}개 파일 선택됨")

            # 각 파일을 순서대로 슬롯에 배치
            for i, file_path in enumerate(files):
                self.prepare_image(file_path, i)
                self.drop_area.set_image_to_zone(i, file_path)
        else:
            print(f"[DEBUG] select_image: 파일 선택 취소됨")

    def process_selected_image(self):
        """가공하기 버튼 - 모드별 처리"""
        # 모드별 파일 확인
        if self.current_mode == "four_cut":
            if not all(file is not None for file in self.selected_files):
                ToastMessage.show_toast(self, "4개 이미지를 모두 선택해주세요.", type="warning", anchor_widget=self.process_button)
                return
        else:  # single_cut
            if not self.selected_files[0]:
                ToastMessage.show_toast(self, "이미지를 선택해주세요.", type="warning", anchor_widget=self.process_button)
                return

        folder_number_text = self.folder_input.text().strip()
        if not folder_number_text:
            ToastMessage.show_toast(self, "폴더 번호를 입력해주세요.", type="warning", anchor_widget=self.folder_input, center_x=True)
            return

        if not self.folder_input.isReadOnly():
            reply = MessageBox.question(self, '폴더 번호 확인',
                                         f"폴더 번호를 '{folder_number_text}'로 설정하시겠습니까?\n설정 후에는 변경할 수 없습니다.")

            if reply == MessageBox.Yes:
                # 실제 폴더 이름 확인 (중복 시 _a 등 붙은 이름)
                actual_folder_name = self.folder_manager.get_actual_folder_name(folder_number_text)
                self.folder_input.setText(actual_folder_name)
                self.folder_input.setReadOnly(True)
            else:
                return

        if not self.created_folder or not os.path.exists(self.created_folder):
            actual_folder_name = self.folder_manager.get_actual_folder_name(folder_number_text)
            self.create_folder(actual_folder_name)
            folder_name = os.path.basename(self.created_folder)
            
            folder_name = os.path.basename(self.created_folder)
            
            ToastMessage.show_toast(self, f"'{folder_name}' 폴더가 생성되었습니다.", type="success", anchor_widget=self.folder_input, center_x=True, position="top")

        processed_path = self.process_and_save(self.selected_files, self.created_folder)

        # 가공된 이미지 미리보기 표시
        if processed_path and os.path.exists(processed_path):
            print(f"[DEBUG] 가공된 이미지 로드 시작: {processed_path}")
            self.processed_file = processed_path
            
            self.load_processed_preview()
            
            if self.processed_label.pixmap() and not self.processed_label.pixmap().isNull():
                folder_name = os.path.basename(self.created_folder)
                frame_name = self.frame_combo.currentText()
                self.processing_status_card.show_success(f"{frame_name}로 가공이 성공적으로 완료되었습니다.\n'{folder_name}' 폴더에 저장되었습니다.")
            else:
                self.processing_status_card.show_error("가공된 이미지를 표시할 수 없습니다.")
        else:
            print(f"[DEBUG] 가공된 이미지 파일이 존재하지 않음: {processed_path}")
            self.processed_label.setText("가공된 이미지를 표시할 수 없습니다")
            self.processing_status_card.show_error("이미지 가공에 실패했습니다.")

        self.process_button.setEnabled(False)

    def load_processed_preview(self):
        """가공된 이미지 미리보기 로드 (비율 적용)"""
        if not self.processed_file or not os.path.exists(self.processed_file):
            return

        # 비율 설정 가져오기
        ratio_str = self.settings_manager.get("preview_aspect_ratio", "3:2")
        try:
            w_ratio, h_ratio = map(int, ratio_str.split(":"))
        except:
            w_ratio, h_ratio = 3, 2
            
        target_width = 280
        target_height = int(target_width * (h_ratio / w_ratio))
        
        print(f"[DEBUG] 가공된 이미지 미리보기 크기: {target_width}x{target_height}")

        pixmap = ImageUtils.load_and_resize_with_pil(self.processed_file, target_width, target_height)

        if pixmap and not pixmap.isNull():
            self.processed_label.setPixmap(pixmap)
            self.processed_label.setAlignment(Qt.AlignCenter)
            self.print_button.setEnabled(True)
        else:
            self.processed_label.setText("가공된 이미지를 표시할 수 없습니다")

    def process_and_save(self, files, folder_path):
        processed_image_path = None

        # 기존 가공된 파일 삭제 (새로 가공하므로)
        try:
            old_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            for old_file in old_files:
                if old_file.startswith("processed_"):
                    old_file_path = os.path.join(folder_path, old_file)
                    os.remove(old_file_path)
                    print(f"이전 가공 파일 삭제됨: {old_file_path}")
        except Exception as e:
            print(f"파일 삭제 오류: {e}")

        try:
            processed_image_path = self.process_image(files, folder_path)
            if processed_image_path:
                print(f"가공된 이미지 저장됨: {processed_image_path}")
        except Exception as e:
            print(f"이미지 가공 오류: {e}")
            MessageBox.critical(self, "오류", f"이미지 가공 중 오류가 발생했습니다: {str(e)}")

        # 파일 복사 로직 제거 (prepare_image에서 이미 수행됨)

        return processed_image_path

    def process_image(self, files, folder_path):
        try:
            # 합성 영역 확장 설정 가져오기
            expand_pixels = self.settings_manager.get("expand_pixels", 0)

            processed_path = self.image_processor.process_images(
                files, 
                self.selected_frame, 
                self.frame_manager, 
                folder_path,
                expand_pixels=expand_pixels
            )
            
            if processed_path:
                if self.selected_frame != "none":
                    self.processing_status_card.show_success(f"이미지가 '{self.selected_frame}' 프레임으로 가공되었습니다.")
                return processed_path
            else:
                MessageBox.warning(self, "경고", "처리할 이미지가 없습니다.")
                return None

        except Exception as e:
            error_msg = f"이미지 가공 중 오류가 발생했습니다: {str(e)}"
            print(error_msg)
            MessageBox.critical(self, "오류", error_msg)
            
            # 오류 발생 시 원본 복사 시도 (기존 로직 유지)
            base_name = os.path.basename(files[0]) if files[0] else "image.jpg"
            processed_image_path = os.path.join(folder_path, "processed_" + base_name)
            if files[0]:
                shutil.copy(files[0], processed_image_path)
            
            self.processing_status_card.show_error("오류로 인해 원본 이미지가 그대로 사용되었습니다.")
            return processed_image_path

    def print_image(self):
        """인쇄 기능 - 설정에 따라 분기"""
        if not self.processed_file:
            MessageBox.warning(self, "경고", "인쇄할 이미지가 없습니다. 먼저 이미지를 가공해주세요.")
            return

        direct_print = self.settings_manager.get("direct_print", True)

        if direct_print:
            print(f"[DEBUG] 인쇄 요청: {self.processed_file}")
            success = self.print_manager.print_image(self.processed_file, self)
            
            if success:
                MessageBox.information(self, "성공", "이미지 인쇄가 시작되었습니다.")
                print(f"[DEBUG] 인쇄 작업 시작됨")
        else:
            # 사진 보기 (기본 뷰어 실행)
            if os.path.exists(self.processed_file):
                os.startfile(self.processed_file)
            else:
                MessageBox.warning(self, "오류", "파일을 찾을 수 없습니다.")

    def update_print_button_ui(self):
        """설정에 따라 인쇄 버튼 UI 업데이트"""
        direct_print = self.settings_manager.get("direct_print", True)
        if direct_print:
            self.print_button.setText("🖨 인쇄")
            self.print_button.setStyleSheet(Styles.BTN_PRIMARY)
        else:
            self.print_button.setText("👁 사진 보기")
            self.print_button.setStyleSheet(Styles.BTN_SECONDARY)



    def reset_processed_state(self):
        """설정 변경 등으로 인해 가공된 상태를 초기화"""
        self.processed_file = None
        self.processed_label.clear()
        self.processed_label.setText("이미지를 추가하고 가공해주세요")
        self.print_button.setEnabled(False)
        self.processing_status_card.show_info("설정이 변경되었습니다. 다시 가공해주세요.")
        
        # 가공 버튼 상태 업데이트 (이미지가 모두 준비되어 있다면 활성화)
        if self.current_mode == "four_cut":
            if all(file is not None for file in self.selected_files):
                self.process_button.setEnabled(True)
        else: # single_cut
            if self.selected_files[0] is not None:
                self.process_button.setEnabled(True)

    def reset_image(self):
        """사진 초기화 버튼을 눌렀을 때 실행되는 메서드"""
        if not any(file is not None for file in self.selected_files):
            return

        reply = MessageBox.question(self, '사진 초기화 확인',
                                     "현재 선택된 사진들을 초기화하시겠습니까?")

        if reply == MessageBox.No:
            return

        if self.created_folder and os.path.exists(self.created_folder):
            try:
                files = os.listdir(self.created_folder)
                for file in files:
                    if file.startswith("copy") or file.startswith("processed_"):
                        file_path = os.path.join(self.created_folder, file)
                        os.remove(file_path)
                        print(f"파일 삭제됨: {file_path}")
            except Exception as e:
                print(f"파일 삭제 오류: {e}")

        # 선택된 파일들과 가공된 파일 정보 초기화
        self.selected_files = [None, None, None, None]
        self.processed_file = None

        # 드롭 영역 초기화
        self.drop_area.reset_zones()

        # 가공된 이미지 미리보기 초기화
        self.processed_label.setText("가공 후 미리보기")
        self.processed_label.setPixmap(QPixmap())

        # 상태 메시지 초기화
        if self.current_mode == "four_cut":
            self.processing_status_card.show_info("이미지를 선택해주세요. (0/4)")
        else:
            self.processing_status_card.show_info("이미지를 선택해주세요.")

        # 버튼 상태 초기화
        self.process_button.setEnabled(False)
        self.print_button.setEnabled(False)
        self.open_folder_btn.setEnabled(False) # 폴더 열기 버튼 비활성화

        print("사진들이 초기화되었습니다.")
        MessageBox.information(self, "알림", "사진들이 초기화되었습니다.")

    def reset_work_without_folder(self):
        """폴더 정보는 유지하고 작업만 초기화"""
        # 파일 정리 (copy 및 processed 파일 삭제)
        if self.created_folder and os.path.exists(self.created_folder):
            try:
                files = os.listdir(self.created_folder)
                for file in files:
                    if file.startswith("copy") or file.startswith("processed_"):
                        file_path = os.path.join(self.created_folder, file)
                        os.remove(file_path)
                        print(f"파일 삭제됨: {file_path}")
            except Exception as e:
                print(f"파일 삭제 오류: {e}")

        # 선택된 파일들과 가공된 파일 정보 초기화
        if self.current_mode == "four_cut":
            self.selected_files = [None, None, None, None]
        else:
            self.selected_files = [None]
        self.processed_file = None

        # 드롭 영역 초기화
        self.drop_area.reset_zones()

        # 가공된 이미지 초기화 (helper 사용)
        self.clear_processed_view()

        # 상태 메시지 초기화
        if not self.folder_input.isReadOnly():
             # 폴더가 아직 확정되지 않은 경우
             self.processing_status_card.show_info("폴더 번호를 입력해주세요.")
        else:
            if self.current_mode == "four_cut":
                self.processing_status_card.show_info("이미지를 선택해주세요. (0/4)")
            else:
                self.processing_status_card.show_info("이미지를 선택해주세요.")

        # 버튼 상태 초기화
        self.process_button.setEnabled(False)
        self.print_button.setEnabled(False)
        
        # 폴더 열기 버튼 비활성화 (폴더가 확정되지 않은 상태로 간주하거나, 유지)
        if self.folder_input.isReadOnly():
            self.open_folder_btn.setEnabled(True)
        else:
            self.open_folder_btn.setEnabled(False)

    def reset_application(self):
        """초기화 버튼을 눌렀을 때 실행되는 메서드"""
        reply = MessageBox.question(self, '초기화 확인',
                                     "정말로 현재 작업을 초기화하시겠습니까?\n생성된 폴더와 파일은 삭제되지 않습니다.")

        if reply == MessageBox.No:
            return

        # UI 초기화
        self.folder_input.clear()

        # 폴더 입력 필드 다시 활성화
        # 폴더 입력 필드 다시 활성화
        self.folder_input.setReadOnly(False)
        self.folder_input.setStyleSheet(Styles.INPUT)

        self.folder_input.setStyleSheet(Styles.INPUT)

        # self.folder_status_card.clear()

        # 모드를 네컷으로 초기화
        self.current_mode = "four_cut"
        self.four_cut_button.setChecked(True)
        self.single_cut_button.setChecked(False)

        # 드롭 영역 재설정
        self.setup_drop_area()

        # 가공된 이미지 미리보기 초기화
        self.processed_label.setText("가공 후 미리보기")
        self.processed_label.setPixmap(QPixmap())

        # 상태 메시지 초기화
        self.processing_status_card.show_success("준비됨")

        # 버튼 상태 초기화
        self.process_button.setEnabled(False)
        self.print_button.setEnabled(False)

        # 내부 변수 초기화
        self.selected_files = [None, None, None, None]  # 네컷 모드 기본값
        self.processed_file = None
        self.created_folder = None
        self.previous_folder_number = None
        self.is_first_check = True

        # 프레임 선택 초기화
        self.frame_combo.setCurrentIndex(0)
        self.selected_frame = "01.png"

        print("애플리케이션이 초기화되었습니다.")
        MessageBox.information(self, "알림", "모든 작업이 초기화되었습니다.")

    def close_application(self):
        reply = MessageBox.question(self, '종료 확인',
                                     "정말로 종료하시겠습니까?")

        if reply == MessageBox.Yes:
            QApplication.quit()
