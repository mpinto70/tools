"""Unit tests main driver"""

import os
import sys
import unittest

dir_tests = os.path.dirname(os.path.realpath(__file__))

test_loader = unittest.defaultTestLoader.discover(dir_tests)
test_runner = unittest.TextTestRunner()
result = test_runner.run(test_loader)
if not result.wasSuccessful():
    sys.exit(1)
