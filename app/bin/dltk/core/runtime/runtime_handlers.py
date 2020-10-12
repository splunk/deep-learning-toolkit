import os
from urllib.parse import parse_qs, unquote
from dltk.core.rest import BaseRestHandler
from . import runtime_api

__all__ = [
    "RuntimesHandler",
]


class RuntimesHandler(BaseRestHandler):
    def handle_GET(self):
        results = []
        for runtime in runtime_api.get_all(self.splunk):
            result = {
                "name": runtime.name,
                "connector": runtime.connector_name,
            }
            results.append(result)
        self.send_entries(results)

    def handle_POST(self):
        runtime_name = self.get_param("name")
        if not runtime_name:
            raise Exception("name missing")
        connector_name = self.get_param("connector")
        if not connector_name:
            raise Exception("connector missing")
        r = runtime_api.create(
            self.splunk,
            runtime_name,
            connector_name
        )
        algorithm_params = self.get_param("algorithm_params")
        if algorithm_params:
            r.set_algorithm_param_names = algorithm_params

    def handle_DELETE(self):
        query = self.request['query']
        runtime_name = query.get("name", "")
        if not runtime_name:
            raise Exception("missing name")
        runtime_api.delete(self.splunk, runtime_name)
