from urllib.parse import parse_qs

from dltk.core.rest import BaseRestHandler
from . import connector_api

__all__ = [
    "ConnectorsHandler",
]


class ConnectorsHandler(BaseRestHandler):
    def handle_GET(self):
        results = []
        for environment in connector_api.get_all(self.splunk):
            result = {
                "name": environment.name,
            }
            results.append(result)
        self.send_entries(results)

    def handle_POST(self):
        params = parse_qs(self.request['payload'])
        if "name" not in params:
            raise Exception("missing name")
        connector_name = params["name"][0]
        connector_api.create(
            self.splunk,
            connector_name,
        )

    def handle_DELETE(self):
        query = self.request['query']
        connector_name = query.get("name", "")
        if not connector_name:
            raise Exception("missing name")
        connector_api.delete(self.splunk, connector_name)
