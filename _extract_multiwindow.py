# 임시 스크립트: MultiWindow 클래스 추출
with open('multi.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 필요한 imports
imports =  """\"\"\"
MainWindow 모듈
Multi 모드 메인 윈도우를 제공합니다.
\"\"\"

import sys
import os
import shutil
import datetime
import io
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                           QWidget, QFileDialog, QLineEdit, QLabel, QHBoxLayout,
                           QFrame, QSizePolicy, QSpacerItem, QMessageBox, QComboBox,
                           QDialog)
from PyQt5.QtGui import QFont, QPixmap, QImage, QPainter
from PyQt5.QtCore import Qt
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PIL import Image as PILImage
from .drop_area import SingleDropArea, MultiDropArea


"""

# Image Utils 클래스 (16-96)
imageutils_lines = ''.join(lines[15:96])

# MultiWindow 클래스 (553-1706)
multiwindow_lines = ''.join(lines[552:1706])

# 결합
output = imports + imageutils_lines + '\n\n' + multiwindow_lines

with open('ui/main_window.py', 'w', encoding='utf-8') as f:
    f.write(output)

print("main_window.py 생성 완료!")
