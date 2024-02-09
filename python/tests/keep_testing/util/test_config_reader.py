"""Tests config reader"""

# pylint: disable=protected-access

import os
import unittest

import apps.keep_testing.util.config_reader as config_reader
import tests.util.utils_tests_lib as utils


class TestConfigReader(utils.TestWithTmpDir):
    """Tests ConfigReader class"""

    def setUp(self) -> None:
        super().setUp()
        self.file_path = os.path.join(utils.TEST_DIR_PATH, "file.toml")

    def test_basic_config(self):
        """Test a file with basic config"""
        self._fill_file(
            """
            cmds = ["ls -l", "echo 'command 1'"]
            dirs = ["/path/to/dir1", "/path/to/dir2"]
            files = ["path/to/file1.txt", "/path/to/file2.txt"]
            ignores = [".*\\\\.git", ".*\\\\.idea"]
            """
        )
        reader = config_reader.ConfigReader(self.file_path)
        self.assertEqual(reader.cmds(), ["ls -l", "echo 'command 1'"])
        self.assertEqual(reader.dirs(), ["/path/to/dir1", "/path/to/dir2"])
        self.assertEqual(reader.files(), [
                         "path/to/file1.txt", "/path/to/file2.txt"])
        self.assertEqual(reader.ignores(), [".*\\.git", ".*\\.idea"])

    def test_empty_file(self):
        """Test an empty toml file"""
        self._fill_file("")
        reader = config_reader.ConfigReader(self.file_path)
        self.assertEqual(reader.cmds(), [])
        self.assertEqual(reader.dirs(), [])
        self.assertEqual(reader.files(), [])
        self.assertEqual(reader.ignores(), [])

    def test_no_file(self):
        """Test an empty toml file"""
        reader = config_reader.ConfigReader("")
        self.assertEqual(reader.cmds(), [])
        self.assertEqual(reader.dirs(), [])
        self.assertEqual(reader.files(), [])
        self.assertEqual(reader.ignores(), [])

    def test_error_not_list(self):
        """Test a file with basic config"""
        some_string = '"some string"'
        for key in ["cmds", "dirs", "files", "ignores"]:
            self._fill_file(f"{key} = {some_string}")
            with self.assertRaises(ValueError):
                config_reader.ConfigReader(self.file_path)

    def _fill_file(self, content: str) -> None:
        with open(self.file_path, "w", encoding="utf-8") as file:
            print(content, file=file)


if __name__ == "__main__":
    unittest.main()
