# app/core/logging.py
import logging

def configure_logging():
    """
    Global logging configuration.
    Defines format and log level.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )