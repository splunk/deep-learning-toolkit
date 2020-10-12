from dltk.core.rest import BaseRestHandler
from . import algorithm_api
from . import method_api
from urllib.parse import parse_qs

__all__ = ["AlgorithmMethodsHandler"]


class AlgorithmMethodsHandler(BaseRestHandler):
    def handle_GET(self):
        query = self.request['query']
        algorithm_name = query.get("algorithm", "")
        if not algorithm_name:
            raise Exception("missing algorithm name")
        a = algorithm_api.get(self.splunk, algorithm_name)
        results = []
        for m in method_api.get_all(self.splunk, a):
            results.append({
                "name": m.name,
                "command_type": m.command_type,
                "max_buffer_size": m.max_buffer_size,
            })
        self.send_entries(results)

    def handle_POST(self):
        params = parse_qs(self.request['payload'])
        if "algorithm" not in params:
            raise Exception("missing algorithm")
        algorithm_name = params["algorithm"][0]
        if "name" not in params:
            raise Exception("missing name")
        method_name = params["name"][0]
        a = algorithm_api.get(self.splunk, algorithm_name)
        method_api.create(self.splunk, algorithm_name, method_name)

    def handle_DELETE(self):
        query = self.request['query']
        algorithm_name = query.get("algorithm", "")
        if not algorithm_name:
            raise Exception("missing algorithm name")
        method_name = query.get("name", "")
        if not method_name:
            raise Exception("missing name")
        method_api.delete(self.splunk, algorithm_name, method_name)
