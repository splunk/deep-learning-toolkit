import os
import logging
import threading
import time
from queue import Queue

from status_server import StatusServer
from tcp_source import TCPSource
from http_sink import HTTPSink

if __name__ == "__main__":
    logging.basicConfig(
        level=os.environ.get("LOGLEVEL", "INFO"),
        format='%(asctime)s %(levelname)-8s %(message)s',
    )

    queue = Queue()

    status_server = StatusServer()
    source = TCPSource(queue)
    sink = HTTPSink(queue, status_server)

    logging.info("Main: waiting until all data is received from Spark...")
    status_server.wait_for_source_sent_all_data()
    logging.info("Main: waiting until all data is sent to Splunk...")
    queue.join()
    logging.info("Main: mark sink as done")
    status_server.mark_sink_received_all_data()

    while True:
        time.sleep(30)
