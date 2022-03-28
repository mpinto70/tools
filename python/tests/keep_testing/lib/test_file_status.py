"""Tests persistence.search module"""

# pylint: disable=protected-access

from encodings import utf_8
import hashlib
import itertools
import os
import random
import re
import unittest

import apps.keep_testing.lib.file_status as file_status
import tests.lib.utils_tests_lib as utils


class TestFileInfo(utils.TestWithTmpDir):
    """Tests FileInfo class"""

    def setUp(self) -> None:
        super().setUp()
        self.file1_path = os.path.join(utils.TEST_DIR_PATH, "file1.txt")
        self.file2_path = os.path.join(utils.TEST_DIR_PATH, "file2.txt")
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


class TestDirInfo(utils.TestWithTmpDir):
    """Tests FileInfo class"""

    def setUp(self) -> None:
        super().setUp()
        dirs = ["bin", "build", "src"]
        files = ["file1.txt", "file2.txt", "file3.txt", "file4.txt"]
        self.dirs = [os.path.join(*element)
                     for element in itertools.product([utils.TEST_DIR_PATH], dirs)]
        self.files = [os.path.join(*element) for element in itertools.product(self.dirs, files)]
        for subdir in self.dirs:
            os.mkdir(subdir)
        for file_path in self.files:
            with open(file_path, "w", encoding="utf_8") as file:
                print(file_path, file=file)

    def test_create_no_ignore(self):
        """Test creation of DirInfo without ignore."""
        dir_info = file_status.DirInfo(utils.TEST_DIR_PATH, [])
        self.assertEqual(dir_info._path, utils.TEST_DIR_PATH)
        expected_files = {file: file_status.FileInfo(file) for file in self.files}
        self.assertEqual(dir_info._files, expected_files)

    def test_create_with_ignore(self):
        """Test creation of DirInfo with ignore."""
        os.mkdir(os.path.join(utils.TEST_DIR_PATH, "build", "ignored"))

        dir_info = file_status.DirInfo(
            utils.TEST_DIR_PATH, [re.compile(r".*1.txt"), re.compile(r".*/build\b.*")])
        self.assertEqual(dir_info._path, utils.TEST_DIR_PATH)

        filtered = list(filter(lambda file: not (file.endswith(
            "file1.txt") or "build" in file), self.files))

        expected_files = {file: file_status.FileInfo(file) for file in filtered}
        self.assertEqual(dir_info._files, expected_files)
        # dirs[1] is build that is ignored
        self.assertEqual(dir_info._dirs, [self.dirs[0], self.dirs[2]])

    def test_create_with_subdir_in_ignored_dir(self):
        """Test creation of DirInfo with ignore."""
        dir_info_0 = file_status.DirInfo(
            utils.TEST_DIR_PATH, [re.compile(r".*1.txt"), re.compile(r".*/build/.*")])

        os.mkdir(os.path.join(self.dirs[1], "new_dir"))  # build is ignored

        dir_info_1 = file_status.DirInfo(
            utils.TEST_DIR_PATH, [re.compile(r".*1.txt"), re.compile(r".*/build/.*")])

        self.assertEqual(dir_info_0, dir_info_1)


class TestDirsAndFilesInfo(utils.TestWithTmpDir):
    """Tests DirsAndFilesInfo class"""

    def setUp(self) -> None:
        super().setUp()
        dirs = [os.path.join(*el)
                for el in itertools.product([utils.TEST_DIR_PATH], ["bin", "build", "src"])]
        files = ["file1.txt", "file2.txt", "file3.txt", "file4.txt"]
        self.dirs = [os.path.join(*el)
                     for el in itertools.product([utils.TEST_DIR_PATH], ["usr", "lib"])]
        self.files = [os.path.join(*el) for el in itertools.product(dirs, files)]
        self.ignores = [
            re.compile(r".*ignore.*"),
            re.compile(r".*/usr/.*"),
        ]
        for subdir in self.dirs:
            os.mkdir(subdir)
        for subdir in dirs:
            os.mkdir(subdir)
        for file_path in self.files:
            with open(file_path, "w", encoding="utf_8") as file:
                print(file_path, file=file)

    def test_create_file_infos(self):
        """Test create_file_infos create FileInfo dict"""
        file_infos = file_status.DirsAndFiles._create_file_infos(self.files)
        expected = {file: file_status.FileInfo(file) for file in self.files}
        self.assertEqual(file_infos, expected)

    def test_create_dir_infos(self):
        """Test create_dir_infos create DirInfo dict"""
        dir_infos = file_status.DirsAndFiles._create_dir_infos(self.dirs, self.ignores)
        expected = {adir: file_status.DirInfo(adir, self.ignores) for adir in self.dirs}
        self.assertEqual(dir_infos, expected)

    def test_create(self):
        """Test creation of object"""
        dirs_and_files = file_status.DirsAndFiles(self.files, self.dirs, self.ignores)
        file_infos = file_status.DirsAndFiles._create_file_infos(self.files)
        dir_infos = file_status.DirsAndFiles._create_dir_infos(self.dirs, self.ignores)

        self.assertEqual(dirs_and_files._file_infos, file_infos)
        self.assertEqual(dirs_and_files._dir_infos, dir_infos)
        self.assertEqual(dirs_and_files._ignore, self.ignores)

    def test_change_in_files(self):
        """Test change in files are reported as True"""
        dirs_and_files = file_status.DirsAndFiles(self.files, self.dirs, self.ignores)
        self.assertFalse(dirs_and_files.update())
        for file in self.files:
            utils.change_file(file)
            self.assertTrue(dirs_and_files.update())
            self.assertFalse(dirs_and_files.update())  # subsequent calls always return False

    def test_change_in_ignored_files(self):
        """Test change in ignored files/dirs are reported as False"""
        dirs_and_files = file_status.DirsAndFiles(self.files, self.dirs, self.ignores)

        utils.change_file(os.path.join(self.dirs[0], "some-file"))  # /usr/ is ignored
        self.assertFalse(dirs_and_files.update())
        utils.change_file(os.path.join(self.dirs[1], "file-ignored.txt"))
        self.assertFalse(dirs_and_files.update())

    def test_creation_of_new_files(self):
        """Test creation of files are reported as True"""
        dirs_and_files = file_status.DirsAndFiles(self.files, self.dirs, self.ignores)

        utils.change_file(os.path.join(self.dirs[1], "some-file"))  # /lib/ is not ignored
        self.assertTrue(dirs_and_files.update())

    def test_creation_of_new_dirs(self):
        """Test creation of directories are reported as True"""
        dirs_and_files = file_status.DirsAndFiles(self.files, self.dirs, self.ignores)

        os.mkdir(os.path.join(self.dirs[1], "some-dir"))  # /lib/ is not ignored
        self.assertTrue(dirs_and_files.update())


if __name__ == "__main__":
    unittest.main()
