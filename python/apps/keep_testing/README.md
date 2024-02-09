# Keep testing

`keep_testing` is a directory monitoring tool to allow repeated execution of commands when something
changes in a directory tree or when the user presses `ENTER`.

## How to run

This script reapetedly runs the commands passed (`-c`) whenever the directories (`-d`) or files
(`-f`) change, **or** when the user presses `ENTER`.

The commands are executed sequentially and, if any of the commands fails, the next commands are not
executed and the script goes back to watch directory/file changes or `ENTER` presses. This way, if
you prepare a set of commands to compile + run tests + static check, if compilation fails, neither
of the other two will be executed.

You can see the options running help (`-h`):

```sh
$ PYTHONPATH=python python3 python/apps/keep_testing -h
usage: keep_testing [-h] [-c CMDS [CMDS ...]] [-d DIRS [DIRS ...]] [-f FILES [FILES ...]] [-i IGNORES [IGNORES ...]] [-s SLEEP] [--config CONFIG] [--debug]

Keep runing a command based on changes in a tree

options:
  -h, --help            show this help message and exit
  -c CMDS [CMDS ...], --cmds CMDS [CMDS ...]
                        command(s) to execute
  -d DIRS [DIRS ...], --dirs DIRS [DIRS ...]
                        directory(ies) to watch
  -f FILES [FILES ...], --files FILES [FILES ...]
                        file(s) to watch
  -i IGNORES [IGNORES ...], --ignores IGNORES [IGNORES ...]
                        files or directories to ignore (regexes)
  -s SLEEP, --sleep SLEEP
  --config CONFIG       TOML config file that has cmds, dirs, files and ignores
  --debug               set log level to DEBUG
```

To run unit tests in this project while you make changes, you can run the following command:

```sh
keep-testing -c "PYTHONPATH=python python python/tests" -d python -i ".*__pycache__.*"
```

Then, every time you change/craete/delete a file or directory (that is not ignored), the tests will
run automatically.

## Options

| short | long        | description                                                                                                       |
| ----- | ----------- | ----------------------------------------------------------------------------------------------------------------- |
| `-c`  | `--cmds`    | one or more commands to be executed. Commands will be executed in the order they are entered in the command line  |
| `-d`  | `--dirs`    | one or more directories to watch                                                                                  |
| `-f`  | `--files`   | one or more files to watch (even if ignores match, they will be watched)                                          |
| `-i`  | `--ignores` | one or more regex to match against files and directories to be ignored (e.g. ".*\\\\.o" will ignore object files) |
| `-s`  | `--sleep`   | sleep time after a check of changed dirs/files or `ENTER` (default is 0.2s)                                       |
|       | `--config`  | a config file in format TOML with values for `cmds`, `dirs`, `files`, `ignores`                                   |
|       | `--degub`   | if debug logging should be enabled (note that this is very verbose, because it logs messages from `inotify`)      |

### Example TOML file

Below is an example TOML configuration file:

```toml
cmds = ["PYTHONPATH=python python python/tests" ]
dirs = ["python"]
ignores = [".*__pycache__.*"]

```
