"""Helpers for lib tests"""

import os
import shutil
import unittest

SCRIPT_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
TEST_DIR_PATH = os.path.join(SCRIPT_DIR_PATH, "tmp")


class TestWithTmpDir(unittest.TestCase):
    """Base class for all tests in lib"""

    def setUp(self) -> None:
        if os.path.isdir(TEST_DIR_PATH):
            shutil.rmtree(TEST_DIR_PATH)
        self.maxDiff = None  # pylint: disable=invalid-name
        os.mkdir(TEST_DIR_PATH)

    def tearDown(self) -> None:
        shutil.rmtree(TEST_DIR_PATH)


def create_file(filename: str):
    """Creates a file with some content"""
    with open(filename, "w") as file:
        print("more content", file=file)


def change_file(filename: str):
    """Changes the contents of file"""
    with open(filename, "a") as file:
        print("more content", file=file)
