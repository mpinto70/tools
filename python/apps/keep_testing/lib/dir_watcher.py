"""Dir watcher for modification"""

import os
from typing import List

import inotify.adapters


class DirWatcher:  # pylint: disable=too-few-public-methods
    """Watches directories for change events"""

    EVENTS_WATCHED = (
        inotify.constants.IN_MODIFY |
        inotify.constants.IN_ATTRIB |
        inotify.constants.IN_MOVED_FROM |
        inotify.constants.IN_MOVED_TO |
        inotify.constants.IN_CREATE |
        inotify.constants.IN_DELETE |
        inotify.constants.IN_DELETE_SELF |
        inotify.constants.IN_MOVE_SELF
    )

    def __init__(self, files: List[str], dirs: List[str]) -> None:
        """Creates a watcher for directory changes

        Args:
            files (List[str]): file list to watch (will extract dirs)
            dirs (List[str]): directory list to watch
        """
        unique_dirs = DirWatcher._unify_dirs(files, dirs)

        self._watcher = inotify.adapters.InotifyTrees(unique_dirs, mask=self.EVENTS_WATCHED)

    @staticmethod
    def _unify_dirs(files: List[str], dirs: List[str]) -> List[str]:
        """Removes directories that are subdirs of other directories in the set"""
        unique_dirs = {os.path.dirname(file) for file in files}
        unique_dirs = unique_dirs.union(set(dirs))
        watched: list[str] = []
        for candidate in sorted(unique_dirs):
            if not watched or not candidate.startswith(watched[-1]):
                watched.append(candidate)
        return watched

    def changed(self) -> bool:
        """Checks if there were any change events in watched dirs"""
        return len(list(self._watcher.event_gen(timeout_s=0))) > 0
