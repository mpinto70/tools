"""Keep information on files and directories being watched"""

import hashlib
import os
import re
from typing import Dict, List, Tuple


class FileInfo:  # pylint: disable=too-few-public-methods
    """Class that manages file info"""

    def __init__(self, path: str):
        if os.path.isfile(path):
            self._hash = FileInfo._calculate_hash(path)
        else:
            self._hash = ""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FileInfo):
            return NotImplemented
        return self._hash == other._hash

    @staticmethod
    def _calculate_hash(path: str):
        """Create a hash of file content

        Args:
            path (str): path to file
        """
        hasher = hashlib.sha1()
        with open(path, "rb") as file:
            while True:
                data = file.read(65536)
                if not data:
                    break
                hasher.update(data)
        return hasher.hexdigest()


def _changed_files(lhs: Dict[str, FileInfo], rhs: Dict[str, FileInfo]) -> List[str]:
    """Return a list of files that has changed from lhs to rhs

    Args:
        lhs (Dict[str, FileInfo]): the first list
        rhs (Dict[str, FileInfo]): the second list

    Returns:
        List[str]: list of changed files
    """
    if lhs == rhs:
        return []

    result = []
    for file_name, file_info in lhs.items():
        if file_name not in rhs:
            result.append(f"deleted {file_name}")
        elif file_info != rhs[file_name]:
            result.append(f"changed {file_name}")

    for file_name in rhs:
        if file_name not in lhs:
            result.append(f"created {file_name}")

    return result


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

    def changed(self, other: object) -> List[str]:
        """ Return a list of changed files and directories

        Args:
            other (object): the other object

        Returns:
            List[str]: changed files and directories
        """
        if not isinstance(other, DirInfo):
            return []

        if self._files == other.files and self._dirs == other.dirs:
            return []

        result = _changed_files(self._files, other.files)

        for adir in self._dirs:
            if adir not in other.dirs:
                result.append(f"deleted {adir}")

        for adir in other.dirs:
            if adir not in self._dirs:
                result.append(f"created {adir}")

        return result

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
                    subfiles, subdirs = DirInfo._create_files_dirs(
                        full_dir, ignore)
                    files.update(subfiles)
                    dirs.extend(subdirs)
        return files, sorted(dirs)

    @property
    def files(self) -> Dict[str, FileInfo]:
        """Returns the files

        Returns:
            Dict[str, FileInfo]: the files
        """
        return self._files

    @property
    def dirs(self) -> List[str]:
        """Returns the dirs

        Returns:
            List[str]: the dirs
        """
        return self._dirs


def _changed_dirs(lhs: Dict[str, DirInfo], rhs: Dict[str, DirInfo]) -> List[str]:
    """Return a list of files that has changed from lhs to rhs

    Args:
        lhs (Dict[str, DirInfo]): the first list
        rhs (Dict[str, DirInfo]): the second list

    Returns:
        List[str]: list of changed files
    """
    if lhs == rhs:
        return []

    result = []
    for dir_name, dir_info in lhs.items():
        if dir_name not in rhs:
            result.append(f"deleted {dir_name}")
        else:
            result.extend(dir_info.changed(rhs[dir_name]))

    for dir_name in rhs:
        if dir_name not in lhs:
            result.append(f"created {dir_name}")

    return result


class DirsAndFiles:  # pylint: disable=too-few-public-methods
    """Class that manages DirInfos and FileInfos"""

    def __init__(self, files: List[str], dirs: List[str], ignore: List[re.Pattern]):
        self._file_infos = DirsAndFiles._create_file_infos(sorted(files))
        self._ignore = ignore
        self._dir_infos = DirsAndFiles._create_dir_infos(sorted(dirs), ignore)

    def update(self) -> List[str]:
        """Update directory and files info and return if anything changed"""
        file_infos = DirsAndFiles._create_file_infos(
            sorted(self._file_infos.keys()))
        dir_infos = DirsAndFiles._create_dir_infos(
            sorted(self._dir_infos.keys()), self._ignore)

        changed = _changed_files(self._file_infos, file_infos) + \
            _changed_dirs(self._dir_infos, dir_infos)
        self._file_infos = file_infos
        self._dir_infos = dir_infos

        return sorted(changed)

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
