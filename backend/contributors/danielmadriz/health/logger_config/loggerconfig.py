import logging
import sys
from pathlib import Path
from typing import Optional

# Constants
DEFAULT_LOG_FILE = "logs/application.log"
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEVELOPMENT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:

    if format_string is None:
        format_string = DEFAULT_LOG_FORMAT
    
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=numeric_level,
        format=format_string,
        handlers=[]
    )
    
    root_logger = logging.getLogger()
    
    console_handler = _create_console_handler(numeric_level, format_string)
    root_logger.addHandler(console_handler)
    
    if log_file:
        file_handler = _create_file_handler(log_file, numeric_level, format_string)
        root_logger.addHandler(file_handler)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

# Standard configuration in case of wanting to put this in different environments
def setup_application_logging() -> logging.Logger:
    return setup_logging(
        level="INFO",
        format_string=DEFAULT_LOG_FORMAT
    )


def setup_development_logging() -> logging.Logger:
    return setup_logging(
        level="DEBUG",
        format_string=DEVELOPMENT_LOG_FORMAT
    )


def setup_production_logging(log_file: str = DEFAULT_LOG_FILE) -> logging.Logger:
    return setup_logging(
        level="WARNING",
        log_file=log_file,
        format_string=DEFAULT_LOG_FORMAT
    )


def _create_console_handler(level: int, format_string: str) -> logging.StreamHandler:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(format_string)
    console_handler.setFormatter(console_formatter)
    
    return console_handler


def _create_file_handler(log_file: str, level: int, format_string: str) -> logging.FileHandler:
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(format_string)
    file_handler.setFormatter(file_formatter)
    
    return file_handler