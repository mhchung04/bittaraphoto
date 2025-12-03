"""
DropZone 위젯 모듈
개별 드롭 존의 UI와 드래그&드롭 로직을 담당합니다.
"""

import os
from PyQt5.QtWidgets import QLabel, QMessageBox, QFrame, QVBoxLayout, QSizePolicy, QPushButton
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QImage
from PyQt5.QtCore import Qt, QRect
from PIL import Image as PILImage
from .styles import Styles, Colors, Fonts
from .toast_message import ToastMessage

class ImageUtils:
    """이미지 변환 및 처리 유틸리티 클래스"""

    @staticmethod
    def pil_to_qpixmap(pil_image):
        """PIL 이미지를 QPixmap으로 변환"""
        try:
            import io
            
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
            return qpixmap

        except Exception as e:
            print(f"[DEBUG] ImageUtils: PIL → QPixmap 변환 오류: {e}")
            return QPixmap()


class DropZone(QFrame):
    """개별 드롭 존 (이미지 + 파일명)"""

    def __init__(self, zone_id, parent_drop_area):
        super().__init__()
        self.zone_id = zone_id
        self.parent_drop_area = parent_drop_area
        self.setAcceptDrops(True)
        self.image_path = None

        # 기본 설정
        self.setMinimumSize(130, 90) # 최소 크기 설정
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.setObjectName("dropZone")
        
        # 레이아웃 설정 - 이미지 공간 확보를 위해 여백 최소화
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(2)
        
        # 이미지/번호 표시 라벨
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.image_label)
        
        self.filename_label = QLabel()
        self.filename_label.setAlignment(Qt.AlignCenter)
        self.filename_label.setFont(QFont(Fonts.FAMILY, 9))
        self.filename_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        self.filename_label.setWordWrap(True)
        self.filename_label.setFixedHeight(20) # 높이 축소하여 이미지 공간 확보
        self.layout.addWidget(self.filename_label)

        # 삭제 버튼 (우측 상단)
        self.delete_btn = QPushButton("✕", self)
        self.delete_btn.setFixedSize(24, 24)
        self.delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(0, 0, 0, 0.5);
                color: white;
                border-radius: 12px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {Colors.DESTRUCTIVE};
            }}
        """)
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        self.delete_btn.hide()
        self.delete_btn.clicked.connect(self.delete_image)
        
        # 버튼을 항상 최상위에 표시
        self.delete_btn.raise_()

        # 초기 상태 설정
        self.reset_to_default()

    def check_folder_validation(self):
        """폴더 번호 유효성 검사"""
        if not hasattr(self.parent_drop_area.parent_window, 'folder_input'):
            return False

        folder_number_text = self.parent_drop_area.parent_window.folder_input.text().strip()
        if not folder_number_text:
            return False

        return True

    def set_image(self, image_path):
        """이미지 설정 및 미리보기 표시"""
        self.image_path = image_path

        if not image_path or not os.path.exists(image_path):
            self.reset_to_default()
            return

        try:
            # PIL로 이미지 로드 및 리사이즈
            pil_image = PILImage.open(image_path)
            
            # 미리보기 크기 계산 (라벨 크기에 맞춤)
            target_width = self.image_label.width()
            target_height = self.image_label.height()
            if target_width <= 0: target_width = 130
            if target_height <= 0: target_height = 90
            
            pil_image.thumbnail((target_width, target_height), PILImage.Resampling.LANCZOS)
            
            # QPixmap 변환
            pixmap = ImageUtils.pil_to_qpixmap(pil_image)
            
            if pixmap.isNull():
                self.reset_to_default()
                return

            # 이미지 설정 (rounded corners effect)
            self.image_label.setPixmap(pixmap)
            self.image_label.setText("") # 텍스트 제거
            self.image_label.setStyleSheet("""
                QLabel {
                    border-radius: 6px;
                    background-color: transparent;
                }
            """)
            
            # 파일명 설정 - 더 세련된 스타일 (배경 제거하여 깔끔하게)
            filename = os.path.basename(image_path)
            self.filename_label.setText(filename)
            self.filename_label.setStyleSheet(f"""
                QLabel {{
                    color: {Colors.TEXT_PRIMARY};
                    font-weight: 600;
                    font-size: 11px;
                    background-color: transparent;
                    padding: 2px;
                }}
            """)

            # 스타일 업데이트 (성공) - 모던한 디자인
            self.setStyleSheet(f"""
                #dropZone {{
                    border: 2px solid {Colors.SUCCESS};
                    border-radius: 12px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                stop:0 #F1F8F4, stop:1 #E8F5E9);
                    padding: 8px;
                }}
            """)
            
            # 삭제 버튼 표시 및 위치 조정
            self.delete_btn.show()
            self.delete_btn.raise_()
            # 위치는 resizeEvent에서 조정되지만, 여기서도 한 번 잡아줌
            self.update_delete_btn_position()

        except Exception as e:
            print(f"[DEBUG] Zone {self.zone_id}: 이미지 처리 중 오류: {e}")
            self.reset_to_default()

    def reset_to_default(self):
        """기본 상태로 리셋"""
        self.image_path = None
        self.image_label.setPixmap(QPixmap())
        self.image_label.setText(f"{self.zone_id + 1}")
        self.image_label.setFont(QFont(Fonts.FAMILY, 36, QFont.Bold))
        self.image_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_HINT};
                border: none;
                background-color: transparent;
            }}
        """)
        
        self.filename_label.setText("이미지 드롭")
        self.filename_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_HINT};
                font-size: 11px;
                background-color: transparent;
            }}
        """)

        # 스타일 업데이트 (기본) - 부드러운 디자인
        self.setStyleSheet(f"""
            #dropZone {{
                border: 2px dashed {Colors.BORDER};
                border-radius: 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #FAFAFA, stop:1 #F5F5F5);
            }}
        """)
        
        # 삭제 버튼 숨기기
        if hasattr(self, 'delete_btn'):
            self.delete_btn.hide()

    def dragEnterEvent(self, event):
        if hasattr(self.parent_drop_area.parent_window,
                   'processed_file') and self.parent_drop_area.parent_window.processed_file:
            event.ignore()
            return

        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(f"""
                #dropZone {{
                    border: 2px solid {Colors.PRIMARY};
                    border-radius: 12px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                stop:0 #E3F2FD, stop:1 #BBDEFB);
                    padding: 8px;
                }}
            """)
        
        # 삭제 버튼 숨기기
        if hasattr(self, 'delete_btn'):
            self.delete_btn.hide()

    def delete_image(self):
        """이미지 삭제 처리"""
        if self.image_path:
            self.reset_to_default()
            # 메인 윈도우에 알림
            if hasattr(self.parent_drop_area.parent_window, 'remove_image'):
                self.parent_drop_area.parent_window.remove_image(self.zone_id)

    def resizeEvent(self, event):
        """크기 변경 시 삭제 버튼 위치 조정"""
        super().resizeEvent(event)
        if hasattr(self, 'delete_btn'):
            self.update_delete_btn_position()
            
    def update_delete_btn_position(self):
        """삭제 버튼을 우측 상단에 배치"""
        padding = 5
        self.delete_btn.move(self.width() - self.delete_btn.width() - padding, padding)

    def dragLeaveEvent(self, event):
        if self.image_path:
            # 이미지가 있는 경우 성공 스타일 복구
            self.setStyleSheet(f"""
                #dropZone {{
                    border: 2px solid {Colors.SUCCESS};
                    border-radius: 12px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                stop:0 #F1F8F4, stop:1 #E8F5E9);
                    padding: 8px;
                }}
            """)
            
            # 삭제 버튼 다시 표시
            if hasattr(self, 'delete_btn'):
                self.delete_btn.show()
                self.delete_btn.raise_()
        else:
            # 이미지가 없는 경우 기본 스타일 복구
            self.setStyleSheet(f"""
                #dropZone {{
                    border: 2px dashed {Colors.BORDER};
                    border-radius: 12px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                stop:0 #FAFAFA, stop:1 #F5F5F5);
                }}
            """)

    def dropEvent(self, event):
        # 1. 가공 상태 확인
        if hasattr(self.parent_drop_area.parent_window,
                   'processed_file') and self.parent_drop_area.parent_window.processed_file:
            ToastMessage.show_toast(self.parent_drop_area.parent_window, 
                                    "이미 이미지 가공이 완료되었습니다. '사진 초기화'를 먼저 해주세요.", 
                                    type="warning", 
                                    anchor_widget=self.parent_drop_area.parent_window.reset_image_button)
            event.ignore()
            return

        # 2. 폴더 번호 유효성 검사
        if not self.check_folder_validation():
            ToastMessage.show_toast(self.parent_drop_area.parent_window, 
                                    "폴더 번호를 먼저 입력해주세요.", 
                                    type="warning", 
                                    anchor_widget=self.parent_drop_area.parent_window.folder_input,
                                    center_x=True)
            self.dragLeaveEvent(event)
            event.ignore()
            return

        # 3. URL 데이터 처리
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                    self.set_image(file_path)
                    
                    if hasattr(self.parent_drop_area.parent_window, 'prepare_image'):
                        self.parent_drop_area.parent_window.prepare_image(file_path, self.zone_id)
                    break
            
            event.acceptProposedAction()
