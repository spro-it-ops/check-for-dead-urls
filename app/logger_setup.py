import os
import logging

class LoggerSetup:
    """Handles logging configuration."""
    @staticmethod
    def setup(config):
        os.makedirs(config.log_dir, exist_ok=True)

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        # Clear existing handlers
        if logger.hasHandlers():
            logger.handlers.clear()

        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

        # File Handler: DEBUG level (includes individual checks)
        file_handler = logging.FileHandler(config.log_file, mode='a')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console Handler: INFO level (summary/errors only)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Silence noisy libraries
        logging.getLogger("urllib3").setLevel(logging.WARNING)