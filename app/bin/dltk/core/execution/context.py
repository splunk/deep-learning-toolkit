__all__ = ["ExecutionContext"]


class ExecutionContext(object):
    is_preop = None
    is_searchpeer = None
    search_id = None
    model = None
    root_trace_context_string = None
    method = None
    message_logger = None
    fields = None
    params = None

    def __init__(
        self,
        is_preop,
        is_searchpeer,
        search_id,
        model,
        root_trace_context_string,
        method,
        message_logger,
        fields,
        params,
    ):
        self.is_preop = is_preop
        self.is_searchpeer = is_searchpeer
        self.search_id = search_id
        self.model = model
        self.root_trace_context_string = root_trace_context_string
        self.method = method
        self.message_logger = message_logger
        self.fields = fields
        self.params = params
