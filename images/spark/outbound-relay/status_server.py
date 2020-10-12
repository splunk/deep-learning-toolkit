from waitress import serve
from flask import Flask, request
import threading
import http


class StatusServer(object):

    def __init__(self):
        self.source_done = threading.Event()
        self.source_error_event = threading.Event()
        self._source_error_message = None
        self.sink_done = threading.Event()
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()

    def run(self):
        app = Flask(__name__)
        app.add_url_rule('/', view_func=self.get_handler, methods=["GET"])
        app.add_url_rule('/source_done', view_func=self.source_done_handler, methods=["PUT"])
        app.add_url_rule('/source_error', view_func=self.source_error_handler, methods=["PUT"])
        serve(
            app,
            host="0.0.0.0",
            port=8889,
            threads=1,
        )

    def get_handler(self):
        if self.source_error_event.is_set():
            return 'error', http.HTTPStatus.OK
        if not self.source_done.is_set():
            return 'receiving', http.HTTPStatus.OK
        if not self.sink_done.is_set():
            return 'sending', http.HTTPStatus.OK
        return 'done', http.HTTPStatus.OK

    def source_error_handler(self):
        self.source_error_event.set()
        self._source_error_message = request.data.decode()
        return '', http.HTTPStatus.OK

    def source_done_handler(self):
        self.source_done.set()
        return '', http.HTTPStatus.OK

    @property
    def source_error_message(self):
        if not self.source_error_event.is_set():
            return None
        return self._source_error_message

    @property
    def source_sent_all_data(self):
        return self.source_done.is_set()

    def wait_for_source_sent_all_data(self):
        self.source_done.wait()

    @property
    def sink_received_all_data(self):
        return self.sink_done.is_set()

    def mark_sink_received_all_data(self):
        self.sink_done.set()
