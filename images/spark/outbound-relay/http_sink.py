from waitress import serve
from flask import Flask, request
from queue import Empty
import logging
import threading
import http


class HTTPSink(object):

    def __init__(self, queue, status):
        self.queue = queue
        self.status = status
        self.total_bytes = 0
        self.chunk_count = 0
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()

    def run(self):
        logging.info("HTTPSink: starting ...")
        app = Flask(__name__)
        app.add_url_rule('/ping', view_func=self.ping_handler, methods=["GET"])
        app.add_url_rule('/pull', view_func=self.pull_handler, methods=["POST"])
        serve(
            app,
            host="0.0.0.0",
            port=8890,
            channel_timeout=100000,
            # threads=concurrent_algo_executions,
        )

    def ping_handler(self):
        return '', http.HTTPStatus.OK

    def pull_handler(self):
        try:
            chunk = self.queue.get_nowait()
        except Empty:
            msg = self.status.source_error_message
            if msg:
                logging.info("HTTPSink: informed Splunk that there is an error: %s" % msg)
                return msg, http.HTTPStatus.INTERNAL_SERVER_ERROR
            if self.status.source_sent_all_data:
                logging.info("HTTPSink: informed Splunk that there won't be more data")
                return '', http.HTTPStatus.GONE
            return '', http.HTTPStatus.NO_CONTENT

        chunk_size = len(chunk)
        self.lock.acquire()
        self.total_bytes += chunk_size
        #total_bytes = self.total_bytes
        self.chunk_count += 1
        chunk_count = self.chunk_count
        self.lock.release()

        logging.info("HTTPSink: will send chunk %s (%s bytes) to Splunk" % (
            chunk_count,
            chunk_size,
        ))

        self.queue.task_done()
        return chunk, 200
