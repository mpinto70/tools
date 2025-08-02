"""Shows the different log messages"""

import logging

import coloredlogs  # type: ignore

OK_LEVEL = 25


def ok(self, message, *args, **kwargs):
    if self.isEnabledFor(OK_LEVEL):
        self._log(OK_LEVEL, message, args, **kwargs)


def init(debug: bool):
    """Prepare log configuration

    Args:
        debug (bool): if the level should be debug
    """

    loglevel = "DEBUG" if debug else "INFO"

    dbg_cr = 34
    inf_cr = 39
    wrn_cr = 208
    err_cr = 196
    coloredlogs.DEFAULT_FIELD_STYLES["levelname"] = {"color": 14, "bold": False}
    coloredlogs.DEFAULT_FIELD_STYLES["asctime"] = {"color": 13, "bold": True}
    coloredlogs.DEFAULT_LEVEL_STYLES["debug"] = {"color": dbg_cr, "bold": False}
    coloredlogs.DEFAULT_LEVEL_STYLES["info"] = {"color": inf_cr, "bold": False}
    coloredlogs.DEFAULT_LEVEL_STYLES["ok"] = {"color": 10, "bold": True}
    coloredlogs.DEFAULT_LEVEL_STYLES["warning"] = {"color": wrn_cr, "bold": False}
    coloredlogs.DEFAULT_LEVEL_STYLES["error"] = {"color": err_cr, "bold": True}
    coloredlogs.DEFAULT_LEVEL_STYLES["critical"] = {"color": 226, "background": "red", "bold": True}
    coloredlogs.install(
        level=loglevel,
        fmt="%(asctime)s %(levelname)-5s | %(message)s (%(filename)s:%(lineno)d)",
    )

    logging.addLevelName(logging.WARNING, "WARN")
    logging.addLevelName(logging.CRITICAL, "FATAL")
    logging.addLevelName(OK_LEVEL, "OK")
    logging.Logger.ok = ok


if __name__ == "__main__":
    init(True)
    logging.debug("Debug message")
    logging.info("Info message")
    logging.warning("Warning message")
    logging.error("Error message")
    logging.critical("Critical message")
    logging.log(OK_LEVEL,"Success message")
