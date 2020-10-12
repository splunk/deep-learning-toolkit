import logging
import logging.handlers
import importlib

__all__ = ["get_handler"]

file_handler = None


def get_handler():
    global file_handler

    if not file_handler:
        name = "dltk"
        maxBytes = 25000000
        backupCount = 5
        util = importlib.import_module("splunk.appserver.mrsparkle.lib.util")
        logfile = util.make_splunkhome_path(["var", "log", "splunk", name + '.log'])
        file_handler = logging.handlers.RotatingFileHandler(
            logfile,
            mode='a',
            maxBytes=maxBytes,
            backupCount=backupCount
        )
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(message)s",
            datefmt="%m/%d/%Y %I:%M:%S %p %Z",
        )
        file_handler.setFormatter(formatter)

    return file_handler
