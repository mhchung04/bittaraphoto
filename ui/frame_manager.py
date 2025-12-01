import json
import os

class FrameManager:
    """프레임 데이터 관리 클래스 (JSON 연동)"""
    def __init__(self, filepath='frames.json'):
        self.filepath = filepath
        self.frames = []
        self.load_frames()

    def load_frames(self):
        """JSON 파일에서 프레임 데이터 로드"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.frames = json.load(f)
            except Exception as e:
                print(f"프레임 데이터 로드 실패: {e}")
                self.frames = []
        else:
            self.frames = []

    def save_frames(self):
        """프레임 데이터를 JSON 파일로 저장"""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.frames, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"프레임 데이터 저장 실패: {e}")

    def get_all_frames(self):
        return self.frames

    def get_frame_by_name(self, name):
        for frame in self.frames:
            if frame['name'] == name:
                return frame
        return None

    def add_frame(self, frame_data):
        self.frames.append(frame_data)
        # self.save_frames() # 자동 저장 제거

    def update_frame(self, index, frame_data):
        if 0 <= index < len(self.frames):
            self.frames[index] = frame_data
            # self.save_frames() # 자동 저장 제거

    def delete_frame(self, index):
        if 0 <= index < len(self.frames):
            del self.frames[index]
            # self.save_frames() # 자동 저장 제거

    def set_frames(self, frames):
        """프레임 리스트 전체 업데이트"""
        self.frames = frames
