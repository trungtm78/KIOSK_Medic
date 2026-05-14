import logging
import sys
import os

LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")

def setup_logger(name: str = "CyberMedical Robot Service") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))

    # Tắt propagate để không đẩy log lên root logger nữa
    logger.propagate = False  

    # Tránh tạo nhiều handler nếu gọi nhiều lần
    if not logger.handlers:
        formatter = logging.Formatter(
            ":::[%(levelname)s] [%(asctime)s] | %(module)s.%(funcName)s:::\n%(message)s",
            datefmt="%Y-%b-%d %H:%M:%S"  # ví dụ: 2025-Sep-09 12:34:56
        )
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.flush = sys.stdout.flush

        logger.addHandler(console_handler)

    return logger

logger = setup_logger()
