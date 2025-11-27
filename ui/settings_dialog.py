import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QLabel, QLineEdit, QPushButton, QMessageBox, 
                             QComboBox, QWidget, QScrollArea, QFormLayout,
                             QSpinBox, QGroupBox, QGridLayout, QFileDialog,
                             QTabWidget, QListWidgetItem, QSplitter)
from PyQt5.QtCore import Qt, QSize, QRect, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QIcon
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QIcon
from PIL import Image
from .styles import Styles, Colors, Fonts
from .message_box import MessageBox

class RegionInputWidget(QGroupBox):
    """개별 영역 좌표 입력 위젯 (박스 형태) - Compact"""
    def __init__(self, index, region=None, parent_dialog=None):
        super().__init__(f"영역 {index + 1}")
        self.parent_dialog = parent_dialog
        self.setStyleSheet(Styles.GROUP_BOX)
        
        layout = QGridLayout()
        layout.setContentsMargins(5, 15, 5, 5)
        layout.setSpacing(5)
        
        self.x1 = QSpinBox(); self.x1.setRange(0, 10000); self.x1.setPrefix("X1: "); self.x1.setStyleSheet(Styles.INPUT)
        self.y1 = QSpinBox(); self.y1.setRange(0, 10000); self.y1.setPrefix("Y1: "); self.y1.setStyleSheet(Styles.INPUT)
        self.x2 = QSpinBox(); self.x2.setRange(0, 10000); self.x2.setPrefix("X2: "); self.x2.setStyleSheet(Styles.INPUT)
        self.y2 = QSpinBox(); self.y2.setRange(0, 10000); self.y2.setPrefix("Y2: "); self.y2.setStyleSheet(Styles.INPUT)

        for spin in [self.x1, self.y1, self.x2, self.y2]:
            spin.valueChanged.connect(self.on_value_changed)

        if region:
            self.x1.setValue(region[0])
            self.y1.setValue(region[1])
            self.x2.setValue(region[2])
            self.y2.setValue(region[3])

        layout.addWidget(self.x1, 0, 0)
        layout.addWidget(self.y1, 0, 1)
        layout.addWidget(self.x2, 1, 0)
        layout.addWidget(self.y2, 1, 1)
        
        self.setLayout(layout)

    def on_value_changed(self):
        if self.parent_dialog:
            self.parent_dialog.update_preview()

    def get_values(self):
        return [self.x1.value(), self.y1.value(), self.x2.value(), self.y2.value()]

    def set_values(self, region):
        self.x1.blockSignals(True)
        self.y1.blockSignals(True)
        self.x2.blockSignals(True)
        self.y2.blockSignals(True)
        
        self.x1.setValue(region[0])
        self.y1.setValue(region[1])
        self.x2.setValue(region[2])
        self.y2.setValue(region[3])
        
        self.x1.blockSignals(False)
        self.y1.blockSignals(False)
        self.x2.blockSignals(False)
        self.y2.blockSignals(False)


