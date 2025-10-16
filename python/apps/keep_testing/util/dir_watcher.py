"""Dir watcher for modification"""

import logging
import os
from typing import List
import threading

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class DirWatcher(FileSystemEventHandler):
    """Watches directories for change events"""

    def __init__(self, files: List[str], dirs: List[str]) -> None:
        """Creates a watcher for directory changes

        Args:
            files (List[str]): file list to watch (will extract dirs)
            dirs (List[str]): directory list to watch
        """
        unique_dirs = DirWatcher._unify_dirs(files, dirs)

        self._modified = False
        self._started = False
        self._observer = Observer()
        self._lock = threading.Lock()
        for d in unique_dirs:
            self._observer.schedule(self, d, recursive=True)

    def start(self):
        """Starts monitoring"""
        with self._lock:
            if self._started:
                return
            self._observer.start()
            self._started = True
            self._modified = False

    def stop(self):
        """Stops the monitoring"""
        with self._lock:
            if not self._started:
                return
            self._observer.stop()
            self._observer.join()
            self._started = False
            self._modified = False

    def on_created(self, event):
        with self._lock:
            logging.debug("Created %s", event.src_path)
            self._modified = True

    def on_deleted(self, event):
        with self._lock:
            logging.debug("Deleted %s", event.src_path)
            self._modified = True

    def on_modified(self, event):
        with self._lock:
            logging.debug("Modified %s", event.src_path)
            self._modified = True

    def on_moved(self, event):
        with self._lock:
            logging.debug("Moved %s to %s", event.src_path, event.dest_path)
            self._modified = True

    @staticmethod
    def _unify_dirs(files: List[str], dirs: List[str]) -> List[str]:
        """Removes directories that are subdirs of other directories in the set"""
        unique_dirs = {os.path.dirname(file)
                       for file in files} if files else set()
        unique_dirs = unique_dirs.union(set(dirs) if dirs else set())
        watched: list[str] = []
        for candidate in sorted(unique_dirs):
            if not watched or not candidate.startswith(watched[-1]):
                watched.append(candidate)
        return watched

    def changed(self) -> bool:
        """Checks if there were any change events in watched dirs"""
        with self._lock:
            res = self._modified
            self._modified = False
        return res
