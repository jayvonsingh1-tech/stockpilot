"""
Logging utilities for StockPilot
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logger(name: str = "stockpilot", level: str = "INFO", 
                 log_file: str = "logs/stockpilot.log",
                 max_bytes: int = 100 * 1024 * 1024,  # 100MB
                 backup_count: int = 5) -> logging.Logger:
    """
    Set up logger with console and file handlers
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    return logger


def log_trade_signal(logger: logging.Logger, signal: dict):
    """Log a trade signal with all details"""
    logger.info(f"SIGNAL GENERATED: {signal.get('action')} {signal.get('ticker')}")
    logger.info(f"  Confidence: {signal.get('confidence')}%")
    logger.info(f"  Entry: {signal.get('entry_price')}")
    logger.info(f"  Stop Loss: {signal.get('stop_loss')}")
    logger.info(f"  Take Profit: {signal.get('take_profit')}")
    logger.info(f"  Strategy: {signal.get('strategy')}")
    logger.info(f"  Reasoning: {signal.get('reasoning')}")


def log_error(logger: logging.Logger, error: Exception, context: str = ""):
    """Log an error with context"""
    logger.error(f"ERROR in {context}: {type(error).__name__}: {str(error)}", exc_info=True)


def log_performance(logger: logging.Logger, metrics: dict):
    """Log performance metrics"""
    logger.info("=" * 50)
    logger.info("PERFORMANCE METRICS")
    logger.info("=" * 50)
    for key, value in metrics.items():
        logger.info(f"  {key}: {value}")
    logger.info("=" * 50)
