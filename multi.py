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
from PyQt5.QtCore import Qt, QRect  # QRect 추가
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PIL import Image as PILImage


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


class DropZone(QLabel):
    """개별 드롭 존 (파일명 표시 + 폴더 검증)"""

    def __init__(self, zone_id, parent_drop_area):
        super().__init__()
        self.zone_id = zone_id
        self.parent_drop_area = parent_drop_area
        self.setAcceptDrops(True)
        self.image_path = None

        print(f"[DEBUG] DropZone {zone_id} 초기화됨")

        # 기본 설정 (크기 확대)
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Arial", 11))
        # 드롭박스 크기 확대 (가로 넓히기)
        self.setFixedSize(240, 126)  # 180x160 → 240x180 (가로 +60, 세로 +20)

        # 간단한 숫자 표시
        self.setText(f"{zone_id + 1}")
        self.setFont(QFont("Malgun Gothic", 40, QFont.Bold))  # 고딕체, 큰 크기, 볼드

        # 기본 스타일
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 8px;
                background-color: #f8f8f8;
                color: #888;
                padding: 5px;
                margin: 5px;
            }
        """)

    def check_folder_validation(self):
        """폴더 번호 유효성 검사"""
        if not hasattr(self.parent_drop_area.parent_window, 'folder_input'):
            return False

        folder_number_text = self.parent_drop_area.parent_window.folder_input.text().strip()
        if not folder_number_text or not folder_number_text.isdigit():
            print(f"[DEBUG] Zone {self.zone_id}: 폴더 번호 검증 실패: '{folder_number_text}'")
            return False

        print(f"[DEBUG] Zone {self.zone_id}: 폴더 번호 검증 성공: '{folder_number_text}'")
        return True

    def set_image(self, image_path):
        """이미지 설정 및 미리보기 표시 - 미리보기 크기 강제 확대"""
        print(f"[DEBUG] Zone {self.zone_id}: set_image 호출됨, 경로: {image_path}")

        self.image_path = image_path

        if not image_path:
            print(f"[DEBUG] Zone {self.zone_id}: 이미지 경로가 None 또는 빈 문자열")
            self.reset_to_default()
            return

        if not os.path.exists(image_path):
            print(f"[DEBUG] Zone {self.zone_id}: 파일이 존재하지 않음: {image_path}")
            self.reset_to_default()
            return

        print(f"[DEBUG] Zone {self.zone_id}: 파일 존재 확인됨")

        try:
            # PIL로 이미지 로드
            pil_image = PILImage.open(image_path)
            print(f"[DEBUG] Zone {self.zone_id}: PIL 이미지 로드 성공, 크기: {pil_image.size}")

            # 미리보기 크기를 강제로 크게 설정 (드롭박스 높이 무시)
            widget_width = self.width()  # 240

            # 가로 여백만 고려하여 미리보기 크기 결정
            preview_width = widget_width - 20  # 좌우 여백 10px씩 = 220

            # 미리보기 크기를 이전 수준으로 강제 설정 (높이 제약 무시)
            target_preview_size = min(preview_width, 140)  # 가로 제약만 고려, 최대 140
            preview_size = max(target_preview_size, 110)  # 최소 110 보장

            print(f"[DEBUG] Zone {self.zone_id}: 강제 설정된 미리보기 크기: {preview_size}x{preview_size}")

            # PIL로 리사이즈
            pil_image.thumbnail((preview_size, preview_size), PILImage.Resampling.LANCZOS)
            print(f"[DEBUG] Zone {self.zone_id}: PIL 리사이즈 완료: {pil_image.size}")

            # QPixmap으로 변환 (통합된 유틸리티 사용)
            pixmap = ImageUtils.pil_to_qpixmap(pil_image)

            if pixmap.isNull():
                print(f"[DEBUG] Zone {self.zone_id}: QPixmap 변환 실패")
                self.reset_to_default()
                return

            # 파일명 처리
            filename = os.path.basename(image_path)
            if len(filename) > 35:
                filename = filename[:32] + "..."
            print(f"[DEBUG] Zone {self.zone_id}: 표시될 파일명: {filename}")

            # 이미지와 파일명을 결합한 새 위젯 생성
            combined_pixmap = QPixmap(self.width(), self.height())
            combined_pixmap.fill(Qt.transparent)

            painter = QPainter(combined_pixmap)

            # 이미지 그리기 (상단 중앙, 큰 이미지가 넘쳐도 상관없이)
            img_x = (self.width() - pixmap.width()) // 2
            img_y = 2  # 상단 여백 최소화
            painter.drawPixmap(img_x, img_y, pixmap)

            # 파일명을 이미지 하단에 오버레이 (항상 오버레이 방식 사용)
            # 반투명 배경 생성
            overlay_y = img_y + pixmap.height() - 20
            if overlay_y < 0:  # 이미지가 너무 크면 하단에 배치
                overlay_y = self.height() - 20

            painter.fillRect(0, overlay_y, self.width(), 20, QColor(255, 255, 255, 200))  # 반투명 흰색 배경

            # 텍스트 그리기
            painter.setPen(Qt.black)
            painter.setFont(QFont("Malgun Gothic", 8, QFont.Bold))

            text_rect = QRect(5, overlay_y, self.width() - 10, 20)
            painter.drawText(text_rect, Qt.AlignCenter, filename)

            painter.end()

            # 결합된 이미지 설정
            self.setPixmap(combined_pixmap)
            self.setText("")  # 기본 텍스트 제거

            print(f"[DEBUG] Zone {self.zone_id}: 강제 확대된 미리보기 설정 완료")

            # 성공 스타일 적용
            self.setStyleSheet("""
                QLabel {
                    border: 2px solid #4CAF50;
                    border-radius: 8px;
                    background-color: #e8f5e8;
                    padding: 5px;
                    margin: 5px;
                }
            """)

        except Exception as e:
            print(f"[DEBUG] Zone {self.zone_id}: 이미지 처리 중 오류: {e}")
            self.reset_to_default()

    def reset_to_default(self):
        """기본 상태로 리셋 - 간단한 숫자 표시"""
        print(f"[DEBUG] Zone {self.zone_id}: reset_to_default 호출됨")

        self.image_path = None
        self.setPixmap(QPixmap())
        self.setText(f"{self.zone_id + 1}")
        self.setFont(QFont("Malgun Gothic", 40, QFont.Bold))  # 고딕체, 큰 크기, 볼드
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 8px;
                background-color: #f8f8f8;
                color: #888;
                padding: 5px;
                margin: 5px;
            }
        """)

    def dragEnterEvent(self, event):
        print(f"[DEBUG] Zone {self.zone_id}: dragEnterEvent 호출됨")

        if hasattr(self.parent_drop_area.parent_window,
                   'processed_file') and self.parent_drop_area.parent_window.processed_file:
            print(f"[DEBUG] Zone {self.zone_id}: 이미 가공 완료됨, 드래그 무시")
            event.ignore()
            return

        if event.mimeData().hasUrls():
            print(f"[DEBUG] Zone {self.zone_id}: URL 데이터 확인됨")
            event.acceptProposedAction()
            self.setStyleSheet("""
                QLabel {
                    border: 3px dashed #007ACC;
                    border-radius: 8px;
                    background-color: #e6f3ff;
                    color: #007ACC;
                    padding: 5px;
                    margin: 5px;
                    font-weight: bold;
                }
            """)
        else:
            print(f"[DEBUG] Zone {self.zone_id}: URL 데이터 없음")

    def dragLeaveEvent(self, event):
        print(f"[DEBUG] Zone {self.zone_id}: dragLeaveEvent 호출됨")

        if self.image_path:
            self.setStyleSheet("""
                QLabel {
                    border: 2px solid #4CAF50;
                    border-radius: 8px;
                    background-color: #e8f5e8;
                    padding: 5px;
                    margin: 5px;
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    border: 2px dashed #aaa;
                    border-radius: 8px;
                    background-color: #f8f8f8;
                    color: #888;
                    padding: 5px;
                    margin: 5px;
                }
            """)

    def dropEvent(self, event):
        print(f"[DEBUG] Zone {self.zone_id}: dropEvent 호출됨")

        # 1. 먼저 가공 상태 확인
        if hasattr(self.parent_drop_area.parent_window,
                   'processed_file') and self.parent_drop_area.parent_window.processed_file:
            print(f"[DEBUG] Zone {self.zone_id}: 이미 가공 완료됨, 드롭 무시")
            QMessageBox.warning(self.parent_drop_area.parent_window, "경고",
                                "이미 이미지 가공이 완료되었습니다.\n새 이미지를 추가하려면 먼저 '사진 초기화' 버튼을 누르세요.")
            event.ignore()
            return

        # 2. 폴더 번호 유효성 검사 (미리보기 처리 전에)
        if not self.check_folder_validation():
            print(f"[DEBUG] Zone {self.zone_id}: 폴더 번호 검증 실패로 드롭 거부")
            QMessageBox.warning(self.parent_drop_area.parent_window, "경고", "유효한 폴더 번호를 먼저 입력해주세요.")
            # 스타일을 원래대로 복원
            self.dragLeaveEvent(event)
            event.ignore()
            return

        # 3. URL 데이터 처리
        if event.mimeData().hasUrls():
            print(f"[DEBUG] Zone {self.zone_id}: URL 리스트 처리 시작")

            for i, url in enumerate(event.mimeData().urls()):
                file_path = url.toLocalFile()
                print(f"[DEBUG] Zone {self.zone_id}: URL {i}: {file_path}")

                if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                    print(f"[DEBUG] Zone {self.zone_id}: 유효한 이미지 파일 확인됨")

                    # 4. 이미지 설정 (폴더 검증 통과 후)
                    self.set_image(file_path)

                    # 5. 부모 창의 메서드 호출
                    if hasattr(self.parent_drop_area.parent_window, 'prepare_image'):
                        print(f"[DEBUG] Zone {self.zone_id}: prepare_image 호출")
                        self.parent_drop_area.parent_window.prepare_image(file_path, self.zone_id)
                    else:
                        print(f"[DEBUG] Zone {self.zone_id}: prepare_image 메서드 없음")
                    break
                else:
                    print(f"[DEBUG] Zone {self.zone_id}: 지원하지 않는 파일 형식: {file_path}")

            event.acceptProposedAction()
            print(f"[DEBUG] Zone {self.zone_id}: dropEvent 완료")
        else:
            print(f"[DEBUG] Zone {self.zone_id}: URL 데이터 없음")


