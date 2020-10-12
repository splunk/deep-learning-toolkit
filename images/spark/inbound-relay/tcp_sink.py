import logging
import threading
import socketserver
import hdfs
import traceback


class TCPSink(object):

    def __init__(self, queue):
        self.queue = queue
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()

    def run(self):
        queue = self.queue

        class TCPSinkHandler(socketserver.StreamRequestHandler):
            def handle(self):
                logging.info("TCPSink: Spark connected")
                try:
                    while True:
                        logging.info("TCPSink: waiting for chunk in queue ...")
                        data = queue.get()
                        if data is None:
                            logging.info("TCPSink: done")
                            queue.task_done()
                            break
                        chunk_size = len(data)
                        logging.info("TCPSink: sending chunk of %s bytes to Spark ..." % chunk_size)
                        self.wfile.write(("%s\n" % chunk_size).encode())
                        self.wfile.write(data)
                        self.wfile.flush()
                        queue.task_done()
                except:
                    err_msg = traceback.format_exc()
                    logging.error("TCPSink: error sending data:\n%s" % err_msg)
                finally:
                    logging.info("TCPSink: Spark disconnected")

        with socketserver.TCPServer(('0.0.0.0', 8890), TCPSinkHandler) as server:
            server.serve_forever()
