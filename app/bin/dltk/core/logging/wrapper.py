import logging

__all__ = ["WrappedLogger"]


class WrappedLogger(object):
    logger = None

    def __init__(self, logger, extras):
        self.logger = logger
        self.message_prefix = ' '.join(["%s=\"%s\"" % (key, value) for key, value in extras.items()])
        if self.message_prefix:
            self.message_prefix = self.message_prefix + " "

    def log(self, level, message, *args, **kwargs):
        return self.logger.log(
            level,
            self.message_prefix + message,
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
