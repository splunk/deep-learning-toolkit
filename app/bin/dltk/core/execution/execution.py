
__all__ = ["Execution"]


class Execution(object):
    context = None
    deployment = None
    _logger = None

    def __init__(
        self,
        deployment,
        context,
    ):
        self.deployment = deployment
        self.context = context

    @property
    def logger(self):
        if self._logger is None:
            extras = {
                "search_id": self.context.search_id,
                "model": self.context.model,
                "is_preop": self.context.is_preop,
                "is_searchpeer": self.context.is_preop,
                "method": self.context.method.name,
            }
            if self.context.model:
                extras["model"] = self.context.model
            if self.context.model:
                extras["method"] = self.context.method
            import logging as system_logging
            from dltk.core import logging as dltk_logging
            dltk_logger = dltk_logging.wrap(extras, self.deployment.logger)
            self._logger = dltk_logging.BranchLogger(system_logging, dltk_logger)
        return self._logger

    def setup(self):
        pass

    def handle(self, buffer, buffer_size, finished):
        pass

    def finalize(self):
        pass

    def get_param(self, name):
        return self.deployment.get_param(name)
