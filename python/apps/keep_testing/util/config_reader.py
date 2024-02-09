"""A reader for configuration in TOML files"""

import os
import tomllib
from typing import List


class ConfigReader:  # pylint: disable=too-few-public-methods
    """Read TOML configuration file with execution parameters"""
    CMDS = "cmds"
    DIRS = "dirs"
    FILES = "files"
    IGNORES = "ignores"

    def __init__(self, config_file: str) -> None:
        """Creates the config file reader

        Args:
            config_file: path to the configuration file
        """
        if not config_file:
            self._data = {}
            return

        if not os.path.isfile(config_file):
            raise FileNotFoundError(
                f"Configuration file not found: {config_file}")

        with open(config_file, "rb") as f:
            self._data = tomllib.load(f)

        for key in [self.CMDS, self.DIRS, self.FILES, self.IGNORES]:
            if key in self._data and not isinstance(self._data[key], list):
                raise ValueError(f"'{key}' should be a list")

    def cmds(self) -> List[str]:
        """Returns the list of commands to execute"""
        return self._return_list(self.CMDS)

    def dirs(self) -> List[str]:
        """Returns the list of directories to watch"""
        return self._return_list(self.DIRS)

    def files(self) -> List[str]:
        """Returns the list of files to watch"""
        return self._return_list(self.FILES)

    def ignores(self) -> List[str]:
        """Returns the list of items to ignore"""
        return self._return_list(self.IGNORES)

    def _return_list(self, key: str) -> List[str]:
        """Returns the list of 'key' values"""
        return self._data[key] if key in self._data else []
