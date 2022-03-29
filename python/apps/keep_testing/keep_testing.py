"""Keep running a command every time a change in a tree occurs"""

import argparse
import logging
import os
import re
import time
from typing import List

import apps.util.config_log as config_log
import apps.keep_testing.util.file_status as file_status
import apps.keep_testing.util.dir_watcher as dir_watcher


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
    """

    logging.debug("Starting watching")
    dirs_files = file_status.DirsAndFiles(files, dirs, ignore)
    logging.debug("Information gathered")
    while True:
        for cmd in cmds:
            if os.system(cmd) == 0:
                logging.info("Success: %s", cmd)
            else:
                logging.error("Command failed: %s", cmd)
                break

        changed: List[str] = []
        while not changed:
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
            while not watcher.changed():
                time.sleep(sleep)


def main():
    """Keep running commands watching directories"""

    try:

        parser = argparse.ArgumentParser(
            description="Keep runing a command based on changes in a tree",
            formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("-c", "--cmds", type=str, nargs="+", required=True,
                            help="command(s) to execute", action="extend")
        parser.add_argument("-d", "--dirs", type=str, nargs="+",
                            help="directory(ies) to watch", action="extend")
        parser.add_argument("-f", "--files", type=str, nargs="+",
                            help="file(s) to watch", action="extend")
        parser.add_argument("-i", "--ignore", type=str, nargs="+",
                            help="file(s) or directory(ies) to ignore", action="extend")
        parser.add_argument("-s", "--sleep", type=float, default=0.2)
        parser.add_argument("--debug", action="store_true", help="set log level to DEBUG")

        args = parser.parse_args()

        config_log.init(args.debug)

        logging.info("Executing %s", args.cmds)
        if args.dirs:
            logging.info("Watching dirs %s", args.dirs)
        if args.files:
            logging.info("Watching files %s", args.files)
        if args.ignore:
            logging.info("Ignoring %s", args.ignore)

        if not args.files and not args.dirs:
            logging.critical("Either provide files or directories")

        files = normalize_paths(args.files, os.path.isfile)
        dirs = normalize_paths(args.dirs, os.path.isdir)
        ignore = create_regexes(args.ignore)
        execution_loop(args.cmds, files, dirs, ignore, args.sleep)
    except KeyboardInterrupt:
        logging.info("Ctrl+C pressed")


if __name__ == "__main__":
    main()
