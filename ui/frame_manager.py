import json
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QLabel, QLineEdit, QPushButton, QMessageBox, 
                             QComboBox, QWidget, QScrollArea, QFormLayout,
                             QSpinBox, QGroupBox, QGridLayout, QFileDialog)
from PyQt5.QtCore import Qt
from PIL import Image

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
        self.save_frames()

    def update_frame(self, index, frame_data):
        if 0 <= index < len(self.frames):
            self.frames[index] = frame_data
            self.save_frames()

    def delete_frame(self, index):
        if 0 <= index < len(self.frames):
            del self.frames[index]
            self.save_frames()


class RegionInputWidget(QGroupBox):
    """개별 영역 좌표 입력 위젯 (박스 형태)"""
    def __init__(self, index, region=None):
        super().__init__(f"영역 {index + 1}")
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)
        
        layout = QGridLayout()
        
        self.x1 = QSpinBox(); self.x1.setRange(0, 10000); self.x1.setPrefix("X1: ")
        self.y1 = QSpinBox(); self.y1.setRange(0, 10000); self.y1.setPrefix("Y1: ")
        self.x2 = QSpinBox(); self.x2.setRange(0, 10000); self.x2.setPrefix("X2: ")
        self.y2 = QSpinBox(); self.y2.setRange(0, 10000); self.y2.setPrefix("Y2: ")

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

    def get_values(self):
        return [self.x1.value(), self.y1.value(), self.x2.value(), self.y2.value()]

    def set_values(self, region):
        self.x1.setValue(region[0])
        self.y1.setValue(region[1])
        self.x2.setValue(region[2])
        self.y2.setValue(region[3])


