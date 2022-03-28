"""Shows the different log messages"""

import logging

import coloredlogs  # type: ignore


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
    fat_cr = 196
    coloredlogs.DEFAULT_FIELD_STYLES["levelname"] = {"color": 14, "bold": False}
    coloredlogs.DEFAULT_FIELD_STYLES["asctime"] = {"color": 13, "bold": True}
    coloredlogs.DEFAULT_LEVEL_STYLES["debug"] = {"color": dbg_cr, "bold": False}
    coloredlogs.DEFAULT_LEVEL_STYLES["info"] = {"color": inf_cr, "bold": False}
    coloredlogs.DEFAULT_LEVEL_STYLES["warning"] = {"color": wrn_cr, "bold": False}
    coloredlogs.DEFAULT_LEVEL_STYLES["error"] = {"color": err_cr, "bold": False}
    coloredlogs.DEFAULT_LEVEL_STYLES["critical"] = {"color": fat_cr, "bold": True}
    coloredlogs.install(
        level=loglevel, fmt="%(asctime)s %(levelname)-5s | %(message)s (%(filename)s:%(lineno)d)")

    logging.addLevelName(logging.WARNING, "WARN")
    logging.addLevelName(logging.CRITICAL, "FATAL")


if __name__ == "__main__":
    init(True)
    logging.debug("Debug message")
    logging.info("Info message")
    logging.warning("Warning message")
    logging.error("Error message")
    logging.critical("Critical message")
