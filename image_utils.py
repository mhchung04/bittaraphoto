"""
이미지 처리 유틸리티 모듈
PIL과 Qt 간의 변환, 이미지 로드 등의 공통 기능을 제공합니다.
"""

import io
import os
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PIL import Image as PILImage


class ImageUtils:
    """이미지 처리 유틸리티 클래스"""

    @staticmethod
    def pil_to_qpixmap(pil_image):
        """PIL 이미지를 QPixmap으로 변환"""
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
                print("[ImageUtils] QImage 변환 실패")
                return QPixmap()

            # QPixmap으로 변환
            qpixmap = QPixmap.fromImage(qimage)
            print("[ImageUtils] PIL → QPixmap 변환 성공")
            return qpixmap

        except Exception as e:
            print(f"[ImageUtils] PIL → QPixmap 변환 오류: {e}")
            return QPixmap()

    @staticmethod
    def pil_to_qimage(pil_image):
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
            print(f"[ImageUtils] PIL → QImage 변환 오류: {e}")
            return QImage()

    @staticmethod
    def load_image_with_pil(image_path, target_width=None, target_height=None):
        """PIL을 통해 이미지를 로드하고 선택적으로 크기 조정"""
        try:
            print(f"[ImageUtils] PIL로 이미지 로드 시작: {image_path}")

            if not os.path.exists(image_path):
                print(f"[ImageUtils] 파일이 존재하지 않음: {image_path}")
                return None

            # PIL로 이미지 로드
            pil_image = PILImage.open(image_path)
            print(f"[ImageUtils] PIL 이미지 로드 성공, 원본 크기: {pil_image.size}")

            # 크기 조정이 요청된 경우
            if target_width and target_height:
                # 비율 유지하며 크기 조정
                pil_image.thumbnail((target_width, target_height), PILImage.Resampling.LANCZOS)
                print(f"[ImageUtils] PIL 리사이즈 완료: {pil_image.size}")

            return pil_image

        except Exception as e:
            print(f"[ImageUtils] 이미지 로드 오류: {e}")
            return None

    @staticmethod
    def load_image_as_qpixmap(image_path, target_width=None, target_height=None):
        """이미지를 PIL로 로드한 후 QPixmap으로 변환하여 반환"""
        pil_image = ImageUtils.load_image_with_pil(image_path, target_width, target_height)

        if pil_image is None:
            return QPixmap()

        return ImageUtils.pil_to_qpixmap(pil_image)

    @staticmethod
    def load_image_as_qimage(image_path, target_width=None, target_height=None):
        """이미지를 PIL로 로드한 후 QImage로 변환하여 반환"""
        pil_image = ImageUtils.load_image_with_pil(image_path, target_width, target_height)

        if pil_image is None:
            return QImage()

        return ImageUtils.pil_to_qimage(pil_image)

    @staticmethod
    def is_valid_image_file(file_path):
        """유효한 이미지 파일인지 확인"""
        if not file_path or not os.path.exists(file_path):
            return False

        valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
        return file_path.lower().endswith(valid_extensions)

    @staticmethod
    def get_image_info(image_path):
        """이미지 파일의 기본 정보 반환"""
        try:
            if not ImageUtils.is_valid_image_file(image_path):
                return None

            with PILImage.open(image_path) as img:
                return {
                    'size': img.size,
                    'mode': img.mode,
                    'format': img.format,
                    'filename': os.path.basename(image_path)
                }
        except Exception as e:
            print(f"[ImageUtils] 이미지 정보 조회 오류: {e}")
            return None