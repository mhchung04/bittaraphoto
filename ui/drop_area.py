"""
DropArea 위젯 모듈
Single/Multi 모드용 드롭 영역을 제공합니다.
"""

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from .drop_zone import DropZone
from .styles import Styles, Fonts, Colors


class SingleDropArea(QFrame):
    """Single 모드용 드롭 영역 (드롭존 1개)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.NoFrame)
        self.setLineWidth(0)
        # 한컷 모드용 크기 (MultiDropArea와 동일하게 맞춤)
        self.setMinimumSize(540, 260)
        self.setMaximumHeight(260)  # 최대 높이도 고정하여 확장 방지
        self.setAcceptDrops(False)

        self.setStyleSheet(f"""
            SingleDropArea {{
                background-color: #fafafa;
                border-radius: 10px;
                border: 1px solid {Colors.BORDER};
            }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 제목 라벨
        title_label = QLabel("이미지 드롭 영역 (1개) - 폴더 번호를 먼저 입력하세요")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"{Fonts.heading()}; color: {Colors.TEXT_PRIMARY}; margin-bottom: 8px;")
        main_layout.addWidget(title_label)

        # 상하 간격을 위한 스페이서 (Vertical Centering)
        main_layout.addStretch(1)

        # 단일 드롭존 (중앙 배치)
        zone_layout = QHBoxLayout()
        zone_layout.addStretch()

        self.zone1 = DropZone(0, self)
        zone_layout.addWidget(self.zone1)

        zone_layout.addStretch()
        main_layout.addLayout(zone_layout)

        # 하단 간격을 위한 스페이서 (Vertical Centering)
        main_layout.addStretch(1)

        # 파일 선택 버튼
        # 파일 선택 버튼
        self.select_btn = QPushButton("또는 파일 선택")
        self.select_btn.setFixedSize(140, 32)
        self.select_btn.setStyleSheet(Styles.BTN_SECONDARY)
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
        self.setMinimumSize(540, 260)  # 540x330 → 540x260
        self.setMaximumHeight(260)  # 최대 높이도 고정하여 확장 방지
        self.setAcceptDrops(False)

        self.setStyleSheet(f"""
            MultiDropArea {{
                background-color: #fafafa;
                border-radius: 10px;
                border: 1px solid {Colors.BORDER};
            }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 제목 라벨
        title_label = QLabel("이미지 드롭 영역 (4개) - 폴더 번호를 먼저 입력하세요")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"{Fonts.heading()}; color: {Colors.TEXT_PRIMARY}; margin-bottom: 8px;")
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
        main_layout.addSpacing(5)  # 상하 드롭존 사이 간격 축소

        # 하단 행
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(8)

        self.zone3 = DropZone(2, self)
        self.zone4 = DropZone(3, self)

        bottom_layout.addWidget(self.zone3)
        bottom_layout.addWidget(self.zone4)

        main_layout.addLayout(bottom_layout)

        # 파일 선택 버튼
        # 파일 선택 버튼
        self.select_btn = QPushButton("또는 파일 선택")
        self.select_btn.setFixedSize(140, 32)
        self.select_btn.setStyleSheet(Styles.BTN_SECONDARY)
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
