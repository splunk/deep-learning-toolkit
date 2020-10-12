from logging import Handler

__all__ = ["LoggingHandler"]


class LoggingHandler(Handler):
    _events = None
    _last_time = None

    def __init__(self):
        Handler.__init__(self)
        self._events = []

    def emit(self, record):
        raw_message = record.getMessage()
        if raw_message.startswith("Setting logger=splunk"):
            return
        if raw_message.startswith("Using default logging config file"):
            return
        msg = raw_message.replace('"', '\\"')
        time = round(record.created, 3)
        if self._last_time and time <= self._last_time:
            time = self._last_time + 0.001
        self._last_time = time
        self._events.append({
            "_raw": "%.3f, level=\"%s\", msg=\"%s\"" % (
                time,
                record.levelname,
                msg
            ),
        })

    @property
    def events(self):
        return self._events
