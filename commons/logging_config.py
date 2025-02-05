import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


class LogConfig:
    """Configuration class for setting up logging with separate console and file handlers."""

    DEFAULT_FORMAT = {
        "file": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        "console": "%(asctime)s - %(levelname)s - %(message)s",
    }

    def __init__(
        self,
        log_file: str = "app.log",
        file_level: int = logging.INFO,
        console_level: int = logging.INFO,
        max_file_size: int = 2 * 1024 * 1024,  # 2 MB
        backup_count: int = 1,
    ):
        """
        Initialize logging configuration.

        Args:
            log_file: Name of the log file
            file_level: Logging level for file output
            console_level: Logging level for console output
            max_file_size: Maximum size of each log file in bytes
            backup_count: Number of backup files to keep
        """
        self.log_file = log_file
        self.file_level = file_level
        self.console_level = console_level
        self.max_file_size = max_file_size
        self.backup_count = backup_count

        # Ensure log directory exists
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)

    def _create_file_handler(self) -> RotatingFileHandler:
        """Create and configure the file handler."""
        handler = RotatingFileHandler(
            self.log_dir / self.log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
        )
        handler.setFormatter(logging.Formatter(self.DEFAULT_FORMAT["file"]))
        handler.setLevel(self.file_level)
        return handler

    def _create_console_handler(self) -> logging.StreamHandler:
        """Create and configure the console handler."""
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(self.DEFAULT_FORMAT["console"]))
        handler.setLevel(self.console_level)
        return handler

    def setup(self):
        """Set up the logging configuration."""
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(min(self.file_level, self.console_level))

        # Remove existing handlers
        root_logger.handlers = []

        # Add handlers
        root_logger.addHandler(self._create_console_handler())
        root_logger.addHandler(self._create_file_handler())

        # Log initialization
        logging.info("Logging system initialized")


def setup_logging(**kwargs):
    """
    Convenience function to set up logging configuration.

    Example usage:
        setup_logging(
            console_level=logging.INFO,
            file_level=logging.DEBUG
        )
    """
    config = LogConfig(**kwargs)
    config.setup()