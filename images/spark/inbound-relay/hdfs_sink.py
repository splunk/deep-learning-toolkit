from waitress import serve
from flask import Flask, jsonify, request
import os
import logging
import threading
import time
from queue import Empty
import http
import hdfs
import threading


class HDFSSink(object):

    def __init__(self, queue, hdfs_base_url, path):
        self.queue = queue
        self.client = hdfs.InsecureClient(hdfs_base_url)
        self.base_path = path
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()

    def run(self):
        buffer_index = 0
        self.client.delete(self.base_path, recursive=True)
        self.client.makedirs(self.base_path)
        while True:
            data = self.queue.get()
            if data is None:
                logging.info("stopping hdfs sink")
                self.queue.task_done()
                return
            logging.info("sending chunk %s (%s bytes) to hdfs ..." % (buffer_index, len(data)))
            file_path = '%s/buffer_%s' % (self.base_path, buffer_index)
            with self.client.write(file_path) as writer:
                writer.write(data)
            buffer_index += 1
            self.queue.task_done()
        logging.info("buffer_count=%s" % buffer_index)
