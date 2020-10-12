import time
import logging
from splunklib.searchcommands import GeneratingCommand, Configuration, Option, validators
import traceback
import json
import re

from . import exceptions
from .logging import LoggingHandler
from dltk.core import get_method
from dltk.core.logging import get_handler, configure_logger, get_logger


@Configuration(type='reporting')
class JobCommand(GeneratingCommand):
    handler = Option(require=True)
    search_name = Option(require=False)
    argv = Option(require=False)
    repeat_on_error = Option(default=True, validate=validators.Boolean())
    repeat_on_success = Option(default=True, validate=validators.Boolean())

    def generate(self):
        logging_handler = LoggingHandler()
        logger = get_logger()
        #root_logger = logging.getLogger()
        #configure_logger(root_logger)
        logger.addHandler(logging_handler)
        #root_logger.addHandler(get_handler())

        logger.debug("running ...")
        try:
            func = get_method(self.handler)
            if self.argv:
                try:
                    argv = json.loads(self.argv)
                except json.JSONDecodeError as e:
                    err_msg = traceback.format_exc()
                    logger.error("unable to decode argv: %s" % err_msg)
                    #raise Stop()
                    argv = []
            else:
                argv = []
            func(self.service, *argv)
            logger.debug("done")
            if self.repeat_on_success:
                return
        except exceptions.Repeat:
            logger.debug("will repeat")
            return
        except exceptions.Stop:
            logger.debug("will stop and not repeat")
        except Exception as e:
            err_msg = traceback.format_exc()
            #err_msg = "..............."
            logger.error("exception during job execution: %s" % err_msg)
            if self.repeat_on_error:
                logger.debug("will repeat")
                return
        finally:
            logging.shutdown()
            for e in logging_handler.events:
                yield e

        if self.search_name:
            self.service.saved_searches.delete(self.search_name)
        else:
            logger.error("missing search_name")
