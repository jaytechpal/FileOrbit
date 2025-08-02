"""
Logging utilities for FileOrbit application
"""

import logging
import sys
import os
from pathlib import Path
from typing import Optional


def setup_logger(name: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """Setup application logger with file and console handlers"""
    
    # Create logs directory - platform appropriate
    if os.name == 'nt':  # Windows
        log_dir = Path(os.environ.get('APPDATA', '')) / "FileOrbit" / "logs"
    else:  # macOS/Linux
        log_dir = Path.home() / ".config" / "fileorbit" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger_name = name or "fileorbit"
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # File handler
    log_file = log_dir / "fileorbit.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(f"fileorbit.{name}")


class LogFilter:
    """Custom log filter for specific modules"""
    
    def __init__(self, allowed_modules: list):
        self.allowed_modules = allowed_modules
    
    def filter(self, record):
        return any(module in record.name for module in self.allowed_modules)
