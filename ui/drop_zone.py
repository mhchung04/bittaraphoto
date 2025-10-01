"""
DropZone 위젯 모듈
개별 드롭 존의 UI와 드래그&드롭 로직을 담당합니다.
"""

import os
from PyQt5.QtWidgets import QLabel, QMessageBox
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt, QRect
from PIL import Image as PILImage


class ImageUtils:
    """이미지 변환 및 처리 유틸리티 클래스"""

    @staticmethod
    def pil_to_qpixmap(pil_image):
        """PIL 이미지를 QPixmap으로 변환"""
        try:
            import io
            from PyQt5.QtGui import QImage
            
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
