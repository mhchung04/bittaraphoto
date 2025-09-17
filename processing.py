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


def insert_images_into_frame(photo_regions: List[Tuple[str, Tuple[int, int, int, int]]], frame_path: str,
                             output_path: str) -> None:
    """
    프레임 이미지의 투명 영역에 여러 사진을 자동 맞춤 삽입 후, PNG 무손실 또는 JPEG 최고 품질로 저장합니다.

    Parameters:
    - photo_regions: [(photo_path, (left_x, top_y, right_x, bottom_y)), ...] 형태의 리스트
    - frame_path: 프레임 이미지 경로
    - output_path: 결과 이미지 저장 경로
    """
    print(f"[DEBUG] insert_images_into_frame 시작")
    print(f"[DEBUG] 프레임 경로: {frame_path}")
    print(f"[DEBUG] 출력 경로: {output_path}")
    print(f"[DEBUG] 사진 영역 수: {len(photo_regions)}")

    # 프레임 이미지 불러오기
    frame = Image.open(frame_path).convert('RGBA')
    frame_w, frame_h = frame.size
    print(f"[DEBUG] 프레임 크기: {frame_w}x{frame_h}")

    # 새 캔버스 생성
    base = Image.new('RGBA', (frame_w, frame_h))

    # 각 사진을 해당 영역에 삽입
    for i, (photo_path, region) in enumerate(photo_regions):
        print(f"[DEBUG] 사진 {i + 1} 처리: {photo_path}")
        left_x, top_y, right_x, bottom_y = region
        print(f"[DEBUG] 영역 좌표: ({left_x}, {top_y}, {right_x}, {bottom_y})")

        # right_x가 None인 경우 처리 (기존 호환성)
        if right_x is None:
            right_x = frame_w - left_x
        region_w = right_x - left_x
        region_h = bottom_y - top_y
        print(f"[DEBUG] 영역 크기: {region_w}x{region_h}")

        # 사진 불러오기 및 크기 맞추기
        photo = Image.open(photo_path).convert('RGBA')
        print(f"[DEBUG] 원본 사진 크기: {photo.size}")
        fitted = fit_image_to_region(photo, (region_w, region_h))
        print(f"[DEBUG] 맞춤 사진 크기: {fitted.size}")

        # 해당 위치에 사진 삽입
        base.paste(fitted, (left_x, top_y))
        print(f"[DEBUG] 사진 {i + 1} 삽입 완료")

    # 프레임을 최상단에 합성
    base.paste(frame, (0, 0), frame)
    print(f"[DEBUG] 프레임 합성 완료")

    # 파일 확장자에 따른 저장 옵션
    ext = os.path.splitext(output_path)[1].lower()
    if ext in ('.jpg', '.jpeg'):
        base.convert('RGB').save(
            output_path,
            format='JPEG',
            quality=100,
            subsampling=0,
            optimize=True
        )
    else:
        base.save(
            output_path,
            format='PNG',
            compress_level=0
        )

    print(f"[DEBUG] 저장 완료: {output_path}")


def insert_image_into_frame(photo_path: str, frame_path: str, output_path: str, left_x: int = 30, top_y: int = 30,
                            right_x: int = None, bottom_y: int = 1050) -> None:
    """
    기존 단일 이미지 삽입 함수 (하위 호환성을 위한 래퍼 함수)
    """
    # 단일 이미지를 리스트 형태로 변환하여 새 함수 호출
    photo_regions = [(photo_path, (left_x, top_y, right_x, bottom_y))]
    insert_images_into_frame(photo_regions, frame_path, output_path)


if __name__ == '__main__':
    # 4개 이미지 사용 예시 (정확한 01.png 좌표)
    photo_regions = [
        ('./img1.jpg', (63, 66, 1757, 1195)),  # 1번 영역
        ('./img2.jpg', (1796, 66, 3490, 1195)),  # 2번 영역
        ('./img3.jpg', (63, 1229, 1757, 2358)),  # 3번 영역
        ('./img4.jpg', (1796, 1826, 3490, 2955))  # 4번 영역
    ]
    insert_images_into_frame(photo_regions, './frame/01.png', 'result_multi.png')