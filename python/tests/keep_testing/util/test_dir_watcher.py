"""Tests persistence.search module"""

# pylint: disable=protected-access

import itertools
import os
import shutil
import unittest

import apps.keep_testing.util.dir_watcher as dir_watcher
import tests.util.utils_tests_lib as utils


class TestDirWatcher(utils.TestWithTmpDir):
    """Tests DirWatcher class"""

    def setUp(self) -> None:
        super().setUp()

        dirs = [os.path.join(*el)
                for el in itertools.product([utils.TEST_DIR_PATH], ["bin", "build", "src", "src/app"])]  # pylint: disable=line-too-long
        files = ["file1.txt", "file2.txt", "file3.txt", "file4.txt"]
        self.dirs = [os.path.join(*el)
                     for el in itertools.product([utils.TEST_DIR_PATH], ["usr", "lib", "bin", "bin/exe"])]  # pylint: disable=line-too-long
        self.files = [os.path.join(*el) for el in itertools.product(dirs, files)]
        for subdir in self.dirs:
            os.mkdir(subdir)
        for subdir in dirs:
            if not os.path.isdir(subdir):
                os.mkdir(subdir)

        for file in self.files:
            utils.create_file(file)

        self.dir_not_watched = os.path.join(utils.TEST_DIR_PATH, "other")
        self.file_not_watched = os.path.join(utils.TEST_DIR_PATH, "other", "not_watched.txt")

        os.mkdir(self.dir_not_watched)
        utils.create_file(self.file_not_watched)

    def tearDown(self) -> None:
        shutil.rmtree(utils.TEST_DIR_PATH)

    def test_unify_dirs(self):
        """Test that unify_dirs creates a list with directories without repetition"""
        unique_dirs = dir_watcher.DirWatcher._unify_dirs(self.files, self.dirs)
        expect_dirs = [
            os.path.join(utils.TEST_DIR_PATH, "bin"),
            os.path.join(utils.TEST_DIR_PATH, "build"),
            os.path.join(utils.TEST_DIR_PATH, "lib"),
            os.path.join(utils.TEST_DIR_PATH, "src"),
            os.path.join(utils.TEST_DIR_PATH, "usr"),
        ]
        self.assertEqual(unique_dirs, expect_dirs)

    def test_no_change(self):
        """Test that when nothing is changed returns False"""
        watcher = dir_watcher.DirWatcher(self.files, self.dirs)
        self.assertFalse(watcher.changed())

    def test_change_file(self):
        """Test that when a file is changed returns True"""
        watcher = dir_watcher.DirWatcher(self.files, self.dirs)

        for file in self.files:
            utils.change_file(file)
            self.assertTrue(watcher.changed(), msg=file)

        utils.change_file(self.file_not_watched)
        self.assertFalse(watcher.changed(), msg=self.file_not_watched)

    def test_no_change_after_check(self):
        """Test that after checking for change, the next check is False"""
        watcher = dir_watcher.DirWatcher(self.files, self.dirs)

        for file in self.files:
            utils.change_file(file)
            self.assertTrue(watcher.changed(), msg=file)
            self.assertFalse(watcher.changed(), msg=file)

    def test_create_file(self):
        """Test that when a file is craeted returns True"""
        watcher = dir_watcher.DirWatcher(self.files, self.dirs)

        for adir in self.dirs:
            new_file = os.path.join(adir, "new_file.txt")
            utils.create_file(new_file)
            self.assertTrue(watcher.changed())

        utils.create_file(os.path.join(self.dir_not_watched, "new_file.txt"))
        self.assertFalse(watcher.changed(), msg=self.file_not_watched)

    def test_delete_file(self):
        """Test that when a file is deleted returns True"""
        watcher = dir_watcher.DirWatcher(self.files, self.dirs)

        for file in self.files:
            os.remove(file)
            self.assertTrue(watcher.changed())

        os.remove(self.file_not_watched)
        self.assertFalse(watcher.changed(), msg=self.file_not_watched)

    def test_create_dir(self):
        """Test that when a directory is craeted returns True"""
        watcher = dir_watcher.DirWatcher(self.files, self.dirs)

        for adir in self.dirs:
            new_dir = os.path.join(adir, "new_dir")
            os.mkdir(new_dir)
            self.assertTrue(watcher.changed())

        os.mkdir(os.path.join(self.dir_not_watched, "new_dir"))
        self.assertFalse(watcher.changed(), msg=self.file_not_watched)

    def test_delete_dir(self):
        """Test that when a directory is removed returns True"""
        for file in self.files:
            os.remove(file)
        os.remove(self.file_not_watched)

        watcher = dir_watcher.DirWatcher([], self.dirs)

        for adir in sorted(self.dirs, reverse=True):
            os.rmdir(adir)
            self.assertTrue(watcher.changed())

        os.rmdir(self.dir_not_watched)
        self.assertFalse(watcher.changed(), msg=self.file_not_watched)

    def test_create_file_in_created_dir(self):
        """Test that when a file is craeted under a created dir returns True"""
        watcher = dir_watcher.DirWatcher([], self.dirs)

        for adir in self.dirs:
            new_dir = os.path.join(adir, "new_dir")
            os.mkdir(new_dir)
            self.assertTrue(watcher.changed())
            new_file = os.path.join(new_dir, "new_file.txt")
            utils.create_file(new_file)
            self.assertTrue(watcher.changed())

        os.mkdir(os.path.join(self.dir_not_watched, "new_dir"))
        self.assertFalse(watcher.changed())
        utils.create_file(os.path.join(self.dir_not_watched, "new_dir", "new_file.txt"))
        self.assertFalse(watcher.changed())

    def test_create_dir_in_created_dir(self):
        """Test that when a dir is craeted under a created dir returns True"""
        watcher = dir_watcher.DirWatcher([], self.dirs)

        for adir in self.dirs:
            new_dir = os.path.join(adir, "new_dir")
            os.mkdir(new_dir)
            self.assertTrue(watcher.changed())
            new_sub_dir = os.path.join(adir, "new_dir", "sub_dir")
            os.mkdir(new_sub_dir)
            self.assertTrue(watcher.changed())

        os.mkdir(os.path.join(self.dir_not_watched, "new_dir"))
        self.assertFalse(watcher.changed())
        os.mkdir(os.path.join(self.dir_not_watched, "new_dir", "sub_dir"))
        self.assertFalse(watcher.changed())


if __name__ == "__main__":
    unittest.main()
