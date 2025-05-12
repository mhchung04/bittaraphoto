import os
from PIL import Image
from typing import List, Tuple, Union


def fit_image_to_region(img: Image.Image, region_size: tuple[int, int]) -> Image.Image:
    """
    사진 이미지를 지정된 영역 크기(region_size)에 맞춰 비율 유지하며 확대/축소 후 중앙에서 Crop 합니다.
    """
    target_w, target_h = region_size
    w, h = img.size
    scale = max(target_w / w, target_h / h)
    new_size = (int(w * scale), int(h * scale))
    resized = img.resize(new_size, Image.LANCZOS)
    left = (new_size[0] - target_w) // 2
    top = (new_size[1] - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def insert_images_into_frame(photo_regions: List[Tuple[str, Tuple[int, int, int, int]]],
                             frame_path: str, output_path: str) -> None:
    """
    프레임 이미지의 투명 영역에 여러 사진을 자동 맞춤 삽입 후, PNG 무손실 또는 JPEG 최고 품질로 저장합니다.

    Parameters:
    - photo_regions: [(photo_path, (left_x, top_y, right_x, bottom_y)), ...] 형태의 리스트
    - frame_path: 프레임 이미지 경로
    - output_path: 결과 이미지 저장 경로
    """
    # 프레임 이미지 불러오기
    frame = Image.open(frame_path).convert('RGBA')
    frame_w, frame_h = frame.size

    # 새 캔버스 생성
    base = Image.new('RGBA', (frame_w, frame_h))

    # 각 사진을 해당 영역에 삽입
    for photo_path, region in photo_regions:
        left_x, top_y, right_x, bottom_y = region

        # right_x가 None인 경우 처리 (기존 호환성)
        if right_x is None:
            right_x = frame_w - left_x

        region_w = right_x - left_x
        region_h = bottom_y - top_y

        # 사진 불러오기 및 크기 맞추기
        photo = Image.open(photo_path).convert('RGBA')
        fitted = fit_image_to_region(photo, (region_w, region_h))

        # 해당 위치에 사진 삽입
        base.paste(fitted, (left_x, top_y))

    # 프레임을 최상단에 합성
    base.paste(frame, (0, 0), frame)

    # 파일 확장자에 따른 저장 옵션
    ext = os.path.splitext(output_path)[1].lower()
    if ext in ('.jpg', '.jpeg'):
        base.convert('RGB').save(
            output_path, format='JPEG', quality=100, subsampling=0, optimize=True
        )
    else:
        base.save(
            output_path, format='PNG', compress_level=0
        )
    print(f"Saved result to {output_path}")


def insert_image_into_frame(photo_path: str, frame_path: str, output_path: str,
                            left_x: int = 30, top_y: int = 30, right_x: int = None, bottom_y: int = 1050) -> None:
    """
    기존 단일 이미지 삽입 함수 (하위 호환성을 위한 래퍼 함수)

    Parameters:
    - photo_path: 원본 사진 경로
    - frame_path: 프레임 이미지 경로
    - output_path: 결과 이미지 저장 경로
    - left_x: 투명 영역 좌측 X 좌표
    - top_y: 투명 영역 상단 Y 좌표
    - right_x: 투명 영역 우측 X 좌표 (None이면 frame_w - left_x로 계산)
    - bottom_y: 투명 영역 하단 Y 좌표
    """
    # 단일 이미지를 리스트 형태로 변환하여 새 함수 호출
    photo_regions = [(photo_path, (left_x, top_y, right_x, bottom_y))]
    insert_images_into_frame(photo_regions, frame_path, output_path)


if __name__ == '__main__':
    # 단일 이미지 사용 예시 (기존 방식)
    insert_image_into_frame('./img.jpg', './frame/01.png', 'result_single.png')

    # 4개 이미지 사용 예시 (새로운 방식)
    photo_regions = [
        ('./img1.jpg', (30, 30, 500, 400)),
        ('./img2.jpg', (530, 30, 1000, 400)),
        ('./img3.jpg', (30, 430, 500, 800)),
        ('./img4.jpg', (530, 430, 1000, 800))
    ]
    insert_images_into_frame(photo_regions, './frame/01.png', 'result_multi.png')