class FramePreviewWidget(QLabel):
    """프레임 미리보기 및 영역 표시 위젯"""
    regionClicked = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: #e0e0e0; border: 1px solid #999;")
        self.setMinimumSize(300, 200) # 최소 크기 조정
        self.regions = []
        self.original_pixmap = None
        self.scaled_pixmap = None
        self.scale_factor_x = 1.0
        self.scale_factor_y = 1.0

    def set_image(self, image_path):
        if image_path and os.path.exists(image_path):
            self.original_pixmap = QPixmap(image_path)
        else:
            self.original_pixmap = None
        self.update_display()

    def set_regions(self, regions):
        self.regions = regions
        self.update_display()

    def update_display(self):
        if not self.original_pixmap:
            self.setText("이미지 없음")
            return

        # 뷰어 크기
        view_size = self.size()
        if view_size.width() < 10 or view_size.height() < 10:
            return

        # 원본 비율 유지하며 뷰어에 맞춤
        scaled_pixmap = self.original_pixmap.scaled(view_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # 그리기 도구 준비
        painter = QPainter(scaled_pixmap)
        
        # 좌표 변환 비율 계산
        scale_x = scaled_pixmap.width() / self.original_pixmap.width()
        scale_y = scaled_pixmap.height() / self.original_pixmap.height()
        
        # 영역 그리기
        colors = [Qt.red, Qt.blue, Qt.green, Qt.magenta]
        for i, region in enumerate(self.regions):
            x1, y1, x2, y2 = region
            
            # 좌표 스케일링
            sx1 = int(x1 * scale_x)
            sy1 = int(y1 * scale_y)
            sx2 = int(x2 * scale_x)
            sy2 = int(y2 * scale_y)
            
            w = sx2 - sx1
            h = sy2 - sy1
            
            color = colors[i % len(colors)]
            pen = QPen(color)
            pen.setWidth(3) # 선 두께 조정
            painter.setPen(pen)
            
            # 반투명 채우기
            fill_color = QColor(color)
            fill_color.setAlpha(50)
            painter.setBrush(fill_color)
            
            painter.drawRect(sx1, sy1, w, h)
            
            # 번호 표시
            painter.setPen(Qt.black)
            font = painter.font()
            font.setPointSize(20) # 폰트 크기 조정
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(sx1 + 5, sy1 + 25, str(i + 1))

        painter.end()
        self.setPixmap(scaled_pixmap)
        
        # 클릭 이벤트 처리를 위해 저장
        self.scaled_pixmap = scaled_pixmap
        self.scale_factor_x = scale_x
        self.scale_factor_y = scale_y

    def mousePressEvent(self, event):
        if not self.original_pixmap or not self.regions:
            return

        # 클릭 위치 (위젯 기준)
        pos = event.pos()
        
        # 이미지의 실제 그려진 영역 계산 (QLabel 중앙 정렬 고려)
        if self.scaled_pixmap:
            pix_rect = self.scaled_pixmap.rect()
            # QLabel 내에서 pixmap이 그려지는 오프셋 계산 (Center 정렬)
            x_offset = (self.width() - pix_rect.width()) / 2
            y_offset = (self.height() - pix_rect.height()) / 2
            
            # 이미지 내부 좌표로 변환
            img_x = (pos.x() - x_offset) / self.scale_factor_x
            img_y = (pos.y() - y_offset) / self.scale_factor_y
            
            # 영역 확인 (역순으로 확인하여 위에 그려진 것부터 감지)
            for i in reversed(range(len(self.regions))):
                r = self.regions[i]
                if r[0] <= img_x <= r[2] and r[1] <= img_y <= r[3]:
                    self.regionClicked.emit(i)
                    return

    def resizeEvent(self, event):
        self.update_display()
        super().resizeEvent(event)


class SettingsDialog(QDialog):
    """설정 및 프레임 관리 통합 다이얼로그"""
    def __init__(self, frame_manager, parent=None):
        super().__init__(parent)
        self.frame_manager = frame_manager
        self.setWindowTitle("설정")
        self.resize(850, 600) # 컴팩트 사이즈
        
        layout = QVBoxLayout()
        
        # 탭 위젯
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(Styles.TAB_WIDGET)
        self.tabs.addTab(self.create_general_tab(), "일반")
        self.tabs.addTab(self.create_frame_tab(), "프레임 설정")
        
        layout.addWidget(self.tabs)
        
        # 하단 닫기 버튼
        close_btn = QPushButton("닫기")
        close_btn.setStyleSheet(Styles.BTN_SECONDARY)
        close_btn.clicked.connect(self.accept)
        close_btn.setFixedWidth(100)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        # 초기화
        self.region_widgets = []
        self.refresh_frame_list()

    def create_general_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("일반 설정 (준비 중)"))
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget

    def create_frame_tab(self):
        widget = QWidget()
        main_layout = QVBoxLayout()
        
        # --- 상단 툴바 (저장/취소) ---
        toolbar_layout = QHBoxLayout()
        toolbar_layout.addStretch()
        
        self.save_btn = QPushButton("💾 저장")
        self.save_btn.setToolTip("변경사항을 파일에 저장합니다")
        self.save_btn.setStyleSheet(Styles.BTN_PRIMARY)
        self.save_btn.clicked.connect(self.save_changes)
        
        self.cancel_btn = QPushButton("↩ 취소")
        self.cancel_btn.setToolTip("변경사항을 취소하고 다시 불러옵니다")
        self.cancel_btn.setStyleSheet(Styles.BTN_SECONDARY)
        self.cancel_btn.clicked.connect(self.cancel_changes)
        
        toolbar_layout.addWidget(self.save_btn)
        toolbar_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(toolbar_layout)
        
        # --- 상단: 정보/미리보기 (좌) vs 좌표설정 (우) ---
        top_splitter = QSplitter(Qt.Horizontal)
        
        # [좌측 패널] 정보 + 미리보기
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 1. 기본 정보 그룹
        info_group = QGroupBox("기본 정보")
        info_group.setStyleSheet(Styles.GROUP_BOX)
        info_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setStyleSheet(Styles.INPUT)
        self.name_edit.textChanged.connect(self.save_current_frame_info)
        
        file_layout = QHBoxLayout()
        self.filename_edit = QLineEdit()
        self.filename_edit.setReadOnly(True)
        self.filename_edit.setStyleSheet(Styles.INPUT)
        self.filename_edit.textChanged.connect(self.on_filename_changed)
        
        self.browse_btn = QPushButton("찾기...")
        self.browse_btn.setStyleSheet(Styles.BTN_SECONDARY)
        self.browse_btn.clicked.connect(self.browse_file)
        
        file_layout.addWidget(self.filename_edit)
        file_layout.addWidget(self.browse_btn)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["four_cut", "single_cut"])
        self.type_combo.setStyleSheet(Styles.INPUT)
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        
        info_layout.addRow("이름:", self.name_edit)
        info_layout.addRow("파일명:", file_layout)
        info_layout.addRow("타입:", self.type_combo)
        info_group.setLayout(info_layout)
        left_layout.addWidget(info_group)
        
        # 2. 미리보기 그룹
        preview_group = QGroupBox("미리보기")
        preview_group.setStyleSheet(Styles.GROUP_BOX)
        preview_layout = QVBoxLayout()
        
        self.preview_widget = FramePreviewWidget()
        self.preview_widget.regionClicked.connect(self.highlight_input_widget)
        preview_layout.addWidget(self.preview_widget)
        
        preview_group.setLayout(preview_layout)
        left_layout.addWidget(preview_group, 1) # Stretch
        
        left_panel.setLayout(left_layout)
        
        # [우측 패널] 좌표 설정
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.regions_group = QGroupBox("영역 좌표 설정")
        self.regions_group.setStyleSheet(Styles.GROUP_BOX)
        self.regions_layout = QGridLayout()
        self.regions_container = QWidget()
        self.regions_container.setLayout(self.regions_layout)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.regions_container)
        scroll.setStyleSheet(Styles.SCROLL_AREA)
        
        regions_main_layout = QVBoxLayout()
        
        # 자동 인식 버튼 (우측으로 이동)
        self.auto_detect_btn = QPushButton("투명 영역 자동 인식")
        self.auto_detect_btn.setStyleSheet(Styles.BTN_PRIMARY)
        self.auto_detect_btn.clicked.connect(self.auto_detect_regions)
        regions_main_layout.addWidget(self.auto_detect_btn)
        
        regions_main_layout.addWidget(scroll)
        
        # 영역 추가/삭제 버튼
        region_btn_layout = QHBoxLayout()
        self.add_region_btn = QPushButton("영역 추가")
        self.add_region_btn.setStyleSheet(Styles.BTN_SECONDARY)
        self.add_region_btn.clicked.connect(lambda: self.add_region_input(None))
        
        self.remove_region_btn = QPushButton("삭제")
        self.remove_region_btn.setStyleSheet(Styles.BTN_DESTRUCTIVE)
        self.remove_region_btn.clicked.connect(self.remove_last_region)
        
        region_btn_layout.addWidget(self.add_region_btn)
        region_btn_layout.addWidget(self.remove_region_btn)
        regions_main_layout.addLayout(region_btn_layout)
        
        self.regions_group.setLayout(regions_main_layout)
        right_layout.addWidget(self.regions_group)
        
        right_panel.setLayout(right_layout)
        
        top_splitter.addWidget(left_panel)
        top_splitter.addWidget(right_panel)
        top_splitter.setStretchFactor(0, 1) # 좌측(미리보기) 비율 축소
        top_splitter.setStretchFactor(1, 2) # 우측(좌표) 비율 확대
        
        main_layout.addWidget(top_splitter, 1) # 상단 영역 Stretch
        
        # --- 하단: 프레임 목록 (가로 스크롤) ---
        bottom_group = QGroupBox("프레임 목록")
        bottom_group.setStyleSheet(Styles.GROUP_BOX)
        bottom_layout = QVBoxLayout()
        
        # 목록 컨트롤 (추가/삭제)
        list_ctrl_layout = QHBoxLayout()
        list_ctrl_layout.addStretch()
        self.add_btn = QPushButton("프레임 추가")
        self.add_btn.setStyleSheet(Styles.BTN_SECONDARY)
        self.add_btn.clicked.connect(self.add_new_frame)
        
        self.del_btn = QPushButton("선택 삭제")
        self.del_btn.setStyleSheet(Styles.BTN_DESTRUCTIVE)
        self.del_btn.clicked.connect(self.delete_current_frame)
        
        list_ctrl_layout.addWidget(self.add_btn)
        list_ctrl_layout.addWidget(self.del_btn)
        bottom_layout.addLayout(list_ctrl_layout)
        
        # 리스트 위젯
        self.frame_list = QListWidget()
        self.frame_list.setIconSize(QSize(80, 80))
        self.frame_list.setViewMode(QListWidget.IconMode)
        self.frame_list.setFlow(QListWidget.LeftToRight) # 가로 배치
        self.frame_list.setWrapping(False) # 줄바꿈 없음 (가로 스크롤)
        self.frame_list.setResizeMode(QListWidget.Adjust)
        self.frame_list.setStyleSheet(Styles.LIST_WIDGET)
        self.frame_list.setSpacing(10)
        self.frame_list.setFixedHeight(130) # 높이 고정
        self.frame_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.frame_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.frame_list.currentRowChanged.connect(self.load_selected_frame)
        
        bottom_layout.addWidget(self.frame_list)
        bottom_group.setLayout(bottom_layout)
        
        main_layout.addWidget(bottom_group)
        
        widget.setLayout(main_layout)
        return widget

    def refresh_frame_list(self):
        self.frame_list.clear()
        frames = self.frame_manager.get_all_frames()
        for frame in frames:
            item = QListWidgetItem(frame['name'])
            # 썸네일 로드 시도
            frame_path = os.path.join(os.getcwd(), 'frame', frame['filename'])
            icon = None
            if os.path.exists(frame_path):
                pixmap = QPixmap(frame_path)
                if not pixmap.isNull():
                    icon = QIcon(pixmap)
            
            # 아이콘이 없으면 기본 아이콘 생성 (텍스트 정렬을 위해)
            if icon is None:
                pixmap = QPixmap(80, 80)
                pixmap.fill(Qt.lightGray)
                painter = QPainter(pixmap)
                painter.setPen(Qt.black)
                painter.drawText(pixmap.rect(), Qt.AlignCenter, "No Image")
                painter.end()
                icon = QIcon(pixmap)
                
            item.setIcon(icon)
            self.frame_list.addItem(item)

    def load_selected_frame(self, row):
        if row < 0:
            return
            
        frames = self.frame_manager.get_all_frames()
        frame = frames[row]
        
        # UI 업데이트 시 시그널 차단 방지
        self.name_edit.blockSignals(True)
        self.filename_edit.blockSignals(True)
        self.type_combo.blockSignals(True)
        
        self.name_edit.setText(frame['name'])
        self.filename_edit.setText(frame['filename'])
        
        index = self.type_combo.findText(frame.get('type', 'four_cut'))
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
            
        self.name_edit.blockSignals(False)
        self.filename_edit.blockSignals(False)
        self.type_combo.blockSignals(False)
            
        # 영역 로드
        self.clear_regions()
        regions = frame.get('regions', [])
        for i, region in enumerate(regions):
            self.add_region_input(region)
            
        self.rearrange_regions()
        self.update_preview()

    def on_filename_changed(self):
        self.save_current_frame_info()
        self.update_preview()

    def update_preview(self):
        filename = self.filename_edit.text()
        if not filename:
            self.preview_widget.set_image(None)
            return

        filepath = os.path.join(os.getcwd(), 'frame', filename)
        self.preview_widget.set_image(filepath)
        
        # 현재 입력된 좌표값 가져오기
        current_regions = [w.get_values() for w in self.region_widgets]
        self.preview_widget.set_regions(current_regions)
        
        # 변경사항 자동 저장 (선택적)
        self.save_current_frame_info()

    def clear_regions(self):
        # 기존 위젯을 레이아웃에서 즉시 제거하고 숨김 처리
        for widget in self.region_widgets:
            self.regions_layout.removeWidget(widget)
            widget.setParent(None) # 즉시 부모 연결 해제
            widget.deleteLater()
        self.region_widgets = []
        
        # 레이아웃 강제 갱신
        self.regions_container.update()

    def add_region_input(self, region=None):
        index = len(self.region_widgets)
        widget = RegionInputWidget(index, region, self)
        self.region_widgets.append(widget)
        self.rearrange_regions()
        self.update_preview()

    def remove_last_region(self):
        if self.region_widgets:
            widget = self.region_widgets.pop()
            self.regions_layout.removeWidget(widget)
            widget.deleteLater()
            self.rearrange_regions()
            self.update_preview()

    def rearrange_regions(self):
        for i in reversed(range(self.regions_layout.count())): 
            self.regions_layout.itemAt(i).widget().setParent(None)
            
        current_type = self.type_combo.currentText()
        
        for i, widget in enumerate(self.region_widgets):
            if current_type == "four_cut":
                row = i // 2
                col = i % 2
                self.regions_layout.addWidget(widget, row, col)
            else:
                self.regions_layout.addWidget(widget, i, 0)

    def on_type_changed(self, text):
        self.save_current_frame_info()
        if not self.region_widgets:
            count = 4 if text == "four_cut" else 1
            for _ in range(count):
                self.add_region_input([0, 0, 0, 0])
        self.rearrange_regions()

    def browse_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "프레임 이미지 선택", "", "Images (*.png *.jpg *.jpeg)")
        if filename:
            self.filename_edit.setText(os.path.basename(filename))

    def auto_detect_regions(self):
        filename = self.filename_edit.text()
        if not filename:
            MessageBox.warning(self, "경고", "파일명을 먼저 입력하거나 선택해주세요.")
            return

        filepath = os.path.join(os.getcwd(), 'frame', filename)
        if not os.path.exists(filepath):
            if os.path.exists(filename):
                filepath = filename
            else:
                MessageBox.warning(self, "오류", f"파일을 찾을 수 없습니다: {filepath}")
                return

        try:
            img = Image.open(filepath).convert("RGBA")
            width, height = img.size
            
            visited = set()
            regions = []
            pixels = img.load()
            step = 5 
            
            for y in range(0, height, step):
                for x in range(0, width, step):
                    if (x, y) in visited:
                        continue
                        
                    r, g, b, a = pixels[x, y]
                    if a < 10:
                        min_x, min_y, max_x, max_y = x, y, x, y
                        stack = [(x, y)]
                        visited.add((x, y))
                        
                        while stack:
                            cx, cy = stack.pop()
                            min_x = min(min_x, cx)
                            min_y = min(min_y, cy)
                            max_x = max(max_x, cx)
                            max_y = max(max_y, cy)
                            
                            for dx, dy in [(-step, 0), (step, 0), (0, -step), (0, step)]:
                                nx, ny = cx + dx, cy + dy
                                if 0 <= nx < width and 0 <= ny < height:
                                    if (nx, ny) not in visited:
                                        nr, ng, nb, na = pixels[nx, ny]
                                        if na < 10:
                                            visited.add((nx, ny))
                                            stack.append((nx, ny))
                        
                        if (max_x - min_x) > 50 and (max_y - min_y) > 50:
                            regions.append([min_x, min_y, max_x + step, max_y + step])

            regions.sort(key=lambda r: (r[1], r[0]))
            
            final_regions = []
            if regions:
                rows = []
                current_row = [regions[0]]
                for i in range(1, len(regions)):
                    prev = current_row[-1]
                    curr = regions[i]
                    prev_cy = (prev[1] + prev[3]) // 2
                    curr_cy = (curr[1] + curr[3]) // 2
                    prev_h = prev[3] - prev[1]
                    if abs(curr_cy - prev_cy) < (prev_h / 2):
                        current_row.append(curr)
                    else:
                        rows.append(current_row)
                        current_row = [curr]
                rows.append(current_row)
                for row in rows:
                    row.sort(key=lambda r: r[0])
                    final_regions.extend(row)
            
            self.clear_regions()
            for region in final_regions:
                self.add_region_input(region)
            
            self.rearrange_regions()
            self.update_preview()
            
            self.rearrange_regions()
            self.update_preview()
            
            MessageBox.information(self, "완료", f"{len(final_regions)}개의 투명 영역을 감지했습니다.")

        except Exception as e:
            MessageBox.critical(self, "오류", f"이미지 분석 중 오류 발생: {e}")

    def add_new_frame(self):
        new_frame = {
            "name": "새 프레임",
            "filename": "new_frame.png",
            "type": "four_cut",
            "regions": [[0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0]]
        }
        self.frame_manager.add_frame(new_frame)
        self.refresh_frame_list()
        self.frame_list.setCurrentRow(self.frame_list.count() - 1)

    def delete_current_frame(self):
        row = self.frame_list.currentRow()
        if row < 0:
            MessageBox.warning(self, "경고", "삭제할 프레임을 선택해주세요.")
            return
            
        reply = MessageBox.question(self, "삭제 확인", "정말로 이 프레임을 삭제하시겠습니까?")
        if reply == MessageBox.Yes:
            self.frame_manager.delete_frame(row)
            self.refresh_frame_list()
            self.name_edit.clear()
            self.filename_edit.clear()
            self.clear_regions()
            self.preview_widget.set_image(None)

    def save_current_frame_info(self):
        """현재 편집 중인 프레임 정보를 즉시 저장"""
        row = self.frame_list.currentRow()
        if row < 0:
            return
            
        regions = [w.get_values() for w in self.region_widgets]
        
        frame_data = {
            "name": self.name_edit.text(),
            "filename": self.filename_edit.text(),
            "type": self.type_combo.currentText(),
            "regions": regions
        }
        
        self.frame_manager.update_frame(row, frame_data)
        # 리스트 아이템 텍스트 업데이트
        self.frame_list.item(row).setText(self.name_edit.text())

    def save_changes(self):
        """변경사항을 파일에 저장"""
        self.frame_manager.save_frames()
        MessageBox.information(self, "저장 완료", "모든 변경사항이 저장되었습니다.")

    def cancel_changes(self):
        """변경사항 취소 및 다시 불러오기"""
        reply = MessageBox.question(self, "취소 확인", "저장하지 않은 변경사항이 사라집니다. 계속하시겠습니까?")
        if reply == MessageBox.Yes:
            self.frame_manager.load_frames()
            self.refresh_frame_list()
            self.load_selected_frame(0) # 첫 번째 프레임 선택
            MessageBox.information(self, "취소 완료", "변경사항이 취소되었습니다.")

    def highlight_input_widget(self, index):
        """특정 인덱스의 입력 위젯 하이라이트"""
        if 0 <= index < len(self.region_widgets):
            widget = self.region_widgets[index]
            
            # 스타일 적용 (파란색 테두리)
            for w in self.region_widgets:
                w.setStyleSheet(Styles.GROUP_BOX)
            
            widget.setStyleSheet(f"""
                QGroupBox {{
                    font-weight: bold;
                    border: 2px solid {Colors.PRIMARY};
                    border-radius: 5px;
                    margin-top: 10px;
                    background-color: #E3F2FD;
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px 0 3px;
                    color: {Colors.PRIMARY};
                }}
            """)
            
            # 스크롤 이동
            self.regions_container.ensureWidgetVisible(widget)
