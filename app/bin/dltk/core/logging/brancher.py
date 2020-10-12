import logging

__all__ = ["BranchLogger"]


class BranchLogger(object):
    logger_a = None
    logger_b = None

    def __init__(self, logger_a, logger_b):
        self.logger_a = logger_a
        self.logger_b = logger_b

    def log(self, level, message, *args, **kwargs):
        self.logger_a.log(
            level,
            message,
            *args,
            **kwargs
        )
        return self.logger_b.log(
            level,
            message,
            *args,
            **kwargs
        )

    def debug(self, message, *args, **kwargs):
        return self.log(logging.DEBUG, message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        return self.log(logging.INFO, message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        return self.log(logging.WARNING, message, *args, **kwargs)

    # Alias warn to warning
    warn = warning

    def error(self, message, *args, **kwargs):
        return self.log(logging.ERROR, message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        return self.log(logging.CRITICAL, message, *args, **kwargs)
