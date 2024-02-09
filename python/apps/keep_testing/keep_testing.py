"""Keep running a command every time a change in a tree occurs"""

import argparse
import logging
import os
import re
import select
import sys
import threading
import time
from typing import List

import apps.keep_testing.util.config_reader as config_reader
import apps.keep_testing.util.dir_watcher as dir_watcher
import apps.keep_testing.util.file_status as file_status
import apps.util.config_log as config_log


class EnterMonitor(threading.Thread):
    """Montiors Enters pressed by user"""
    enter_pressed = False

    def __init__(self):
        super().__init__()
        self._done = False

    def run(self):
        """Enter a loop until user press Ctrl+C monitoring Enter"""
        logging.info("Start monitoring <ENTER>")
        self._done = False
        while not self._done:
            inp, _, _ = select.select([sys.stdin], [], [], 0.5)
            if inp:
                logging.info("<ENTER> detected")
                sys.stdin.readline()
                EnterMonitor.enter_pressed = True

        logging.info("Leaving <ENTER> monitoring")

    def stop(self):
        """Stops the monitoring"""
        self._done = True


def normalize_paths(paths: List[str], exists) -> List[str]:
    """Normilize all paths to get full path

    Args:
        paths (List[str]): original paths
        exists (function): function to check existence (isfile | isdir)

    Raises:
        RuntimeError: if path is not found

    Returns:
        List[str]: normilized paths
    """
    logging.debug("normalize_paths(%s)", paths)
    if not paths:
        return []
    result = []
    for path in paths:
        if not exists(path):
            logging.critical("Path not found %s", path)
            raise RuntimeError(f"Path not found {path}")
        result.append(os.path.realpath(path))
    return result


def create_regexes(texts: List[str]) -> List[re.Pattern]:
    """Compiles regular expressions

    Args:
        texts (List[str]): text of regular expressions

    Returns:
        List[re.Pattern]: compiled regular expressions
    """
    logging.debug("create_regex(%s)", texts)
    if not texts:
        return []
    result = []
    for text in texts:
        result.append(re.compile(text))
    return result


def execution_loop(cmds: List[str],
                   files: List[str],
                   dirs: List[str],
                   ignore: List[re.Pattern],
                   sleep: float):
    """Loops indefinetely executing `cmds` and checking `dirs` and `files` for changes
    except the ones that match `ignore`

    Args:
        cmds (List[str]): commands to execute
        dirs (List[str]): directories to watch
        files (List[str]): files to watch
        ignore (List[re.Pattern]): regex applied to `dirs` and `files` to ignore
        sleep (float): time to wait between two notifications check
    """

    logging.debug("Starting watching")
    dirs_files = file_status.DirsAndFiles(files, dirs, ignore)
    logging.debug("Information gathered")
    while True:
        for cmd in cmds:
            logging.info("Executing: %s", cmd)
            if os.system(cmd) == 0:
                logging.info("Success: %s", cmd)
            else:
                logging.error("Command failed: %s", cmd)
                break

        changed: List[str] = []
        EnterMonitor.enter_pressed = False
        while not changed and not EnterMonitor.enter_pressed:
            EnterMonitor.enter_pressed = False
            begin = time.time()
            changed = dirs_files.update()
            end = time.time()
            logging.debug("Time to check: %f", end - begin)
            if changed:
                logging.info("Changes detected:")
                for change in changed:
                    logging.info("- %s", change)
                break
            watcher = dir_watcher.DirWatcher(files, dirs)
            logging.info("Monitoring dir changes and <ENTER> key presses")
            while not watcher.changed() and not EnterMonitor.enter_pressed:
                time.sleep(sleep)


def main():
    """Keep running commands watching directories"""
    monitor = EnterMonitor()
    try:
        parser = argparse.ArgumentParser(
            description="Keep runing a command based on changes in a tree",
            formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("-c", "--cmds",
                            type=str,
                            nargs="+",
                            help="command(s) to execute",
                            action="extend",
                            default=[])
        parser.add_argument("-d", "--dirs",
                            type=str,
                            nargs="+",
                            help="directory(ies) to watch",
                            action="extend",
                            default=[])
        parser.add_argument("-f", "--files",
                            type=str,
                            nargs="+",
                            help="file(s) to watch",
                            action="extend",
                            default=[])
        parser.add_argument("-i", "--ignores",
                            type=str,
                            nargs="+",
                            help="files or directories to ignore (regexes)",
                            action="extend",
                            default=[])
        parser.add_argument("-s", "--sleep",
                            type=float,
                            default=0.2)
        parser.add_argument("--config",
                            type=str,
                            help="TOML config file that has cmds, dirs, files and ignores",
                            default="")
        parser.add_argument("--debug", action="store_true",
                            help="set log level to DEBUG")

        args = parser.parse_args()

        config_log.init(args.debug)

        config = config_reader.ConfigReader(args.config)
        cmds = args.cmds + config.cmds()
        dirs = args.dirs + config.dirs()
        files = args.files + config.files()
        ignores = args.ignores + config.ignores()

        logging.info("Executing %s", cmds)
        if not cmds:
            logging.critical("You must inform commands to execute")
            sys.exit(1)
        if dirs:
            logging.info("Watching dirs %s", dirs)
        if files:
            logging.info("Watching files %s", files)
        if ignores:
            logging.info("Ignoring %s", ignores)

        files = normalize_paths(files, os.path.isfile)
        dirs = normalize_paths(dirs, os.path.isdir)
        ignores = create_regexes(ignores)
        monitor.start()
        execution_loop(cmds, files, dirs, ignores, args.sleep)
    except KeyboardInterrupt:
        logging.info("Ctrl+C pressed")
    monitor.stop()
    monitor.join()


if __name__ == "__main__":
    main()
