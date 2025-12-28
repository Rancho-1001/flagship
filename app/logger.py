"""
Logging configuration for FlagShip.
Provides structured logging with appropriate log levels.
"""
import logging
import sys
from typing import Optional
from app.config import settings


def setup_logging(log_level: Optional[str] = None) -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                  If None, uses INFO for development, WARNING for production
    
    Returns:
        Configured logger instance
    """
    if log_level is None:
        log_level = "INFO" if settings.ENVIRONMENT == "development" else "WARNING"
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # Prevent duplicate logs
    root_logger.propagate = False
    
    # Get application logger
    logger = logging.getLogger("flagship")
    logger.setLevel(log_level)
    
    return logger


# Initialize logger
logger = setup_logging()