class FrameEditorDialog(QDialog):
    """프레임 관리 UI 다이얼로그"""
    def __init__(self, frame_manager, parent=None):
        super().__init__(parent)
        self.frame_manager = frame_manager
        self.setWindowTitle("프레임 관리자")
        self.resize(1000, 700)
        
        self.layout = QHBoxLayout()
        
        # 좌측: 프레임 목록
        left_layout = QVBoxLayout()
        self.frame_list = QListWidget()
        self.frame_list.currentRowChanged.connect(self.load_selected_frame)
        left_layout.addWidget(QLabel("프레임 목록"))
        left_layout.addWidget(self.frame_list)
        
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("추가")
        self.add_btn.clicked.connect(self.add_new_frame)
        self.del_btn = QPushButton("삭제")
        self.del_btn.clicked.connect(self.delete_current_frame)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.del_btn)
        left_layout.addLayout(btn_layout)
        
        # 우측: 상세 편집
        right_layout = QVBoxLayout()
        self.form_group = QGroupBox("프레임 상세 정보")
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        
        # 파일명 + 찾기 버튼
        file_layout = QHBoxLayout()
        self.filename_edit = QLineEdit()
        self.browse_btn = QPushButton("찾기...")
        self.browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.filename_edit)
        file_layout.addWidget(self.browse_btn)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["four_cut", "single_cut"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        
        form_layout.addRow("이름:", self.name_edit)
        form_layout.addRow("파일명:", file_layout)
        form_layout.addRow("타입:", self.type_combo)
        
        self.form_group.setLayout(form_layout)
        right_layout.addWidget(self.form_group)
        
        # 자동 인식 버튼
        self.auto_detect_btn = QPushButton("투명 영역 자동 인식 (PNG)")
        self.auto_detect_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 8px;")
        self.auto_detect_btn.clicked.connect(self.auto_detect_regions)
        right_layout.addWidget(self.auto_detect_btn)
        
        # 영역 편집 (그리드 레이아웃)
        self.regions_group = QGroupBox("영역 좌표 설정")
        self.regions_layout = QGridLayout() # 메인 레이아웃은 그리드로 변경
        self.regions_container = QWidget()
        self.regions_container.setLayout(self.regions_layout)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.regions_container)
        
        regions_main_layout = QVBoxLayout()
        regions_main_layout.addWidget(scroll)
        
        # 영역 추가/삭제 버튼 (수동 조작용)
        region_btn_layout = QHBoxLayout()
        self.add_region_btn = QPushButton("영역 추가")
        self.add_region_btn.clicked.connect(lambda: self.add_region_input(None))
        self.remove_region_btn = QPushButton("마지막 영역 삭제")
        self.remove_region_btn.clicked.connect(self.remove_last_region)
        region_btn_layout.addWidget(self.add_region_btn)
        region_btn_layout.addWidget(self.remove_region_btn)
        regions_main_layout.addLayout(region_btn_layout)
        
        self.regions_group.setLayout(regions_main_layout)
        right_layout.addWidget(self.regions_group)
        
        # 저장 버튼
        self.save_btn = QPushButton("변경사항 저장")
        self.save_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        self.save_btn.clicked.connect(self.save_current_frame)
        right_layout.addWidget(self.save_btn)
        
        self.layout.addLayout(left_layout, 1)
        self.layout.addLayout(right_layout, 3) # 우측 비율 증가
        self.setLayout(self.layout)
        
        self.region_widgets = []
        self.refresh_list()

    def refresh_list(self):
        self.frame_list.clear()
        frames = self.frame_manager.get_all_frames()
        for frame in frames:
            self.frame_list.addItem(frame['name'])

    def load_selected_frame(self, row):
        if row < 0:
            return
            
        frames = self.frame_manager.get_all_frames()
        frame = frames[row]
        
        self.name_edit.setText(frame['name'])
        self.filename_edit.setText(frame['filename'])
        
        index = self.type_combo.findText(frame.get('type', 'four_cut'))
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
            
        # 영역 로드
        self.clear_regions()
        regions = frame.get('regions', [])
        for i, region in enumerate(regions):
            self.add_region_input(region)
            
        self.rearrange_regions()

    def clear_regions(self):
        for widget in self.region_widgets:
            self.regions_layout.removeWidget(widget)
            widget.deleteLater()
        self.region_widgets = []

    def add_region_input(self, region=None):
        index = len(self.region_widgets)
        widget = RegionInputWidget(index, region)
        self.region_widgets.append(widget)
        self.rearrange_regions()

    def remove_last_region(self):
        if self.region_widgets:
            widget = self.region_widgets.pop()
            self.regions_layout.removeWidget(widget)
            widget.deleteLater()
            self.rearrange_regions()

    def rearrange_regions(self):
        """위젯들을 그리드에 재배치"""
        # 기존 배치 제거 (위젯은 유지)
        for i in reversed(range(self.regions_layout.count())): 
            self.regions_layout.itemAt(i).widget().setParent(None)
            
        # 타입에 따라 배치
        current_type = self.type_combo.currentText()
        
        for i, widget in enumerate(self.region_widgets):
            if current_type == "four_cut":
                # 2x2 그리드
                row = i // 2
                col = i % 2
                self.regions_layout.addWidget(widget, row, col)
            else:
                # 1열로 나열 (Single cut 등)
                self.regions_layout.addWidget(widget, i, 0)

    def on_type_changed(self, text):
        if not self.region_widgets:
            count = 4 if text == "four_cut" else 1
            for _ in range(count):
                self.add_region_input([0, 0, 0, 0])
        self.rearrange_regions()

    def browse_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "프레임 이미지 선택", "", "Images (*.png *.jpg *.jpeg)")
        if filename:
            # 절대 경로 대신 파일명만 저장 (frame 폴더 기준)
            self.filename_edit.setText(os.path.basename(filename))

    def auto_detect_regions(self):
        """PNG 이미지의 투명 영역을 자동으로 감지"""
        filename = self.filename_edit.text()
        if not filename:
            QMessageBox.warning(self, "경고", "파일명을 먼저 입력하거나 선택해주세요.")
            return

        # frame 폴더 경로 가정
        filepath = os.path.join(os.getcwd(), 'frame', filename)
        if not os.path.exists(filepath):
            # 절대 경로일 수도 있으니 확인
            if os.path.exists(filename):
                filepath = filename
            else:
                QMessageBox.warning(self, "오류", f"파일을 찾을 수 없습니다: {filepath}")
                return

        try:
            img = Image.open(filepath).convert("RGBA")
            width, height = img.size
            
            # 투명한 픽셀 찾기 (Alpha < 10)
            # 간단한 알고리즘:
            # 1. 전체 픽셀 스캔하여 투명 픽셀 마킹
            # 2. 연결된 성분(Connected Components) 찾기 -> 영역 추출
            # 3. 영역의 Bounding Box 계산
            
            # 성능을 위해 썸네일로 축소해서 대략적 위치 찾고 원본에서 정밀 보정? 
            # 아니면 그냥 원본 스캔 (요즘 PC 성능이면 충분)
            
            visited = set()
            regions = []
            
            pixels = img.load()
            
            # 스캔 간격 (속도 최적화)
            step = 5 
            
            for y in range(0, height, step):
                for x in range(0, width, step):
                    if (x, y) in visited:
                        continue
                        
                    r, g, b, a = pixels[x, y]
                    if a < 10: # 투명
                        # Flood fill로 영역 확장
                        min_x, min_y, max_x, max_y = x, y, x, y
                        stack = [(x, y)]
                        visited.add((x, y))
                        
                        region_pixels = []
                        
                        while stack:
                            cx, cy = stack.pop()
                            region_pixels.append((cx, cy))
                            
                            min_x = min(min_x, cx)
                            min_y = min(min_y, cy)
                            max_x = max(max_x, cx)
                            max_y = max(max_y, cy)
                            
                            # 4방향 탐색 (step 단위로)
                            for dx, dy in [(-step, 0), (step, 0), (0, -step), (0, step)]:
                                nx, ny = cx + dx, cy + dy
                                if 0 <= nx < width and 0 <= ny < height:
                                    if (nx, ny) not in visited:
                                        nr, ng, nb, na = pixels[nx, ny]
                                        if na < 10:
                                            visited.add((nx, ny))
                                            stack.append((nx, ny))
                        
                        # 영역이 너무 작으면 무시 (노이즈)
                        if (max_x - min_x) > 50 and (max_y - min_y) > 50:
                            # 정밀 경계 보정 (step 때문에 오차 발생 가능)
                            # 여기서는 단순화를 위해 step 만큼 여유를 두고 저장하거나
                            # 실제로는 step=1로 하는게 가장 정확함. 
                            # 4K 이미지도 1초 내외면 될듯.
                            regions.append([min_x, min_y, max_x + step, max_y + step])

            # 영역 정렬 (좌상단 -> 우하단)
            # Y좌표 우선, 그 다음 X좌표
            # 하지만 2x2 격자라면:
            # 1 2
            # 3 4
            # 순서로 정렬해야 함.
            # 중심점 기준으로 정렬
            
            regions.sort(key=lambda r: (r[1], r[0])) # Y 우선 정렬 (행 단위)
            
            # 행 내에서 X 정렬이 필요함.
            # Y 차이가 크지 않으면 같은 행으로 취급
            
            final_regions = []
            if regions:
                # Y 좌표 기준으로 그룹화
                rows = []
                current_row = [regions[0]]
                
                for i in range(1, len(regions)):
                    prev = current_row[-1]
                    curr = regions[i]
                    
                    # Y 중심점 차이가 높이의 절반보다 작으면 같은 행
                    prev_cy = (prev[1] + prev[3]) // 2
                    curr_cy = (curr[1] + curr[3]) // 2
                    prev_h = prev[3] - prev[1]
                    
                    if abs(curr_cy - prev_cy) < (prev_h / 2):
                        current_row.append(curr)
                    else:
                        rows.append(current_row)
                        current_row = [curr]
                rows.append(current_row)
                
                # 각 행 내부에서 X 정렬
                for row in rows:
                    row.sort(key=lambda r: r[0])
                    final_regions.extend(row)
            
            # UI 업데이트
            self.clear_regions()
            for region in final_regions:
                self.add_region_input(region)
            
            self.rearrange_regions()
            
            QMessageBox.information(self, "완료", f"{len(final_regions)}개의 투명 영역을 감지했습니다.")

        except Exception as e:
            QMessageBox.critical(self, "오류", f"이미지 분석 중 오류 발생: {e}")

    def add_new_frame(self):
        new_frame = {
            "name": "새 프레임",
            "filename": "new_frame.png",
            "type": "four_cut",
            "regions": [[0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0]]
        }
        self.frame_manager.add_frame(new_frame)
        self.refresh_list()
        self.frame_list.setCurrentRow(self.frame_list.count() - 1)

    def delete_current_frame(self):
        row = self.frame_list.currentRow()
        if row < 0:
            QMessageBox.warning(self, "경고", "삭제할 프레임을 선택해주세요.")
            return
            
        reply = QMessageBox.question(self, "삭제 확인", "정말로 이 프레임을 삭제하시겠습니까?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.frame_manager.delete_frame(row)
            self.refresh_list()
            # 선택 초기화
            self.name_edit.clear()
            self.filename_edit.clear()
            self.clear_regions()

    def save_current_frame(self):
        row = self.frame_list.currentRow()
        if row < 0:
            QMessageBox.warning(self, "경고", "저장할 프레임을 선택해주세요.")
            return
            
        regions = [w.get_values() for w in self.region_widgets]
        
        frame_data = {
            "name": self.name_edit.text(),
            "filename": self.filename_edit.text(),
            "type": self.type_combo.currentText(),
            "regions": regions
        }
        
        self.frame_manager.update_frame(row, frame_data)
        self.refresh_list()
        self.frame_list.setCurrentRow(row) # 선택 유지
        QMessageBox.information(self, "저장 완료", "프레임 정보가 저장되었습니다.")
