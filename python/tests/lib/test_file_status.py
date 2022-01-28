"""Tests persistence.search module"""

# pylint: disable=protected-access

import hashlib
import os
import random
import shutil
import unittest

import apps.lib.file_status as file_status


SCRIPT_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
TEST_DIR_PATH = os.path.join(SCRIPT_DIR_PATH, "tmp")


class _TestFileStatusBase(unittest.TestCase):
    """Base class for all file_status tests"""

    def setUp(self) -> None:
        self.maxDiff = None  # pylint: disable=invalid-name
        os.mkdir(TEST_DIR_PATH)

    def tearDown(self) -> None:
        shutil.rmtree(TEST_DIR_PATH)


class TestFileInfo(_TestFileStatusBase):
    """Tests FileInfo class"""

    def setUp(self) -> None:
        super().setUp()
        self.file1_path = os.path.join(TEST_DIR_PATH, "file1.txt")
        self.file2_path = os.path.join(TEST_DIR_PATH, "file2.txt")
        self.file1_content = f"Some content {random.randint(500, 1500)}"
        self.file2_content = f"Other content {random.randint(500, 1500)}"
        with open(self.file1_path, "w") as file:
            print(self.file1_content, file=file)
        with open(self.file2_path, "w") as file:
            print(self.file2_content, file=file)

    def test_hash(self):
        """Test that hash function calculates sha1"""
        hasher = hashlib.sha1()
        hasher.update(str.encode(f"{self.file1_content}\n", ))
        expected_hash = hasher.hexdigest()
        self.assertEqual(file_status.FileInfo._calculate_hash(self.file1_path), expected_hash)

        hasher = hashlib.sha1()
        hasher.update(str.encode(f"{self.file2_content}\n", ))
        expected_hash = hasher.hexdigest()
        self.assertEqual(file_status.FileInfo._calculate_hash(self.file2_path), expected_hash)

    def test_create(self):
        """Test creation of FileInfo"""
        file_info = file_status.FileInfo(self.file1_path)
        self.assertEqual(file_info._datetime, os.path.getmtime(self.file1_path))
        self.assertEqual(file_info._hash, file_status.FileInfo._calculate_hash(self.file1_path))

        file_info = file_status.FileInfo(self.file2_path)
        self.assertEqual(file_info._datetime, os.path.getmtime(self.file2_path))
        self.assertEqual(file_info._hash, file_status.FileInfo._calculate_hash(self.file2_path))

    def test_create_non_existent(self):
        """Test creation of FileInfo with non-existent file"""
        file_info = file_status.FileInfo("non-existent")
        self.assertEqual(file_info._datetime, 0)
        self.assertEqual(file_info._hash, "")

    def test_comparison(self):
        """Test comparisons of FileInfo's"""
        non_existent = file_status.FileInfo("non-existent")
        file1_info = file_status.FileInfo(self.file1_path)
        file2_info = file_status.FileInfo(self.file2_path)

        self.assertEqual(file1_info, file_status.FileInfo(self.file1_path))
        self.assertNotEqual(file1_info, file_status.FileInfo(self.file2_path))
        self.assertEqual(file2_info, file_status.FileInfo(self.file2_path))
        self.assertNotEqual(file2_info, file_status.FileInfo(self.file1_path))
        self.assertEqual(non_existent, file_status.FileInfo("non-existent-2"))

        self.assertNotEqual(file1_info, non_existent)
        self.assertNotEqual(file2_info, non_existent)


if __name__ == "__main__":
    unittest.main()