class SingleDropArea(QFrame):
    """Single 모드용 드롭 영역 (드롭존 1개)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.NoFrame)
        self.setLineWidth(0)
        # 한컷 모드용 크기
        self.setMinimumSize(540, 330)
        self.setAcceptDrops(False)

        self.setStyleSheet("""
            SingleDropArea {
                background-color: #fafafa;
                border-radius: 10px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 제목 라벨
        title_label = QLabel("이미지 드롭 영역 (1개) - 폴더 번호를 먼저 입력하세요")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Malgun Gothic", 13, QFont.Bold))
        title_label.setStyleSheet("color: #333; margin-bottom: 8px;")
        main_layout.addWidget(title_label)

        # 상하 간격을 위한 스페이서 추가
        main_layout.addSpacing(20)

        # 단일 드롭존 (중앙 배치)
        zone_layout = QHBoxLayout()
        zone_layout.addStretch()

        self.zone1 = DropZone(0, self)
        zone_layout.addWidget(self.zone1)

        zone_layout.addStretch()
        main_layout.addLayout(zone_layout)

        # 하단 간격을 위한 스페이서 추가
        main_layout.addSpacing(40)

        # 파일 선택 버튼
        self.select_btn = QPushButton("또는 파일 선택")
        self.select_btn.setFont(QFont("Malgun Gothic", 11))
        self.select_btn.setFixedSize(140, 32)
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
        main_layout.addWidget(self.select_btn, 0, Qt.AlignCenter)

        self.parent_window = parent
        self.labels = [self.zone1]

    def reset_zones(self):
        """모든 드롭 존을 초기 상태로 리셋"""
        self.zone1.reset_to_default()

    def set_image_to_zone(self, zone_index, image_path):
        """특정 존에 이미지 설정"""
        if zone_index == 0:
            self.zone1.set_image(image_path)

class MultiDropArea(QFrame):
    """Multi 모드용 드롭 영역 (축소된 드롭존 높이 반영)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.NoFrame)
        self.setLineWidth(0)
        # 전체 영역 크기 조정 (드롭존 높이 축소에 맞춰)
        self.setMinimumSize(540, 330)  # 540x440 → 540x330 (세로 110px 감소)
        self.setAcceptDrops(False)

        self.setStyleSheet("""
            MultiDropArea {
                background-color: #fafafa;
                border-radius: 10px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 제목 라벨
        title_label = QLabel("이미지 드롭 영역 (4개) - 폴더 번호를 먼저 입력하세요")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Malgun Gothic", 13, QFont.Bold))
        title_label.setStyleSheet("color: #333; margin-bottom: 8px;")
        main_layout.addWidget(title_label)

        # 상단 행
        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)

        self.zone1 = DropZone(0, self)
        self.zone2 = DropZone(1, self)

        top_layout.addWidget(self.zone1)
        top_layout.addWidget(self.zone2)

        # 상하 간격 (축소된 높이에 맞춰 조정)
        main_layout.addLayout(top_layout)
        main_layout.addSpacing(12)  # 상하 드롭존 사이 간격 축소 (18 → 12)

        # 하단 행
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(8)

        self.zone3 = DropZone(2, self)
        self.zone4 = DropZone(3, self)

        bottom_layout.addWidget(self.zone3)
        bottom_layout.addWidget(self.zone4)

        main_layout.addLayout(bottom_layout)

        # 파일 선택 버튼
        self.select_btn = QPushButton("또는 파일 선택")
        self.select_btn.setFont(QFont("Malgun Gothic", 11))
        self.select_btn.setFixedSize(140, 32)
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
        main_layout.addWidget(self.select_btn, 0, Qt.AlignCenter)

        self.parent_window = parent
        self.labels = [self.zone1, self.zone2, self.zone3, self.zone4]

    def reset_zones(self):
        """모든 드롭 존을 초기 상태로 리셋"""
        for zone in [self.zone1, self.zone2, self.zone3, self.zone4]:
            zone.reset_to_default()

    def set_image_to_zone(self, zone_index, image_path):
        """특정 존에 이미지 설정"""
        zones = [self.zone1, self.zone2, self.zone3, self.zone4]
        if 0 <= zone_index < len(zones):
            zones[zone_index].set_image(image_path)

    def dragEnterEvent(self, event):
        pass

    def dragLeaveEvent(self, event):
        pass

    def dropEvent(self, event):
        pass


class MultiWindow(QMainWindow):
    """Multi 모드 메인 윈도우 (4개 이미지 처리)"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("사진 선택 및 인쇄 - Multi Mode (4개 이미지)")
        # 전체 윈도우 크기 증가 (드롭 영역 확대에 맞춰)
        self.setGeometry(100, 100, 620, 630)  # 620x740 → 620x630 (세로 110px 감소)

        # 추가: 첫 번째 체크 상태 관리 변수
        self.is_first_check = True

        # 종료 버튼을 우측 상단에 배치
        self.exit_button = QPushButton("종료", self)
        self.exit_button.setFont(QFont("Arial", 10))
        self.exit_button.setStyleSheet("background-color: #bbbbbb; color: black; padding: 5px;")
        self.exit_button.clicked.connect(self.close_application)
        self.exit_button.setFixedSize(60, 30)
        self.exit_button.move(self.width() - 70, 10)

        # 창 크기가 변경될 때 종료 버튼 위치 조정
        self.resizeEvent = self.on_resize

        # 메인 레이아웃 설정
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)

        # 폴더 번호 입력을 위한 가로 레이아웃
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

        main_layout.addLayout(folder_layout)

        # 정보 표시를 위한 영역
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        # 폴더 존재 여부 표시
        self.folder_exists_label = QLabel("")
        self.folder_exists_label.setFont(QFont("Arial", 12))
        info_layout.addWidget(self.folder_exists_label)

        # 새 폴더 생성 예상 정보 표시
        self.new_folder_label = QLabel("")
        self.new_folder_label.setFont(QFont("Arial", 12))
        self.new_folder_label.setStyleSheet("color: blue;")
        info_layout.addWidget(self.new_folder_label)

        # 마지막 폴더 생성 시간 표시
        self.last_folder_time_label = QLabel("")
        self.last_folder_time_label.setFont(QFont("Arial", 12))
        self.last_folder_time_label.setStyleSheet("color: purple;")
        info_layout.addWidget(self.last_folder_time_label)

        main_layout.addLayout(info_layout)

        # 사이 공간 최소화
        main_layout.addSpacerItem(QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # 모드 선택 버튼 추가
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(10)

        mode_label = QLabel("모드 선택:")
        mode_label.setFont(QFont("Malgun Gothic", 14, QFont.Bold))
        mode_layout.addWidget(mode_label)

        self.four_cut_button = QPushButton("네컷 모드")
        self.four_cut_button.setFont(QFont("Malgun Gothic", 12))
        self.four_cut_button.setFixedSize(120, 40)
        self.four_cut_button.setCheckable(True)
        self.four_cut_button.setChecked(True)  # 기본값: 네컷 모드
        self.four_cut_button.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: 2px solid #4CAF50;
                        border-radius: 5px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                    QPushButton:checked {
                        background-color: #4CAF50;
                        color: white;
                    }
                    QPushButton:!checked {
                        background-color: white;
                        color: #4CAF50;
                    }
                """)
        self.four_cut_button.clicked.connect(self.select_four_cut_mode)
        mode_layout.addWidget(self.four_cut_button)

        self.single_cut_button = QPushButton("한컷 모드")
        self.single_cut_button.setFont(QFont("Malgun Gothic", 12))
        self.single_cut_button.setFixedSize(120, 40)
        self.single_cut_button.setCheckable(True)
        self.single_cut_button.setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border: 2px solid #2196F3;
                        border-radius: 5px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #1976D2;
                    }
                    QPushButton:checked {
                        background-color: #2196F3;
                        color: white;
                    }
                    QPushButton:!checked {
                        background-color: white;
                        color: #2196F3;
                    }
                """)
        self.single_cut_button.clicked.connect(self.select_single_cut_mode)
        mode_layout.addWidget(self.single_cut_button)

        mode_layout.addStretch()
        main_layout.addLayout(mode_layout)

        # 드롭 영역을 위한 고정 컨테이너 생성
        self.drop_container = QWidget()
        self.drop_container_layout = QVBoxLayout(self.drop_container)
        self.drop_container_layout.setContentsMargins(0, 0, 0, 0)

        # 초기 드롭 영역 설정
        self.drop_area = MultiDropArea(self)
        self.drop_area.select_btn.clicked.connect(self.select_image)
        self.drop_container_layout.addWidget(self.drop_area)

        main_layout.addWidget(self.drop_container)

        # 상태 메시지 영역 확대
        self.status_message = QLabel("")
        self.status_message.setFont(QFont("Arial", 12))
        self.status_message.setAlignment(Qt.AlignCenter)
        self.status_message.setStyleSheet("color: #007700; margin: 10px 0px;")
        self.status_message.setWordWrap(True)
        self.status_message.setMinimumHeight(50)  # 최소 높이 설정으로 두 줄 텍스트 수용
        self.status_message.setMaximumHeight(70)  # 최대 높이 제한
        main_layout.addWidget(self.status_message)

        # 가공된 이미지 미리보기 영역만 유지
        preview_layout = QHBoxLayout()

        # 가공된 이미지 미리보기 프레임만 유지
        self.processed_frame = QFrame()
        self.processed_frame.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.processed_frame.setLineWidth(1)
        self.processed_frame.setMinimumSize(280, 180)
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

        # 가공된 이미지 프레임을 중앙에 배치
        preview_layout.addStretch()
        preview_layout.addWidget(self.processed_frame)
        preview_layout.addStretch()

        main_layout.addLayout(preview_layout)

        # 버튼 생성
        button_layout = QHBoxLayout()

        # 가공하기 버튼
        self.process_button = QPushButton("가공하기")
        self.process_button.setFont(QFont("Arial", 14))
        self.process_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        self.process_button.setEnabled(False)
        self.process_button.clicked.connect(self.process_selected_image)
        button_layout.addWidget(self.process_button)

        # 사진 초기화 버튼
        self.reset_image_button = QPushButton("사진 초기화")
        self.reset_image_button.setFont(QFont("Arial", 14))
        self.reset_image_button.setStyleSheet("background-color: #FF9800; color: white; padding: 8px;")
        self.reset_image_button.clicked.connect(self.reset_image)
        button_layout.addWidget(self.reset_image_button)

        # 인쇄 버튼
        self.print_button = QPushButton("인쇄")
        self.print_button.setFont(QFont("Arial", 14))
        self.print_button.setEnabled(False)
        self.print_button.clicked.connect(self.print_image)
        button_layout.addWidget(self.print_button)

        # 새로 만들기 버튼
        self.reset_button = QPushButton("새로 만들기")
        self.reset_button.setFont(QFont("Arial", 14))
        self.reset_button.setStyleSheet("background-color: #f44336; color: white; padding: 8px;")
        self.reset_button.clicked.connect(self.reset_application)
        button_layout.addWidget(self.reset_button)

        main_layout.addLayout(button_layout)

        # 프레임 선택을 위한 레이아웃
        frame_layout = QHBoxLayout()
        frame_label = QLabel("프레임 선택:")
        frame_label.setFont(QFont("Arial", 14))
        frame_layout.addWidget(frame_label)

        self.frame_combo = QComboBox()
        self.frame_combo.setFont(QFont("Arial", 14))
        self.frame_combo.addItem("4컷 - 파란색", "01.png")
        self.frame_combo.addItem("4컷 - 빨간색", "02.png")
        self.frame_combo.addItem("1컷 - 파란색", "03.png")
        self.frame_combo.addItem("1컷 - 빨간색", "04.png")
        self.frame_combo.addItem("프레임 없음", "none")
        frame_layout.addWidget(self.frame_combo)

        # 프레임 미리보기 버튼
        self.preview_frame_btn = QPushButton("프레임 미리보기")
        self.preview_frame_btn.setFont(QFont("Arial", 12))
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

    def select_four_cut_mode(self):
        """네컷 모드 선택"""
        if self.current_mode == "four_cut":
            return

        # 기존 작업 확인
        if any(file is not None for file in self.selected_files) or self.processed_file:
            reply = QMessageBox.question(self, '모드 변경 확인',
                                         "모드를 변경하면 현재 작업이 초기화됩니다.\n계속하시겠습니까?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
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
            reply = QMessageBox.question(self, '모드 변경 확인',
                                         "모드를 변경하면 현재 작업이 초기화됩니다.\n계속하시겠습니까?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
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

        # 레이아웃에 추가 (기존 드롭 영역 위치에)
        central_widget = self.centralWidget()
        layout = central_widget.layout()

        # 드롭 영역을 적절한 위치에 삽입 (상태 메시지 앞)
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item and item.widget() == self.status_message:
                layout.insertWidget(i, self.drop_area)
                break

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
        self.status_message.setText("")

        # 버튼 상태 초기화
        self.process_button.setEnabled(False)
        self.print_button.setEnabled(False)

    def pil_to_qpixmap(self, pil_image):
        """PIL 이미지를 QPixmap으로 변환하는 공통 함수"""
        try:
            # PIL 이미지를 RGB로 변환
            if pil_image.mode == 'RGBA':
                # 흰색 배경과 합성
                background = PILImage.new('RGB', pil_image.size, (255, 255, 255))
                background.paste(pil_image, mask=pil_image.split()[-1])
                pil_image = background
            elif pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')

            # PIL 이미지를 바이트로 변환
            byte_array = io.BytesIO()
            pil_image.save(byte_array, format='PNG')
            byte_array.seek(0)

            # QImage로 로드
            qimage = QImage()
            qimage.loadFromData(byte_array.getvalue())

            if qimage.isNull():
                print(f"[DEBUG] MultiWindow: QImage 변환 실패")
                return QPixmap()

            # QPixmap으로 변환
            qpixmap = QPixmap.fromImage(qimage)
            print(f"[DEBUG] MultiWindow: PIL → QPixmap 변환 성공")
            return qpixmap

        except Exception as e:
            print(f"[DEBUG] MultiWindow: PIL → QPixmap 변환 오류: {e}")
            return QPixmap()

    def load_image_with_pil(self, image_path, target_width, target_height):
        """PIL을 통해 이미지를 로드하고 크기 조정"""
        try:
            print(f"[DEBUG] MultiWindow: PIL로 이미지 로드 시작: {image_path}")

            # PIL로 이미지 로드
            pil_image = PILImage.open(image_path)
            print(f"[DEBUG] MultiWindow: PIL 이미지 로드 성공, 원본 크기: {pil_image.size}")

            # 비율 유지하며 크기 조정
            pil_image.thumbnail((target_width, target_height), PILImage.Resampling.LANCZOS)
            print(f"[DEBUG] MultiWindow: PIL 리사이즈 완료: {pil_image.size}")

            # QPixmap으로 변환
            pixmap = self.pil_to_qpixmap(pil_image)

            if pixmap.isNull():
                print(f"[DEBUG] MultiWindow: QPixmap 변환 실패")
                return None

            print(f"[DEBUG] MultiWindow: 최종 QPixmap 크기: {pixmap.width()}x{pixmap.height()}")
            return pixmap

        except Exception as e:
            print(f"[DEBUG] MultiWindow: 이미지 로드 오류: {e}")
            return None

    def on_resize(self, event):
        """창 크기가 변경될 때 종료 버튼 위치 조정"""
        self.exit_button.move(self.width() - 70, 10)
        super().resizeEvent(event)

    def show_frame_preview(self):
        """선택된 프레임 미리보기"""
        if self.selected_frame == "none":
            QMessageBox.information(self, "프레임 미리보기", "선택된 프레임이 없습니다.")
            return

        frame_path = os.path.join(os.getcwd(), 'frame', self.selected_frame)
        if not os.path.exists(frame_path):
            QMessageBox.warning(self, "오류", f"프레임 파일을 찾을 수 없습니다: {frame_path}")
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
                self.status_message.setText("새로운 프레임이 선택되었습니다. 가공하기 버튼을 눌러 이미지를 재가공하세요.")
                self.status_message.setStyleSheet("color: #007ACC; margin: 10px 0px;")
            else:
                filled_count = sum(1 for file in self.selected_files if file is not None)
                self.status_message.setText(f"새로운 프레임이 선택되었습니다. {filled_count}/4개 이미지가 준비되었습니다.")
                self.status_message.setStyleSheet("color: #007ACC; margin: 10px 0px;")
                self.process_button.setEnabled(False)

    def keyPressEvent(self, event):
        """키 이벤트 처리"""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            focused_widget = QApplication.focusWidget()
            if focused_widget == self.folder_input and not self.folder_input.text().strip() == "":
                folder_number_text = self.folder_input.text().strip()
                if folder_number_text.isdigit():
                    actual_folder_name = self.get_actual_folder_name(folder_number_text)
                    reply = QMessageBox.question(self, '폴더 번호 확인',
                                                 f"폴더 이름을 '{actual_folder_name}'로 설정하시겠습니까?\n설정 후에는 변경할 수 없습니다.",
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        self.folder_input.setEnabled(False)
                        self.folder_input.setStyleSheet("background-color: #e0e0e0;")
                        self.check_folder_exists()
                        self.create_folder(actual_folder_name)
                        folder_name = os.path.basename(actual_folder_name)
                        self.folder_exists_label.setText(f"'{folder_name}' 폴더가 생성되었습니다.")
                        self.folder_exists_label.setStyleSheet("color: green;")
                        self.new_folder_label.setText("")
                        self.last_folder_time_label.setText("")
                    else:
                        self.folder_input.clear()
        super().keyPressEvent(event)

    def get_actual_folder_name(self, folder_number_text):
        """실제 생성될 폴더 이름을 반환하는 메서드"""
        folder_name = folder_number_text
        folder_path = os.path.join(os.getcwd(), folder_name)

        if os.path.exists(folder_path):
            base_folder_name = folder_name
            existing_folders = [d for d in os.listdir(os.getcwd())
                                if os.path.isdir(os.path.join(os.getcwd(), d)) and
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
        """폴더를 즉시 생성하는 메서드"""
        folder_path = os.path.join(os.getcwd(), folder_name)
        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path)
                self.created_folder = folder_path
                self.status_message.setText(f"'{folder_name}' 폴더가 생성되었습니다.")
                self.status_message.setStyleSheet("color: #007700; margin: 10px 0px;")
                self.folder_exists_label.setText(f"'{folder_name}' 폴더가 생성되었습니다.")
                self.folder_exists_label.setStyleSheet("color: green;")
                self.new_folder_label.setText("")
                self.last_folder_time_label.setText("")
                print(f"폴더 생성됨: {folder_path}")
            except Exception as e:
                self.status_message.setText(f"폴더 생성 중 오류가 발생했습니다: {str(e)}")
                self.status_message.setStyleSheet("color: #FF0000; margin: 10px 0px;")
                print(f"폴더 생성 오류: {e}")
        else:
            self.created_folder = folder_path
            self.status_message.setText(f"'{folder_name}' 폴더를 사용합니다.")
            self.status_message.setStyleSheet("color: #007700; margin: 10px 0px;")
            self.folder_exists_label.setText(f"'{folder_name}' 폴더가 사용됩니다.")
            self.folder_exists_label.setStyleSheet("color: green;")
            self.new_folder_label.setText("")
            self.last_folder_time_label.setText("")

    def check_folder_exists(self):
        previous_folder_number = self.folder_input.text().strip() if hasattr(self, 'previous_folder_number') else None
        folder_number_text = self.folder_input.text().strip()

        if previous_folder_number != folder_number_text:
            self.created_folder = None
            self.previous_folder_number = folder_number_text

        self.folder_exists_label.setText("")
        self.new_folder_label.setText("")
        self.last_folder_time_label.setText("")

        if self.created_folder and os.path.exists(self.created_folder):
            folder_name = os.path.basename(self.created_folder)
            self.folder_exists_label.setText(f"'{folder_name}' 폴더가 생성되었습니다.")
            self.folder_exists_label.setStyleSheet("color: green;")
            return

        if not folder_number_text:
            return

        if folder_number_text.isdigit():
            folder_number = int(folder_number_text)
            folder_name = str(folder_number)
            folder_path = os.path.join(os.getcwd(), folder_name)

            if os.path.exists(folder_path):
                self.folder_exists_label.setText("이미 있는 이름입니다.")
                self.folder_exists_label.setStyleSheet("color: red;")

                folder_creation_time = os.path.getctime(folder_path)
                time_str = datetime.datetime.fromtimestamp(folder_creation_time).strftime('%Y-%m-%d %H:%M:%S')
                self.last_folder_time_label.setText(f"'{folder_name}' 폴더 생성 시간: {time_str}")

                base_folder_name = folder_name
                existing_folders = [d for d in os.listdir(os.getcwd())
                                    if os.path.isdir(os.path.join(os.getcwd(), d)) and
                                    d.startswith(base_folder_name + "_")]

                if existing_folders:
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

                    if max_folder:
                        max_folder_path = os.path.join(os.getcwd(), max_folder)
                        max_folder_creation_time = os.path.getctime(max_folder_path)
                        max_time_str = datetime.datetime.fromtimestamp(max_folder_creation_time).strftime(
                            '%Y-%m-%d %H:%M:%S')
                        self.last_folder_time_label.setText(f"'{max_folder}' 폴더 생성 시간: {max_time_str}")

                    new_folder_name = f"{base_folder_name}_{max_num + 1}"
                    self.new_folder_label.setText(f"'{new_folder_name}'에 새로 생성됩니다.")
                else:
                    new_folder_name = f"{base_folder_name}_1"
                    self.new_folder_label.setText(f"'{new_folder_name}'에 새로 생성됩니다.")
            else:
                self.folder_exists_label.setText("새로운 이름입니다.")
                self.folder_exists_label.setStyleSheet("color: green;")
                self.new_folder_label.setText(f"'{folder_name}'에 새로 생성됩니다.")
        else:
            self.folder_exists_label.setText("유효한 번호를 입력해주세요.")
            self.folder_exists_label.setStyleSheet("color: orange;")

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
                self.status_message.setText("4개 이미지가 모두 준비되었습니다. 가공하기 버튼을 누르세요.")
            else:
                self.status_message.setText("이미지가 준비되었습니다. 가공하기 버튼을 누르세요.")
            self.status_message.setStyleSheet("color: #007700; margin: 10px 0px;")
        else:
            if self.current_mode == "four_cut":
                self.status_message.setText(f"{filled_count}/4개 이미지가 준비되었습니다.")
            else:
                self.status_message.setText("이미지를 선택해주세요.")
            self.status_message.setStyleSheet("color: #007ACC; margin: 10px 0px;")
            self.process_button.setEnabled(False)

        print(f"[DEBUG] prepare_image 완료")

    def select_image(self):
        """파일 선택 버튼 - 모드별 처리"""
        print(f"[DEBUG] select_image 호출됨, 모드: {self.current_mode}")

        # 가공 상태 확인
        if self.processed_file:
            QMessageBox.warning(self, "경고", "이미 이미지 가공이 완료되었습니다.\n새 이미지를 추가하려면 먼저 '사진 초기화' 버튼을 누르세요.")
            return

        # 폴더 번호 검증
        folder_number_text = self.folder_input.text().strip()
        if not folder_number_text.isdigit() or not folder_number_text:
            QMessageBox.warning(self, "경고", "유효한 폴더 번호를 먼저 입력해주세요.")
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
                QMessageBox.warning(self, "경고", "4개 이미지를 모두 선택해주세요.")
                return
        else:  # single_cut
            if not self.selected_files[0]:
                QMessageBox.warning(self, "경고", "이미지를 선택해주세요.")
                return

        folder_number_text = self.folder_input.text().strip()
        if not folder_number_text or not folder_number_text.isdigit():
            QMessageBox.warning(self, "경고", "유효한 폴더 번호를 입력해주세요.")
            return

        if self.folder_input.isEnabled():
            reply = QMessageBox.question(self, '폴더 번호 확인',
                                         f"폴더 번호를 '{folder_number_text}'로 설정하시겠습니까?\n설정 후에는 변경할 수 없습니다.",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.folder_input.setEnabled(False)
                self.folder_input.setStyleSheet("background-color: #e0e0e0;")
            else:
                return

        if not self.created_folder or not os.path.exists(self.created_folder):
            actual_folder_name = self.get_actual_folder_name(folder_number_text)
            self.create_folder(actual_folder_name)
            folder_name = os.path.basename(self.created_folder)
            self.folder_exists_label.setText(f"'{folder_name}' 폴더가 생성되었습니다.")
            self.folder_exists_label.setStyleSheet("color: green;")
            self.new_folder_label.setText("")
            self.last_folder_time_label.setText("")

        processed_path = self.process_and_save(self.selected_files, self.created_folder)

        # 가공된 이미지 미리보기 표시 - PIL 적용
        # 가공된 이미지 미리보기 표시 - PIL 적용
        if processed_path and os.path.exists(processed_path):
            print(f"[DEBUG] 가공된 이미지 로드 시작: {processed_path}")

            self.processed_file = processed_path

            # PIL을 통해 이미지 로드 (통합된 유틸리티 사용)
            preview_width = min(self.processed_frame.width() - 20, 260)
            preview_height = min(self.processed_frame.height() - 20, 160)

            print(f"[DEBUG] 가공된 이미지 미리보기 크기: {preview_width}x{preview_height}")

            pixmap = ImageUtils.load_and_resize_with_pil(processed_path, preview_width, preview_height)

            if pixmap and not pixmap.isNull():
                print(f"[DEBUG] 가공된 이미지 미리보기 설정 성공")

                self.processed_label.setPixmap(pixmap)
                self.processed_label.setAlignment(Qt.AlignCenter)
                self.print_button.setEnabled(True)

                folder_name = os.path.basename(self.created_folder)
                frame_name = self.frame_combo.currentText()
                self.status_message.setText(f"{frame_name}로 가공이 성공적으로 완료되었습니다.\n'{folder_name}' 폴더에 저장되었습니다.")
                self.status_message.setStyleSheet("color: #007700; margin: 10px 0px;")
            else:
                print(f"[DEBUG] 가공된 이미지 미리보기 설정 실패")
                self.processed_label.setText("가공된 이미지를 표시할 수 없습니다")
                self.status_message.setText("가공된 이미지를 표시할 수 없습니다.")
                self.status_message.setStyleSheet("color: #FF0000; margin: 10px 0px;")
        else:
            print(f"[DEBUG] 가공된 이미지 파일이 존재하지 않음: {processed_path}")
            self.processed_label.setText("가공된 이미지를 표시할 수 없습니다")
            self.status_message.setText("이미지 가공에 실패했습니다.")
            self.status_message.setStyleSheet("color: #FF0000; margin: 10px 0px;")

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
            QMessageBox.critical(self, "오류", f"이미지 가공 중 오류가 발생했습니다: {str(e)}")

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
        base_name = os.path.basename(files[0]) if files[0] else "image.jpg"
        processed_image_path = os.path.join(folder_path, "processed_" + base_name)

        if self.selected_frame == "none":
            if files[0]:
                image = Image.open(files[0])
                image.save(processed_image_path, quality=100)
            return processed_image_path

        try:
            from processing import insert_images_into_frame
            frame_path = os.path.join(os.getcwd(), 'frame', self.selected_frame)

            os.makedirs(os.path.dirname(frame_path), exist_ok=True)

            if not os.path.exists(frame_path):
                QMessageBox.warning(self, "경고", "프레임 이미지를 찾을 수 없어 원본을 그대로 사용합니다.")
                if files[0]:
                    shutil.copy(files[0], processed_image_path)
            else:
                photo_regions = []

                if self.selected_frame in ["01.png","02.png"]:
                    # 새로운 01.png 좌표 적용
                    '''
                    regions = [
                        (63, 66, 1757, 1195),  # 1번 영역
                        (1796, 666, 3490, 1795),  # 2번 영역
                        (63, 1229, 1757, 2358),  # 3번 영역
                        (1796, 1826, 3490, 2955)  # 4번 영역
                    ]'''
                    regions = [
                        (102, 98, 1348, 930),  # 1번 영역
                        (1383, 511, 2628, 1343),  # 2번 영역
                        (102, 973, 1348, 1805),  # 3번 영역
                        (1383, 1387, 2628, 2218)  # 4번 영역
                    ]
                elif self.selected_frame in ["03.png","04.png"]:
                    regions = [
                        (101, 104, 3394, 1966),
                    ]
                else:
                    regions = []

                for i, file_path in enumerate(files):
                    if file_path and os.path.exists(file_path):
                        photo_regions.append((file_path, regions[i]))

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
            if files[0]:
                shutil.copy(files[0], processed_image_path)
            self.status_message.setText("오류로 인해 원본 이미지가 그대로 사용되었습니다.")
            self.status_message.setStyleSheet("color: #FF0000; margin: 10px 0px;")

        return processed_image_path

    def print_image(self):
        """인쇄 기능 - PIL 적용"""
        if not self.processed_file or not os.path.exists(self.processed_file):
            QMessageBox.warning(self, "경고", "인쇄할 이미지가 없습니다. 먼저 이미지를 가공해주세요.")
            return

        print(f"[DEBUG] 인쇄용 이미지 로드 시작: {self.processed_file}")

        # PIL을 통해 이미지 로드 시도 (통합된 유틸리티 사용)
        try:
            pil_image = PILImage.open(self.processed_file)
            print(f"[DEBUG] PIL로 인쇄용 이미지 로드 성공: {pil_image.size}")

            # QImage로 변환 (통합된 유틸리티 사용)
            qimage = ImageUtils.pil_to_qimage(pil_image)

            if qimage.isNull():
                print(f"[DEBUG] PIL → QImage 변환 실패, 기본 방식 시도")
                # 기본 방식으로 시도
                qimage = QImage(self.processed_file)

            if qimage.isNull():
                QMessageBox.critical(self, "오류", "이미지를 인쇄용으로 로드할 수 없습니다.")
                return

        except Exception as e:
            print(f"[DEBUG] PIL 인쇄용 이미지 로드 실패: {e}, 기본 방식 시도")
            # PIL 실패 시 기본 방식으로 시도
            qimage = QImage(self.processed_file)
            if qimage.isNull():
                QMessageBox.critical(self, "오류", "이미지를 인쇄용으로 로드할 수 없습니다.")
                return

        print(f"[DEBUG] 인쇄용 이미지 준비 완료: {qimage.width()}x{qimage.height()}")

        # 프린터 설정
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.NativeFormat)

        print_dialog = QPrintDialog(printer, self)
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
                QMessageBox.information(self, "성공", "이미지 인쇄가 시작되었습니다.")
                print(f"[DEBUG] 인쇄 작업 시작됨")
            else:
                QMessageBox.critical(self, "오류", "인쇄 작업을 시작할 수 없습니다.")

    def pil_to_qimage(self, pil_image):
        """PIL 이미지를 QImage로 변환"""
        try:
            # PIL 이미지를 RGB로 변환
            if pil_image.mode == 'RGBA':
                background = PILImage.new('RGB', pil_image.size, (255, 255, 255))
                background.paste(pil_image, mask=pil_image.split()[-1])
                pil_image = background
            elif pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')

            # PIL 이미지를 바이트로 변환
            byte_array = io.BytesIO()
            pil_image.save(byte_array, format='PNG')
            byte_array.seek(0)

            # QImage로 로드
            qimage = QImage()
            qimage.loadFromData(byte_array.getvalue())

            return qimage

        except Exception as e:
            print(f"[DEBUG] PIL → QImage 변환 오류: {e}")
            return QImage()

    def reset_image(self):
        """사진 초기화 버튼을 눌렀을 때 실행되는 메서드"""
        if not any(file is not None for file in self.selected_files):
            return

        reply = QMessageBox.question(self, '사진 초기화 확인',
                                     "현재 선택된 사진들을 초기화하시겠습니까?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.No:
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
        self.status_message.setText("")

        # 버튼 상태 초기화
        self.process_button.setEnabled(False)
        self.print_button.setEnabled(False)

        print("사진들이 초기화되었습니다.")
        QMessageBox.information(self, "알림", "사진들이 초기화되었습니다.")

    def reset_application(self):
        """초기화 버튼을 눌렀을 때 실행되는 메서드"""
        reply = QMessageBox.question(self, '초기화 확인',
                                     "정말로 현재 작업을 초기화하시겠습니까?\n생성된 폴더와 파일은 삭제되지 않습니다.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.No:
            return

        # UI 초기화
        self.folder_input.clear()

        # 폴더 입력 필드 다시 활성화
        self.folder_input.setEnabled(True)
        self.folder_input.setStyleSheet("")

        self.folder_exists_label.setText("")
        self.new_folder_label.setText("")
        self.last_folder_time_label.setText("")

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
        self.status_message.setText("")

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
        QMessageBox.information(self, "알림", "모든 작업이 초기화되었습니다.")

    def close_application(self):
        reply = QMessageBox.question(self, '종료 확인',
                                     "정말로 종료하시겠습니까?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            print("애플리케이션 종료")
            sys.exit()


def run_multi_mode():
    """Multi 모드 실행 함수"""
    app = QApplication(sys.argv)
    window = MultiWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(run_multi_mode())