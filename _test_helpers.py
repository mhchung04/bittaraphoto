
import unittest
import os
import shutil
import sys
from PyQt5.QtWidgets import QApplication

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import FolderManager, ImageProcessor, PrintManager

class TestFolderManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = "_test_folders"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
        self.manager = FolderManager(base_path=self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_get_actual_folder_name(self):
        # 기본 이름
        name = self.manager.get_actual_folder_name("100")
        self.assertEqual(name, "100")

        # 이미 존재하는 경우
        os.makedirs(os.path.join(self.test_dir, "100"))
        name = self.manager.get_actual_folder_name("100")
        self.assertEqual(name, "100_1")

        # 100_1도 존재하는 경우
        os.makedirs(os.path.join(self.test_dir, "100_1"))
        name = self.manager.get_actual_folder_name("100")
        self.assertEqual(name, "100_2")

    def test_check_availability(self):
        # 유효하지 않은 입력
        result = self.manager.check_availability("abc")
        self.assertEqual(result["status"], "invalid")

        # 새로운 이름
        result = self.manager.check_availability("200")
        self.assertEqual(result["status"], "available")
        self.assertEqual(result["next_name"], "200")

        # 이미 존재하는 이름
        os.makedirs(os.path.join(self.test_dir, "200"))
        result = self.manager.check_availability("200")
        self.assertEqual(result["status"], "exists")
        self.assertEqual(result["next_name"], "200_1")

    def test_create_folder(self):
        success, path, status = self.manager.create_folder("300")
        self.assertTrue(success)
        self.assertEqual(status, "created")
        self.assertTrue(os.path.exists(path))

        # 이미 존재하는 폴더 생성 시도
        success, path, status = self.manager.create_folder("300")
        self.assertTrue(success)
        self.assertEqual(status, "existing")


class TestImageProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = ImageProcessor()
        # Mocking or setup for image processing tests would go here
        # For now, just checking instantiation
        pass

    def test_instantiation(self):
        self.assertIsInstance(self.processor, ImageProcessor)


class TestPrintManager(unittest.TestCase):
    def setUp(self):
        self.manager = PrintManager()

    def test_instantiation(self):
        self.assertIsInstance(self.manager, PrintManager)

if __name__ == '__main__':
    # QApplication 필요 (QMessageBox 등 사용 시)
    app = QApplication(sys.argv)
    unittest.main()
