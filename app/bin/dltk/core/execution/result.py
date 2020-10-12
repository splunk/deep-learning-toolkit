

__all__ = ["ExecutionResult"]


class ExecutionResult(object):
    events = None
    error = None
    final = None
    wait = None

    def __init__(
        self,
        events=[],
        error=None,
        final=True,
        wait=None,
    ):
        self.events = events
        self.error = error
        self.final = final
        self.wait = wait
