"""Tests persistence.search module"""

# pylint: disable=protected-access

import itertools
import os
import time
import shutil
import unittest

import apps.keep_testing.util.dir_watcher as dir_watcher

import tests.util.utils_tests_lib as utils


class TestDirWatcher(utils.TestWithTmpDir):
    """Tests DirWatcher class"""

    def setUp(self) -> None:
        super().setUp()

        dirs = [
            os.path.join(*el)
            for el in itertools.product(
                [utils.TEST_DIR_PATH], ["bin", "build", "src", "src/app"]
            )
        ]
        files = ["file1.txt", "file2.txt", "file3.txt", "file4.txt"]
        self.dirs = [
            os.path.join(*el)
            for el in itertools.product(
                [utils.TEST_DIR_PATH], ["usr", "lib", "bin", "bin/exe"]
            )
        ]
        self.files = [os.path.join(*el)
                      for el in itertools.product(dirs, files)]

        for subdir in self.dirs:
            os.mkdir(subdir)
        for subdir in dirs:
            if not os.path.isdir(subdir):
                os.mkdir(subdir)

        for filename in self.files:
            # create file
            with open(filename, "w") as file:
                print(f"content for {filename}", file=file)

        self.dir_not_watched = os.path.join(utils.TEST_DIR_PATH, "other")
        self.file_not_watched = os.path.join(
            utils.TEST_DIR_PATH, "other", "not_watched.txt"
        )

        os.mkdir(self.dir_not_watched)
        utils.create_file(self.file_not_watched)

        time.sleep(0.2)

        self.watcher = dir_watcher.DirWatcher(self.files, self.dirs)
        self.watcher.start()

    def tearDown(self) -> None:
        self.watcher.stop()
        shutil.rmtree(utils.TEST_DIR_PATH)

    def _changed(self) -> bool:
        return self.watcher.changed()

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
        self.assertFalse(self._changed())

    def test_change_file(self):
        """Test that when a file is changed returns True"""
        for file in self.files:
            utils.change_file(file)
            self.assertTrue(self._changed(), msg=file)

        utils.change_file(self.file_not_watched)
        self.assertFalse(self._changed(), msg=self.file_not_watched)

    def test_no_change_after_check(self):
        """Test that after checking for change, the next check is False"""
        for file in self.files:
            utils.change_file(file)
            self.assertTrue(self._changed(), msg=file)
            self.assertFalse(self._changed(), msg=file)

    def test_create_file(self):
        """Test that when a file is created returns True"""
        for adir in self.dirs:
            new_file = os.path.join(adir, "new_file.txt")
            utils.create_file(new_file)
            self.assertTrue(self._changed())

        utils.create_file(os.path.join(self.dir_not_watched, "new_file.txt"))
        self.assertFalse(self._changed(), msg=self.file_not_watched)

    def test_delete_file(self):
        """Test that when a file is deleted returns True"""
        for file in self.files:
            utils.remove_file(file)
            self.assertTrue(self._changed())

        utils.remove_file(self.file_not_watched)
        self.assertFalse(self._changed(), msg=self.file_not_watched)

    def test_create_dir(self):
        """Test that when a directory is created returns True"""
        for adir in self.dirs:
            new_dir = os.path.join(adir, "new_dir")
            utils.create_dir(new_dir)
            self.assertTrue(self._changed())

        utils.create_dir(os.path.join(self.dir_not_watched, "new_dir"))
        self.assertFalse(self._changed(), msg=self.file_not_watched)

    def test_delete_dir(self):
        """Test that when a directory is removed returns True"""
        for file in self.files:
            utils.remove_file(file)
        utils.remove_file(self.file_not_watched)

        self.watcher.stop()  # will create it differently
        self.watcher = dir_watcher.DirWatcher([], self.dirs)
        self.watcher.start()

        for adir in sorted(self.dirs, reverse=True):
            utils.remove_dir(adir)
            self.assertTrue(self._changed())

        utils.remove_dir(self.dir_not_watched)
        self.assertFalse(self._changed(), msg=self.file_not_watched)

    def test_create_file_in_created_dir(self):
        """Test that when a file is created under a created dir returns True"""
        self.watcher.stop()  # will create it differently
        self.watcher = dir_watcher.DirWatcher([], self.dirs)
        self.watcher.start()

        for adir in self.dirs:
            new_dir = os.path.join(adir, "new_dir")
            utils.create_dir(new_dir)
            self.assertTrue(self._changed())
            new_file = os.path.join(new_dir, "new_file.txt")
            utils.create_file(new_file)
            self.assertTrue(self._changed())

        utils.create_dir(os.path.join(self.dir_not_watched, "new_dir"))
        self.assertFalse(self._changed())
        utils.create_file(os.path.join(
            self.dir_not_watched, "new_dir", "new_file.txt"))
        self.assertFalse(self._changed())

    def test_create_dir_in_created_dir(self):
        """Test that when a dir is created under a created dir returns True"""
        self.watcher.stop()  # will create it differently
        self.watcher = dir_watcher.DirWatcher([], self.dirs)
        self.watcher.start()

        for adir in self.dirs:
            new_dir = os.path.join(adir, "new_dir")
            utils.create_dir(new_dir)

            self.assertTrue(self._changed())
            new_sub_dir = os.path.join(adir, "new_dir", "sub_dir")
            utils.create_dir(new_sub_dir)
            self.assertTrue(self._changed())

        utils.create_dir(os.path.join(self.dir_not_watched, "new_dir"))
        self.assertFalse(self._changed())
        utils.create_dir(os.path.join(
            self.dir_not_watched, "new_dir", "sub_dir"))
        self.assertFalse(self._changed())


if __name__ == "__main__":
    unittest.main()
