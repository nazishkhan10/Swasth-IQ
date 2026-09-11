import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Ensure logs directory exists
LOGS_DIR = Path(__file__).resolve().parent
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger instance.
    Usage:
        from app.logs.logger import get_logger
        logger = get_logger(__name__)
        logger.info("User logged in successfully")
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Console Handler (always active)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    logger.addHandler(console_handler)

    # File Handler - Rotating (max 5MB, keep 3 backups)
    log_file = LOGS_DIR / "app.log"
    try:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not set up file logging: {e}")

    # Prevent log propagation to root logger
    logger.propagate = False
    return logger


# Convenience app-level logger
app_logger = get_logger("medical_report_analyzer")
logger = app_logger

