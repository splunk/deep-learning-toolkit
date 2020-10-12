import urllib

from dltk.core.rest import BaseRestHandler

from .api import *

__all__ = ["ModelsHandler"]


class ModelsHandler(BaseRestHandler):
    def handle_GET(self):
        results = []
        request_query = self.request['query']
        environment_name = request_query.get("environment", "")
        algorithm_name = request_query.get("algorithm", "")
        for model in get_all(self.splunk):
            if algorithm_name and model.algorithm_name != algorithm_name:
                continue
            if environment_name and model.environment_name != environment_name:
                continue
            result = {
                "name": model.name,
                "algorithm": model.algorithm_name,
                "environment": model.environment_name,
            }
            results.append(result)
        self.send_entries(results)

    def handle_POST(self):
        payload = urllib.parse.parse_qs(self.request['payload'])
        environment_name = payload["environment"][0]
        algorithm_name = payload["algorithm"][0]
        model_name = payload["name"][0]
        create(self.splunk, model_name, algorithm_name, environment_name)
