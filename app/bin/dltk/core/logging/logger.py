import os
import logging
import importlib

from . handler import get_handler

#splunk = importlib.import_module("splunk")

__all__ = ["get_logger", "configure_logger"]


logger = None


def get_logger():
    global logger

    if logger is None:
        logger = logging.getLogger("dltk")
        logger.propagate = False  # Prevent the log messages from being duplicated in the python.log file
        configure_logger(logger)
        logger.addHandler(get_handler())

    return logger


def configure_logger(logger):
    SPLUNK_HOME = os.environ['SPLUNK_HOME']
    LOGGING_DEFAULT_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log.cfg')
    LOGGING_LOCAL_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log-local.cfg')
    LOGGING_STANZA_NAME = 'python'
    #splunk.setupSplunkLogger(logger, LOGGING_DEFAULT_CONFIG_FILE, LOGGING_LOCAL_CONFIG_FILE, LOGGING_STANZA_NAME)
    logger.setLevel("DEBUG")
    #logger.level = "INFO"
