"""Keep information on files and directories being watched"""

import hashlib
import os
import re
from typing import Dict, List, Tuple


class FileInfo:  # pylint: disable=too-few-public-methods
    """Class that manages file info"""

    def __init__(self, path: str):
        if os.path.isfile(path):
            self._datetime = os.path.getmtime(path)
            self._hash = FileInfo._calculate_hash(path)
        else:
            self._datetime = 0
            self._hash = ""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FileInfo):
            return NotImplemented
        return (self._datetime == other._datetime
                and self._hash == other._hash)

    @staticmethod
    def _calculate_hash(path: str):
        """Create a hash of file content

        Args:
            path (str): path to file
        """
        hasher = hashlib.sha1()
        with open(path, "rb") as file:
            data = file.read(65536)
            hasher.update(data)
        return hasher.hexdigest()


class DirInfo:  # pylint: disable=too-few-public-methods
    """Class that manages file info"""

    def __init__(self, path: str, ignore: List[re.Pattern]):
        if not os.path.isdir(path):
            raise RuntimeError(f"File not found {path}")
        self._path = path
        self._files, self._dirs = DirInfo._create_files_dirs(path, ignore)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DirInfo):
            return NotImplemented
        return self._files == other._files and self._dirs == other._dirs

    @staticmethod
    def _create_files_dirs(path: str,
                           ignore: List[re.Pattern]) -> Tuple[Dict[str, FileInfo], List[str]]:
        """Create a dict of files from the tree in path

        Args:
            path (str): path to directory
            ignore (List[re.Pattern]): list of ignore rules

        Returns:
            (Dict[str, FileInfo], List[str]): dictionary mapping file names to FileInfo and
                a list of directories
        """
        def _is_matched(full_file: str, ignore: List[re.Pattern]):
            for ign in ignore:
                if ign.fullmatch(full_file):
                    return True
            return False

        files = {}
        dirs: list[str] = []
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                full_file = os.path.join(dirpath, filename)
                if not _is_matched(full_file, ignore):
                    files[full_file] = FileInfo(full_file)
            for dirname in dirnames:
                full_dir = os.path.join(dirpath, dirname)
                if not _is_matched(full_dir, ignore):
                    dirs.append(full_dir)
                    subfiles, subdirs = DirInfo._create_files_dirs(full_dir, ignore)
                    files.update(subfiles)
                    dirs.extend(subdirs)
        return files, sorted(dirs)


class DirsAndFiles:  # pylint: disable=too-few-public-methods
    """Class that manages DirInfos and FileInfos"""

    def __init__(self, files: List[str], dirs: List[str], ignore: List[re.Pattern]):
        self._file_infos = DirsAndFiles._create_file_infos(sorted(files))
        self._ignore = ignore
        self._dir_infos = DirsAndFiles._create_dir_infos(sorted(dirs), ignore)

    def update(self) -> bool:
        """Update directory and files info and return if anything changed"""
        file_infos = DirsAndFiles._create_file_infos(sorted(self._file_infos.keys()))
        dir_infos = DirsAndFiles._create_dir_infos(sorted(self._dir_infos.keys()), self._ignore)

        changed = file_infos != self._file_infos or dir_infos != self._dir_infos
        self._file_infos = file_infos
        self._dir_infos = dir_infos

        return changed

    @staticmethod
    def _create_file_infos(files: List[str]) -> Dict[str, FileInfo]:
        """Create a dict of file X FileInfo

        Args:
            files (List[str]): list of files

        Returns:
            [Dict[str, FileInfo]: dictionary mapping file names to FileInfo
        """
        return {file: FileInfo(file) for file in files}

    @staticmethod
    def _create_dir_infos(dirs: List[str], ignore: List[re.Pattern]):
        """Create a dict of dir X DirInfo

        Args:
            dirs (List[str]): list of directories
            ignore (List[re.Pattern]): list of ignore rules

        Returns:
            [Dict[str, DirInfo]: dictionary mapping dir names to DirInfo
        """
        return {adir: DirInfo(adir, ignore) for adir in dirs}
