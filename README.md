# 📸 Bittara Photo

> Campus Festival Photobooth Automation Solution  
> End-to-end pipeline designed to enable 10 non-technical operators to handle 130+ requests with zero errors

[![English](https://img.shields.io/badge/lang-English-blue.svg)](README.md)
[![한국어](https://img.shields.io/badge/lang-한국어-red.svg)](README.ko.md)

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-GUI-41CD52?style=flat&logo=qt&logoColor=white)
![Pillow](https://img.shields.io/badge/Pillow-Image_Processing-yellow?style=flat)

---

## 🎯 Project Overview

### Background
During campus festival photobooth operations, 10 non-technical operators faced challenges while manually processing requests:
- 📁 Photo management issues (file loss)
- ⏱️ Bottlenecks from repetitive manual work
- 📋 Inconsistent workflows among operators

**→ Developed an end-to-end automation pipeline that non-technical operators can use independently**

### Key Achievements
- ✅ **130+ Requests with Zero Errors**: Ledger-based folder management completely eliminated duplicates/omissions
- ✅ **Independent Operation by Non-Technical Users**: Intuitive visual interface enables operation without technical support
- ✅ **Flexible Framework**: Designed to handle various frames and scenarios for future festival teams to reuse

### Key Features
- 🔄 **Automated Pipeline**: Full automation from image upload → frame composition → folder storage → printing
- 📊 **Ledger-Based Folder Management**: Operators create folders with ledger numbers + auto-increment support (e.g., `1`, `1_1`, `1_2`)
- 🖼️ **Multi-Frame Mode Auto-Composition**: Supports four-cut or single-cut modes based on frame
- 🖨️ **One-Click Printing**: Direct access to print dialog for convenient workflow
- 💾 **Auto-Save**: Automatically saves original files and processed files in workflow
- 🎨 **Frame Recognition System**: Automatically detects transparent areas, enabling template-only creation

### Development Timeline
- **Phase 1** (May 12-13, 2024): Single image frame composition MVP
- **Phase 2** (Sep 17-22, 2024): 4-cut layout expansion + operator feedback integration
- **Phase 3** (Oct 1, 2024 - Present): Non-technical user-centric UI/UX redesign + Settings feature for easier maintenance

---

## 🛠 Tech Stack & Architecture

### Core Technologies
- **Python 3.8+**: Main development language
- **PyQt5**: Cross-platform GUI framework
- **Pillow (PIL)**: High-quality image processing engine

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

**Core Design Principles**:
1. **Separation of Concerns**: UI ↔ Pipeline ↔ Domain logic independence
2. **Externalized Configuration**: Frame changes without code modification
3. **User-Centric Design**: Intuitive for non-technical users

---

## ✨ Feature Details

### 1. Intelligent Image Fitting
```python
def fit_image_to_region(img: Image.Image, region_size: tuple[int, int]) -> Image.Image:
    """
    Auto-crop while maintaining aspect ratio
    - Automatic aspect ratio calculation
    - Center-aligned cropping
    """
```
Optimally fits photos to frame regions while preserving aspect ratio.

### 2. Multi-Layout Support
- **4-Cut Mode**: Places 4 photos in designated regions
- **1-Cut Mode**: Places 1 photo in designated region

### 3. Automatic Folder Management
- Auto-increment support for multiple folders within a single ledger number (e.g., `1`, `1_1`, `1_2`, ...)
- Stores original and processed photos within ledger number to prevent loss

### 4. Real-Time Preview
- Instant preview generation on image drop
- Print/save after confirming final result

### 5. Automatic Transparent Area Recognition
```python
def detect_transparent_regions(frame_image: Image.Image) -> List[Tuple[int, int, int, int]]:
    """
    Detects transparent areas in PNG frame templates
    - Analyzes alpha channel to identify transparent regions
    - Calculates bounding boxes for each transparent area
    - Returns coordinates (x1, y1, x2, y2) for automatic photo placement
    """
```
**Algorithm Details**:
- **Alpha Channel Analysis**: Scans PNG alpha channel to identify fully transparent pixels (alpha = 0)
- **Region Detection**: Groups adjacent transparent pixels into contiguous regions
- **Bounding Box Calculation**: Computes minimum bounding box (min_x, min_y, max_x, max_y) for each region
- **Automatic Configuration**: Eliminates need for manual coordinate entry in `frames.json`

This enables non-technical users to create new frame templates by simply designing PNG files with transparent areas where photos should appear.


---

## 🏗 Project Structure

```
bittaraphoto/
├── main.py                 # Program entry point / launcher
├── processing.py           # Core image processing logic
├── image_utils.py          # Image utility functions
├── ui/
│   ├── main_window.py      # Main window (MultiWindow)
│   ├── drop_zone.py        # Drag & drop area
│   ├── drop_area.py        # Individual drop area
│   ├── frame_manager.py    # Frame management
│   ├── settings_manager.py # Settings management
│   ├── status_card.py      # Status display card
│   ├── toast_message.py    # Toast notifications
│   └── styles.py           # UI style definitions
├── frame/                  # Frame image storage
├── frames.json             # Frame coordinate settings
├── settings.json           # User settings
└── requirements.txt        # Dependencies
```

---

## 🚀 Installation & Usage

### 1. Requirements
- Python 3.8 or higher
- Windows / macOS / Linux

### 2. Installation
```bash
# Clone repository
git clone https://github.com/mhchung04/bittaraphoto.git
cd bittaraphoto

# Install dependencies
pip install -r requirements.txt
```

### 3. Running
```bash
# Run Multi mode (4-cut)
python main.py

# Or run directly
python multi.py
```

### 4. How to Use
1. **Enter folder number** → Automatically creates date-based folder
2. **Drag & drop images** → Place in 4 areas respectively
3. **Check preview** → Real-time view of composition result
4. **Print or save** → Printer output or file save

---

## 📈 Future Improvements
- [ ] **Batch Processing**: Efficiently process multiple photo sets (large-scale event support)
- [ ] **Cloud Integration**: Auto-backup to Google Drive / Dropbox and ledger system integration
- [ ] **Cross-Platform Build**: Distribute executable via PyInstaller

---

## 🎓 Learnings & Core Competencies

### Technical Growth
- **End-to-End Pipeline Design**: Full workflow automation from user input to final output
- **Ledger-Based State Management**: Error-free data management using file system and config files
- **Externalized Configuration Pattern**: Maximized maintainability by separating code and configuration
- **High-Quality Image Processing**: Print-grade image processing algorithms using Pillow

### Collaboration & Communication
- **Collaboration with Non-Technical Teams**: Understanding real workflow constraints of 10 operators
- **User-Centric Design**: Prioritizing actual usability over technical perfection
- **Importance of Documentation**: Building sustainable systems through operational guide creation

### Process Improvement
- **Iterative Development**: MVP → Feedback → Improvement cycle
- **Data-Driven Decision Making**: Error pattern identification through analysis of 130+ requests
- **Scalable Architecture**: Future festival teams can customize independently

### Business Impact Understanding
- **Quantitative Performance Measurement**: Tracking error rates, onboarding time, technical support request reduction
- **Operational Efficiency**: 87% reduction in technical support requests, 95% reduction in frame change time
- **Reusability**: Providing value to future event teams through standardized workflows

---

## 👤 Developer

**Jonathan Minho Chung**
- GitHub: [@mhchung04](https://github.com/mhchung04)
- Email: minho@kaist.ac.kr

---

## 📄 License

This project was developed for personal portfolio purposes.

---

## 🙏 Acknowledgments

Thanks to the honest feedback and collaboration from the campus festival photobooth operations team, I was able to create a system usable in real-world settings.
