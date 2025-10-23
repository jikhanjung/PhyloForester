"""
PhyloForester Logging Module

Provides centralized logging functionality for the application.
"""
import PfUtils as pu
import logging
import os
from datetime import datetime

# Ensure log directory exists
if not os.path.exists(pu.DEFAULT_LOG_DIRECTORY):
    os.makedirs(pu.DEFAULT_LOG_DIRECTORY)


def setup_logger(name, level=logging.INFO):
    """Setup application logger with file and console handlers

    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        logging.Logger: Configured logger instance
    """
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")

    logfile_path = os.path.join(pu.DEFAULT_LOG_DIRECTORY,
                                f'{pu.PROGRAM_NAME}.{date_str}.log')

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler - logs everything at specified level and above
    file_handler = logging.FileHandler(logfile_path, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    # Console handler - only warnings and above to avoid cluttering console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)

    # Configure logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers if logger already exists
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    # Prevent logs from propagating to root logger
    logger.propagate = False

    return logger


def get_logger(name):
    """Get existing logger or create new one

    Args:
        name: Logger name

    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)