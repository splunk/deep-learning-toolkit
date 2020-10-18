import os
import importlib
splunk_rest = importlib.import_module("splunk.rest")
SplunkBaseRestHandler = getattr(splunk_rest, "BaseRestHandler")
from urllib.parse import parse_qs, unquote

import json
import splunklib.client as client

__all__ = ["BaseRestHandler"]

app_name = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))


class BaseRestHandler(SplunkBaseRestHandler):  # noqa
    _service = None

    # splunk client service object create
    def create_service(self):
        s = client.Service(
            #token=self.sessionKey,
            token=self.request["systemAuth"],
            sharing="app",
            app=app_name,
        )
        return s

    @property
    def service(self):
        return self.splunk

    @property
    def splunk(self):
        if self._service != None:
            return self._service
        self._service = self.create_service()
        return self._service

    # send result list as json response
    def send_entries(self, entries):
        if entries is None:
            entries = []
        if isinstance(entries, dict):
            entries = [entries]
        self.send_json_response({
            "entry": [{
                "content": e
            } for e in entries]
        })

    # send json response
    def send_json_response(self, object):
        self.response.setStatus(200)
        self.response.setHeader('content-type', 'application/json')
        self.response.write(json.dumps(object))

    _params = None

    def read_params(self):
        if self._params is None:
            self._params = {}
            payload = self.request["payload"] if "payload" in self.request else None
            if payload:
                payload = parse_qs(payload, keep_blank_values=True)
                for k, v in payload.items():
                    if len(v):
                        self._params[k] = v[0]
                    else:
                        self._params[k] = None
            query = self.request['query'] if "query" in self.request else None
            if query:
                for k, v in query.items():
                    self._params[k] = v

    @property
    def params(self):
        self.read_params()
        return self._params.items()

    def get_param(self, name, default=None):
        self.read_params()
        if name not in self._params:
            return default
        return self._params[name]

    def handle_request(self, method):
        results = method()
        self.send_entries(results)

    def handle_GET(self):
        self.handle_request(self.get)

    def get(self):
        pass

    def handle_PUT(self):
        self.handle_request(self.put)

    def put(self):
        pass

    def handle_POST(self):
        self.handle_request(self.post)

    def post(self):
        pass

    def handle_DELETE(self):
        self.handle_request(self.delete)

    def delete(self):
        pass
