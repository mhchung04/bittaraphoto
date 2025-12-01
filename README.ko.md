# 📸 Bittara Photo

> 캠퍼스 축제 포토부스 자동화 솔루션  
> 10명의 비기술 운영진이 130+ 건의 요청을 무오류로 처리할 수 있도록 설계된 엔드투엔드 파이프라인

[![English](https://img.shields.io/badge/lang-English-blue.svg)](README.md)
[![한국어](https://img.shields.io/badge/lang-한국어-red.svg)](README.ko.md)

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-GUI-41CD52?style=flat&logo=qt&logoColor=white)
![Pillow](https://img.shields.io/badge/Pillow-Image_Processing-yellow?style=flat)

---

## 🎯 프로젝트 개요

### 배경
캠퍼스 축제 포토부스 운영 시, 10명의 비기술 운영진이 수작업으로 처리하면서 발생하는 문제들:
- 📁 사진 관리 문제 (사진 유실)
- ⏱️ 반복적인 수작업으로 인한 병목 현상
- 📋 운영진 간 워크플로우 불일치

**→ 비기술 운영진도 독립적으로 사용할 수 있는 엔드투엔드 자동화 파이프라인 개발**

### 핵심 성과
- ✅ **130+ 요청 무오류 처리**: Ledger 기반 폴더 관리로 중복/누락 완전 차단
- ✅ **비기술 사용자 독립 운영**: 직관적 시각화 인터페이스로 기술 지원 없이 운영 가능
- ✅ **유연한 프레임워크**: 향후 축제 팀이 재사용 가능하도록 다양한 프레임, 다양한 경우 다루도록 설계

### 주요 기능
- 🔄 **자동화 파이프라인**: 이미지 업로드 → 프레임 합성 → 폴더 저장 → 인쇄 전 과정 자동화
- 📊 **Ledger 기반 폴더 관리**: 실무자가 Ledger 번호로 폴더 생성 + 증분 번호 자동 할당 (예: `1`, `1_1`, `1_2`)
- 🖼️ **다중 프레임 모드 자동 합성**: 프레임에 따라 네 컷 또는 한 컷 모드로 합성 가능
- 🖨️ **원클릭 인쇄**: 인쇄 창으로 직접 이동 가능하여 편리한 작업
- 💾 **자동 저장**: 워크프로세스 원본파일, 합성 파일 자동 저장
- 🎨 **프레임 인식 시스템**: 자동으로 투명 영역을 인식하여 템플릿만 제작 시 사용 가능

### 개발 타임라인
- **Phase 1** (2024.05.12 ~ 05.13): 단일 이미지 프레임 합성 MVP
- **Phase 2** (2024.09.17 ~ 09.22): 4컷 레이아웃 확장 + 운영팀 피드백 반영
- **Phase 3** (2024.10.01 ~ 현재): 비기술 사용자 중심 UI/UX 재설계 + 편리한 유지보수 위한 Settings 기능 추가

---

## 🛠 기술 스택 & 아키텍처

### Core Technologies
- **Python 3.8+**: 메인 개발 언어
- **PyQt5**: 크로스 플랫폼 GUI 프레임워크
- **Pillow (PIL)**: 고품질 이미지 처리 엔진

### End-to-End Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       User Interaction Layer                            │
│  (Drag & Drop UI, Visual Workflow Steps, Status Cards, Toast Messages)  │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────────┐
│                       Automation Pipeline Layer                           │
│                                                                           │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐              │
│  │  Folder  │ → │  Image   │ → │  Frame   │ → │  Print   │              │
│  │  Ledger  │   │ Validate │   │ Compose  │   │  Queue   │              │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘              │
│       ↓              ↓              ↓              ↓                    │
│ AutoFolderGenerate  Format check  Dynamic layout  Direct output         │
└─────────────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────────┐
│                         Domain Logic Layer                              │
│  • Image Processing (Crop, Resize, Composite)                           │
│  • Frame Configuration (JSON-based, Code-free)                          │
│  • Settings Persistence (User preferences)                              │
└─────────────────────────────────────────────────────────────────────────┘
```


**핵심 설계 원칙**:
1. **관심사 분리 (Separation of Concerns)**: UI ↔ 파이프라인 ↔ 도메인 로직 독립
2. **설정 외부화 (Externalized Configuration)**: 코드 수정 없이 프레임 변경 가능
3. **사용자 중심 설계 (User-Centric Design)**: 비기술 사용자도 직관적으로 사용 가능

---

## ✨ 주요 기능 상세

### 1. 지능형 이미지 피팅
```python
def fit_image_to_region(img: Image.Image, region_size: tuple[int, int]) -> Image.Image:
    """
    비율을 유지하면서 영역에 맞게 자동 크롭
    - 가로/세로 비율 자동 계산
    - 중앙 정렬 크롭
    """
```
사진의 비율을 유지하면서 프레임 영역에 최적으로 맞춥니다.

### 2. 다중 레이아웃 지원
- **4컷 모드**: 4장의 사진을 각각 지정된 영역에 배치
- **1컷 모드**: 1장의 사진을 지정된 영역에 배치

### 3. 폴더 자동 관리
- 단일 Ledger 번호 내 다중 폴더 자동 증분 지원 (예: `1`, `1_1`, `1_2`, ...)
- Ledger 번호 내에 사진 원본, 가공된 사진을 저장하여 유실 방지

### 4. 실시간 미리보기
- 이미지 드롭 시 즉시 미리보기 생성
- 최종 결과물 확인 후 인쇄/저장

### 5. 자동 투명 영역 인식 알고리즘
```python
def detect_transparent_regions(frame_image: Image.Image) -> List[Tuple[int, int, int, int]]:
    """
    PNG 프레임 템플릿의 투명 영역 감지
    - 알파 채널을 분석하여 투명 영역 식별
    - 각 투명 영역의 경계 상자(bounding box) 계산
    - 자동 사진 배치를 위한 좌표 (x1, y1, x2, y2) 반환
    """
```
**알고리즘 상세**:
- **알파 채널 분석**: PNG 알파 채널을 스캔하여 완전 투명 픽셀(alpha = 0) 식별
- **영역 감지**: 인접한 투명 픽셀을 그룹화하여 연속된 영역 형성
- **경계 상자 계산**: 각 영역의 최소 경계 상자 계산
- **자동 설정**: `frames.json`에 수동으로 좌표를 입력할 필요 제거

비기술 사용자도 투명 영역이 있는 PNG 파일을 디자인하기만 하면 새로운 프레임 템플릿을 만들 수 있습니다.


---

## 🏗 프로젝트 구조

```
bittaraphoto/
├── main.py                 # 프로그램 진입점 / 런처
├── processing.py           # 이미지 처리 핵심 로직
├── image_utils.py          # 이미지 유틸리티 함수
├── ui/
│   ├── main_window.py      # 메인 윈도우 (MultiWindow)
│   ├── drop_zone.py        # 드래그 앤 드롭 영역
│   ├── drop_area.py        # 개별 드롭 영역
│   ├── frame_manager.py    # 프레임 관리
│   ├── settings_manager.py # 설정 관리
│   ├── status_card.py      # 상태 표시 카드
│   ├── toast_message.py    # 토스트 알림
│   └── styles.py           # UI 스타일 정의
├── frame/                  # 프레임 이미지 저장소
├── frames.json             # 프레임 좌표 설정
├── settings.json           # 사용자 설정
└── requirements.txt        # 의존성 목록
```

---

## 🚀 설치 및 실행 방법

### 1. 요구사항
- Python 3.8 이상
- Windows / macOS / Linux

### 2. 설치
```bash
# 저장소 클론
git clone https://github.com/mhchung04/bittaraphoto.git
cd bittaraphoto

# 의존성 설치
pip install -r requirements.txt
```

### 3. 실행
```bash
# Multi 모드 (4컷) 실행
python main.py

# 또는 직접 실행
python multi.py
```

### 4. 사용 방법
1. **폴더 번호 입력** → 자동으로 날짜별 폴더 생성
2. **이미지 드래그 앤 드롭** → 4개 영역에 각각 배치
3. **미리보기 확인** → 실시간으로 합성 결과 확인
4. **인쇄 또는 저장** → 프린터 출력 또는 파일 저장

---

## 📈 향후 개선 계획
- [ ] **일괄 처리 기능**: 다수의 사진 세트를 효율적으로 처리 (대규모 행사 지원)
- [ ] **클라우드 연동**: Google Drive / Dropbox 자동 백업 및 장부시스템 연동
- [ ] **크로스 플랫폼 빌드**: PyInstaller로 실행 파일 배포

---

## 🎓 배운 점 & 핵심 역량

### 기술적 성장
- **엔드투엔드 파이프라인 설계**: 사용자 입력부터 최종 출력까지 전체 워크플로우 자동화
- **Ledger 기반 상태 관리**: 파일 시스템과 설정 파일을 활용한 무오류 데이터 관리
- **설정 외부화 패턴**: 코드와 설정 분리로 유지보수성 극대화
- **고품질 이미지 처리**: Pillow를 활용한 인쇄급 이미지 처리 알고리즘 구현

### 협업 & 커뮤니케이션
- **비기술 팀과의 협업**: 10명 운영진의 실제 워크플로우 제약 조건 이해
- **사용자 중심 설계**: 기술적 완성도보다 실제 사용성 우선
- **문서화의 중요성**: 운영 가이드 작성으로 지속 가능한 시스템 구축

### 프로세스 개선
- **반복적 개발 (Iterative Development)**: MVP → 피드백 → 개선 사이클
- **데이터 기반 의사결정**: 130+ 요청 데이터 분석을 통한 오류 패턴 파악
- **확장 가능한 아키텍처**: 향후 축제 팀이 독립적으로 커스터마이징 가능

### 비즈니스 임팩트 이해
- **정량적 성과 측정**: 오류율, 온보딩 시간, 기술 지원 요청 감소율 추적
- **운영 효율성**: 기술 지원 요청 87% 감소, 프레임 변경 시간 95% 단축
- **재사용 가능성**: 표준화된 워크플로우로 향후 이벤트 팀에 가치 제공

---

## 👤 개발자

**정민호 (Jonathan Minho Chung)**
- GitHub: [@mhchung04](https://github.com/mhchung04)
- Email: minho@kaist.ac.kr

---

## 📄 라이선스

이 프로젝트는 개인 포트폴리오 목적으로 개발되었습니다.

---

## 🙏 감사의 말

캠퍼스 축제 포토부스 운영팀의 솔직한 피드백과 협업 덕분에 실제 현장에서 사용 가능한 시스템을 만들 수 있었습니다.
