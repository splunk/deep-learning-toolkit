from .brancher import *
from .logger import *
from .wrapper import *
from .handler import *


def wrap(extras={}, parent_logger=None):
    if parent_logger is None:
        parent_logger = get_logger()
    return WrappedLogger(parent_logger, extras)


def branch(a, b):
    return BranchLogger(a, b)


def log(self, level, message, *args, **kwargs):
    logger = get_logger()
    return logger.log(
        level,
        self.message_prefix + message,
        *args,
        **kwargs
    )


def debug(self, message, *args, **kwargs):
    logger = get_logger()
    return logger.debug(
        message,
        *args,
        **kwargs
    )


def info(self, message, *args, **kwargs):
    logger = get_logger()
    return logger.info(
        message,
        *args,
        **kwargs
    )


def warning(self, message, *args, **kwargs):
    logger = get_logger()
    return logger.warning(
        message,
        *args,
        **kwargs
    )


# Alias warn to warning
warn = warning


def error(self, message, *args, **kwargs):
    logger = get_logger()
    return logger.error(
        message,
        *args,
        **kwargs
    )


def critical(self, message, *args, **kwargs):
    logger = get_logger()
    return logger.critical(
        message,
        *args,
        **kwargs
    )
