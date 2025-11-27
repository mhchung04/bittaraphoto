import sys
import os
import shutil
import datetime
import io
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                           QWidget, QFileDialog, QLineEdit, QLabel, QHBoxLayout,
                           QFrame, QSizePolicy, QSpacerItem, QMessageBox, QComboBox,
                           QDialog)
from PyQt5.QtGui import QFont, QDragEnterEvent, QDropEvent, QPixmap, QImage, QPainter, QColor
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PIL import Image as PILImage
from .drop_area import SingleDropArea, MultiDropArea
from .frame_manager import FrameManager
from .drop_area import SingleDropArea, MultiDropArea
from .frame_manager import FrameManager
from .settings_dialog import SettingsDialog
from .styles import Styles, Colors, Fonts
from .message_box import MessageBox
from .status_card import StatusCard



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

    def process_images(self, files, frame_name, frame_manager, output_folder):
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
                insert_images_into_frame(photo_regions, frame_path, processed_image_path)
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

        self.setWindowTitle("사진 선택 및 인쇄 - Multi Mode (4개 이미지)")
        # 전체 윈도우 크기 증가 (가공된 이미지 박스가 잘리지 않도록)
        self.setGeometry(100, 100, 620, 780)  # 세로 크기 증가: 630 → 780

        # 추가: 첫 번째 체크 상태 관리 변수
        self.is_first_check = True

        # 종료 버튼 제거됨



        # 메인 레이아웃 설정
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)

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
        self.folder_input.setPlaceholderText("예: 20231025")
        self.folder_input.setStyleSheet(Styles.INPUT)
        self.folder_input.textChanged.connect(self.check_folder_exists)
        folder_layout.addWidget(self.folder_input)

        main_layout.addWidget(folder_container)

        # 상태 카드 (Unified UI) - 폴더용
        self.folder_status_card = StatusCard()
        main_layout.addWidget(self.folder_status_card)

        # 사이 공간 최소화
        main_layout.addSpacerItem(QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # 모드 선택 버튼 추가
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(10)

        mode_label = QLabel("모드 선택:")
        mode_label.setFont(QFont("Malgun Gothic", 14, QFont.Bold))
        mode_layout.addWidget(mode_label)

        self.four_cut_button = QPushButton("네컷 모드")
        self.four_cut_button.setFixedSize(120, 40)
        self.four_cut_button.setCheckable(True)
        self.four_cut_button.setChecked(True)  # 기본값: 네컷 모드
        self.four_cut_button.setStyleSheet(Styles.BTN_TOGGLE)
        self.four_cut_button.clicked.connect(self.select_four_cut_mode)
        mode_layout.addWidget(self.four_cut_button)

        self.single_cut_button = QPushButton("한컷 모드")
        self.single_cut_button.setFixedSize(120, 40)
        self.single_cut_button.setCheckable(True)
        self.single_cut_button.setStyleSheet(Styles.BTN_TOGGLE)
        self.single_cut_button.clicked.connect(self.select_single_cut_mode)
        mode_layout.addWidget(self.single_cut_button)

        mode_layout.addStretch()
        main_layout.addLayout(mode_layout)

        # 드롭 영역을 위한 고정 컨테이너 생성
        self.drop_container = QWidget()
        self.drop_container.setFixedHeight(270)  # 고정 높이 설정으로 모드 전환 시 UI 안정성 확보
        self.drop_container_layout = QVBoxLayout(self.drop_container)
        self.drop_container_layout.setContentsMargins(0, 0, 0, 0)

        # 초기 드롭 영역 설정
        self.drop_area = MultiDropArea(self)
        self.drop_area.select_btn.clicked.connect(self.select_image)
        self.drop_container_layout.addWidget(self.drop_area)

        main_layout.addWidget(self.drop_container)

        # 상태 메시지 영역 (가공용)
        self.processing_status_card = StatusCard()
        self.processing_status_card.show_success("준비됨") # 초기 상태
        main_layout.addWidget(self.processing_status_card)

        # 가공된 이미지 미리보기 영역
        preview_layout = QHBoxLayout()

        # 가공된 이미지 미리보기 프레임
        self.processed_frame = QFrame()
        self.processed_frame.setStyleSheet(Styles.PROCESSED_FRAME)
        self.processed_frame.setMinimumSize(280, 100)

        processed_frame_layout = QVBoxLayout(self.processed_frame)
        processed_frame_layout.setContentsMargins(10, 10, 10, 10)
        processed_frame_layout.setSpacing(5)
        
        # 타이틀 라벨 - 작고 고정된 크기
        processed_title = QLabel("가공된 이미지")
        processed_title.setAlignment(Qt.AlignCenter)
        processed_title.setStyleSheet(Styles.LABEL_TITLE)
        processed_title.setFixedHeight(30)  # 타이틀은 작게 고정
        processed_title.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        # 이미지 표시 라벨 - 크고 확장 가능
        self.processed_label = QLabel("이미지가 여기에 표시됩니다")
        self.processed_label.setAlignment(Qt.AlignCenter)
        self.processed_label.setStyleSheet(Styles.LABEL_SUBTITLE)
        self.processed_label.setMinimumHeight(150)  # 이미지 영역은 크게
        self.processed_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        processed_frame_layout.addWidget(processed_title)
        processed_frame_layout.addWidget(self.processed_label)

        # 가공된 이미지 프레임을 중앙에 배치
        preview_layout.addStretch()
        preview_layout.addWidget(self.processed_frame)
        preview_layout.addStretch()

        main_layout.addLayout(preview_layout)

        # 버튼 생성
        button_layout = QHBoxLayout()

        # 가공하기 버튼
        self.process_button = QPushButton("가공하기")
        self.process_button.setStyleSheet(Styles.BTN_SUCCESS)
        self.process_button.setEnabled(False)
        self.process_button.clicked.connect(self.process_selected_image)
        button_layout.addWidget(self.process_button)

        # 사진 초기화 버튼
        self.reset_image_button = QPushButton("사진 초기화")
        self.reset_image_button.setStyleSheet(Styles.BTN_ACCENT)
        self.reset_image_button.clicked.connect(self.reset_image)
        button_layout.addWidget(self.reset_image_button)

        # 인쇄 버튼
        self.print_button = QPushButton("인쇄")
        self.print_button.setStyleSheet(Styles.BTN_PRIMARY)
        self.print_button.setEnabled(False)
        self.print_button.clicked.connect(self.print_image)
        button_layout.addWidget(self.print_button)

        # 새로 만들기 버튼
        self.reset_button = QPushButton("새로 만들기")
        self.reset_button.setStyleSheet(Styles.BTN_DESTRUCTIVE)
        self.reset_button.clicked.connect(self.reset_application)
        button_layout.addWidget(self.reset_button)

        main_layout.addLayout(button_layout)

        # 프레임 선택을 위한 레이아웃
        frame_layout = QHBoxLayout()
        frame_label = QLabel("프레임 선택:")
        frame_label.setStyleSheet(f"font-family: 'Malgun Gothic'; font-size: 14px; font-weight: bold; color: {Colors.TEXT_PRIMARY};")
        frame_layout.addWidget(frame_label)

        self.frame_combo = QComboBox()
        self.frame_combo.setStyleSheet(Styles.INPUT)
        self.frame_combo.addItem("4컷 - 파란색", "01.png")
        self.frame_combo.addItem("4컷 - 빨간색", "02.png")
        self.frame_combo.addItem("1컷 - 파란색", "03.png")
        self.frame_combo.addItem("1컷 - 빨간색", "04.png")
        self.frame_combo.addItem("프레임 없음", "none")
        frame_layout.addWidget(self.frame_combo)

        # 설정 버튼 (구 프레임 관리)
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(32, 32)
        self.settings_btn.setStyleSheet(Styles.BTN_ICON)
        self.settings_btn.setToolTip("설정")
        self.settings_btn.clicked.connect(self.open_settings)
        frame_layout.addWidget(self.settings_btn)

        # 프레임 미리보기 버튼
        self.preview_frame_btn = QPushButton("프레임 미리보기")
        self.preview_frame_btn.setStyleSheet(Styles.BTN_SECONDARY)
        self.preview_frame_btn.clicked.connect(self.show_frame_preview)
        frame_layout.addWidget(self.preview_frame_btn)

        main_layout.addLayout(frame_layout)

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
        
        self.update_frame_combo()

    def update_frame_combo(self):
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
        self.on_frame_changed(self.frame_combo.currentIndex())

    def open_settings(self):
        """설정 다이얼로그 열기"""
        dialog = SettingsDialog(self.frame_manager, self)
        dialog.exec_()
        self.update_frame_combo()

    def select_four_cut_mode(self):
        """네컷 모드 선택"""
        if self.current_mode == "four_cut":
            return

        # 기존 작업 확인
        if any(file is not None for file in self.selected_files) or self.processed_file:
            reply = MessageBox.question(self, '모드 변경 확인',
                                         "모드를 변경하면 현재 작업이 초기화됩니다.\n계속하시겠습니까?")
            if reply == MessageBox.No:
                # 버튼 상태 되돌리기
                self.four_cut_button.setChecked(True)
                self.single_cut_button.setChecked(False)
                return

        self.current_mode = "four_cut"
        self.four_cut_button.setChecked(True)
        self.single_cut_button.setChecked(False)

        # 드롭 영역 재구성
        self.setup_drop_area()

        # 작업 초기화
        self.reset_work_without_folder()

        print("[DEBUG] 네컷 모드로 변경됨")

    def select_single_cut_mode(self):
        """한컷 모드 선택"""
        if self.current_mode == "single_cut":
            return

        # 기존 작업 확인
        if any(file is not None for file in self.selected_files) or self.processed_file:
            reply = MessageBox.question(self, '모드 변경 확인',
                                         "모드를 변경하면 현재 작업이 초기화됩니다.\n계속하시겠습니까?")
            if reply == MessageBox.No:
                # 버튼 상태 되돌리기
                self.four_cut_button.setChecked(False)
                self.single_cut_button.setChecked(True)
                return

        self.current_mode = "single_cut"
        self.four_cut_button.setChecked(False)
        self.single_cut_button.setChecked(True)

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

        # 파일 선택 버튼 이벤트 연결
        self.drop_area.select_btn.clicked.connect(self.select_image)

        # 컨테이너에 새 드롭 영역 추가
        self.drop_container_layout.addWidget(self.drop_area)

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

        # 가공된 이미지 미리보기 초기화
        self.processed_label.setText("가공 후 미리보기")
        self.processed_label.setPixmap(QPixmap())

        # 상태 메시지 초기화
        self.processing_status_card.clear()

        # 버튼 상태 초기화
        self.process_button.setEnabled(False)
        self.print_button.setEnabled(False)





    def show_frame_preview(self):
        """선택된 프레임 미리보기"""
        if self.selected_frame == "none":
            MessageBox.information(self, "프레임 미리보기", "선택된 프레임이 없습니다.")
            return

        frame_path = os.path.join(os.getcwd(), 'frame', self.selected_frame)
        if not os.path.exists(frame_path):
            MessageBox.warning(self, "오류", f"프레임 파일을 찾을 수 없습니다: {frame_path}")
            return

        pixmap = QPixmap(frame_path)
        if not pixmap.isNull():
            preview_width = 300
            preview_height = 300
            pixmap = pixmap.scaled(preview_width, preview_height,
                                   Qt.KeepAspectRatio, Qt.SmoothTransformation)

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
                        # 스타일 강제 업데이트 (readOnly 상태 반영을 위해)
                        self.folder_input.setStyleSheet(Styles.INPUT)
                        
                        self.create_folder(actual_folder_name)
                    else:
                        self.folder_input.clear()
                        self.folder_status_card.clear()
        super().keyPressEvent(event)


    def create_folder(self, folder_name):
        """폴더를 즉시 생성하는 메서드"""
        success, folder_path, status = self.folder_manager.create_folder(folder_name)
        
        if success:
            self.created_folder = folder_path
            if status == "created":
                self.processing_status_card.show_success(f"'{folder_name}' 폴더가 생성되었습니다.")
                self.folder_status_card.show_success(f"✅ '{folder_name}' 폴더가 생성되었습니다.")
                
                print(f"폴더 생성됨: {folder_path}")
            else: # existing
                self.processing_status_card.show_success(f"'{folder_name}' 폴더를 사용합니다.")
                self.folder_status_card.show_success(f"✅ '{folder_name}' 폴더를 사용합니다.")
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
            self.folder_status_card.clear()
            return
            
        # FolderManager를 통해 상태 확인
        result = self.folder_manager.check_availability(folder_number_text)
        
        if not result:
             self.folder_status_card.clear()
             return

        if result['status'] == 'invalid':
            self.folder_status_card.show_error(f"⚠ {result['message']}")
            
        elif result['status'] == 'exists':
            self.folder_status_card.show_info(
                f"ℹ '{folder_number_text}' 폴더가 이미 존재합니다.\n"
                f"   마지막 생성: {result['creation_time']}\n"
                f"   엔터를 누르면 '{result['next_name']}' 폴더를 생성합니다."
            )
            
        elif result['status'] == 'available':
            self.folder_status_card.show_info(
                f"✨ 새로운 폴더입니다.\n"
                f"   엔터를 누르면 '{folder_number_text}' 폴더를 생성하고 고정합니다."
            )
            self.previous_folder_number = folder_number_text

    def prepare_image(self, file_path, slot_index):
        """이미지를 준비하고 상태 업데이트 - 모드별 처리"""
        print(f"[DEBUG] prepare_image 호출됨: 파일={file_path}, 슬롯={slot_index}, 모드={self.current_mode}")

        # 가공 상태 확인
        if self.processed_file:
            print(f"[DEBUG] prepare_image: 이미 가공 완료됨, 종료")
            return

        # 폴더 번호 확인
        folder_number_text = self.folder_input.text().strip()
        if not folder_number_text or not folder_number_text.isdigit():
            print(f"[DEBUG] prepare_image: 폴더 번호 검증 실패")
            return

        # 파일 저장 (슬롯 인덱스 검증)
        if self.current_mode == "four_cut":
            if 0 <= slot_index < 4:
                self.selected_files[slot_index] = file_path
                max_files = 4
            else:
                print(f"[DEBUG] prepare_image: 잘못된 슬롯 인덱스 (네컷): {slot_index}")
                return
        else:  # single_cut
            if slot_index == 0:
                self.selected_files[0] = file_path
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

    def select_image(self):
        """파일 선택 버튼 - 모드별 처리"""
        print(f"[DEBUG] select_image 호출됨, 모드: {self.current_mode}")

        # 가공 상태 확인
        if self.processed_file:
            MessageBox.warning(self, "경고", "이미 이미지 가공이 완료되었습니다.\n새 이미지를 추가하려면 먼저 '사진 초기화' 버튼을 누르세요.")
            return

        # 폴더 번호 검증
        folder_number_text = self.folder_input.text().strip()
        if not folder_number_text.isdigit() or not folder_number_text:
            MessageBox.warning(self, "경고", "유효한 폴더 번호를 먼저 입력해주세요.")
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

    def update_preview(self):
        """4분할 미리보기 업데이트"""
        preview_width = self.preview_frame.width() - 20
        preview_height = self.preview_frame.height() - 40

        cell_width = preview_width // 2
        cell_height = preview_height // 2

        preview_image = QPixmap(preview_width, preview_height)
        preview_image.fill(Qt.lightGray)

        painter = QPainter(preview_image)

        positions = [
            (0, 0),
            (cell_width, 0),
            (0, cell_height),
            (cell_width, cell_height)
        ]

        for i, file_path in enumerate(self.selected_files):
            x, y = positions[i]

            if file_path and os.path.exists(file_path):
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(cell_width - 2, cell_height - 2,
                                                  Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    offset_x = (cell_width - scaled_pixmap.width()) // 2
                    offset_y = (cell_height - scaled_pixmap.height()) // 2
                    painter.drawPixmap(x + offset_x, y + offset_y, scaled_pixmap)
            else:
                painter.setPen(Qt.darkGray)
                painter.drawRect(x + 1, y + 1, cell_width - 2, cell_height - 2)
                painter.drawText(x + 10, y + cell_height // 2, f"이미지 {i + 1}")

        painter.setPen(Qt.black)
        painter.drawLine(cell_width, 0, cell_width, preview_height)
        painter.drawLine(0, cell_height, preview_width, cell_height)

        painter.end()

        self.preview_label.setPixmap(preview_image)
        self.preview_label.setAlignment(Qt.AlignCenter)

    def process_selected_image(self):
        """가공하기 버튼 - 모드별 처리"""
        # 모드별 파일 확인
        if self.current_mode == "four_cut":
            if not all(file is not None for file in self.selected_files):
                MessageBox.warning(self, "경고", "4개 이미지를 모두 선택해주세요.")
                return
        else:  # single_cut
            if not self.selected_files[0]:
                MessageBox.warning(self, "경고", "이미지를 선택해주세요.")
                return

        folder_number_text = self.folder_input.text().strip()
        if not folder_number_text or not folder_number_text.isdigit():
            MessageBox.warning(self, "경고", "유효한 폴더 번호를 입력해주세요.")
            return

        if not self.folder_input.isReadOnly():
            reply = MessageBox.question(self, '폴더 번호 확인',
                                         f"폴더 번호를 '{folder_number_text}'로 설정하시겠습니까?\n설정 후에는 변경할 수 없습니다.")

            if reply == MessageBox.Yes:
                self.folder_input.setReadOnly(True)
            else:
                return

        if not self.created_folder or not os.path.exists(self.created_folder):
            actual_folder_name = self.folder_manager.get_actual_folder_name(folder_number_text)
            self.create_folder(actual_folder_name)
            folder_name = os.path.basename(self.created_folder)
            
            self.folder_status_card.show_success(f"✅ '{folder_name}' 폴더가 생성되었습니다.")

        processed_path = self.process_and_save(self.selected_files, self.created_folder)

        # 가공된 이미지 미리보기 표시 - PIL 적용
        if processed_path and os.path.exists(processed_path):
            print(f"[DEBUG] 가공된 이미지 로드 시작: {processed_path}")

            self.processed_file = processed_path

            # PIL을 통해 이미지 로드 (통합된 유틸리티 사용)
            preview_width = min(self.processed_frame.width() - 20, 260)
            preview_height = min(self.processed_frame.width() - 20, 160)

            print(f"[DEBUG] 가공된 이미지 미리보기 크기: {preview_width}x{preview_height}")

            pixmap = ImageUtils.load_and_resize_with_pil(processed_path, preview_width, preview_height)

            if pixmap and not pixmap.isNull():
                print(f"[DEBUG] 가공된 이미지 미리보기 설정 성공")

                self.processed_label.setPixmap(pixmap)
                self.processed_label.setAlignment(Qt.AlignCenter)
                self.print_button.setEnabled(True)

                folder_name = os.path.basename(self.created_folder)
                frame_name = self.frame_combo.currentText()
                self.processing_status_card.show_success(f"{frame_name}로 가공이 성공적으로 완료되었습니다.\n'{folder_name}' 폴더에 저장되었습니다.")
            else:
                print(f"[DEBUG] 가공된 이미지 미리보기 설정 실패")
                self.processed_label.setText("가공된 이미지를 표시할 수 없습니다")
                self.processing_status_card.show_error("가공된 이미지를 표시할 수 없습니다.")
        else:
            print(f"[DEBUG] 가공된 이미지 파일이 존재하지 않음: {processed_path}")
            self.processed_label.setText("가공된 이미지를 표시할 수 없습니다")
            self.processing_status_card.show_error("이미지 가공에 실패했습니다.")

        self.process_button.setEnabled(False)

    def process_and_save(self, files, folder_path):
        processed_image_path = None

        try:
            old_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            for old_file in old_files:
                if old_file.startswith("copy") or old_file.startswith("processed_"):
                    old_file_path = os.path.join(folder_path, old_file)
                    os.remove(old_file_path)
                    print(f"파일 삭제됨: {old_file_path}")
        except Exception as e:
            print(f"파일 삭제 오류: {e}")

        try:
            processed_image_path = self.process_image(files, folder_path)
            if processed_image_path:
                print(f"가공된 이미지 저장됨: {processed_image_path}")
        except Exception as e:
            print(f"이미지 가공 오류: {e}")
            MessageBox.critical(self, "오류", f"이미지 가공 중 오류가 발생했습니다: {str(e)}")

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
            MessageBox.critical(self, "오류", f"파일 복사 중 오류가 발생했습니다: {str(e)}")

        return processed_image_path

    def process_image(self, files, folder_path):
        try:
            processed_path = self.image_processor.process_images(
                files, 
                self.selected_frame, 
                self.frame_manager, 
                folder_path
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
        """인쇄 기능 - PIL 적용"""
        if not self.processed_file:
            MessageBox.warning(self, "경고", "인쇄할 이미지가 없습니다. 먼저 이미지를 가공해주세요.")
            return

        print(f"[DEBUG] 인쇄 요청: {self.processed_file}")
        
        success = self.print_manager.print_image(self.processed_file, self)
        
        if success:
            MessageBox.information(self, "성공", "이미지 인쇄가 시작되었습니다.")
            print(f"[DEBUG] 인쇄 작업 시작됨")



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
        self.processing_status_card.clear()

        # 버튼 상태 초기화
        self.process_button.setEnabled(False)
        self.print_button.setEnabled(False)

        print("사진들이 초기화되었습니다.")
        MessageBox.information(self, "알림", "사진들이 초기화되었습니다.")

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

        self.folder_status_card.clear()

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
        self.processing_status_card.clear()

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
