import datetime
import logging
import sys
import os

LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")


def setup_logger(name: str = "Chat Service") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))

    logger.propagate = False
    if not logger.handlers:
        formatter = logging.Formatter(
            ":::[%(levelname)s] [%(asctime)s] | %(module)s.%(funcName)s:::\n%(message)s\n",
            datefmt="%Y-%b-%d %H:%M:%S",
        )
        tz_vietnam = datetime.timezone(datetime.timedelta(hours=7))
        formatter.converter = lambda timestamp: datetime.datetime.fromtimestamp(
            timestamp, tz=tz_vietnam
        ).timetuple()
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.flush = sys.stdout.flush
        logger.addHandler(console_handler)
    return logger


logger = setup_logger()
