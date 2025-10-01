$header = @"
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


"@

$lines = Get-Content "multi.py" -Encoding UTF8
$imageutils = $lines[15..95] -join "`r`n"
$multiwindow = $lines[534..($lines.Count-1)] -join "`r`n"
$final = $header + $imageutils + "`r`n`r`n" + $multiwindow
$final | Out-File -FilePath "ui\main_window.py" -Encoding UTF8
Write-Host "main_window.py created successfully!"
