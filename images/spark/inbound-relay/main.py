import os
import logging
import threading
import time
import sys
import opentracing
from signalfx_tracing import create_tracer

from waitress import serve
from flask import Flask, request
import http

import hdfs


if __name__ == "__main__":

    logging.basicConfig(
        level=os.environ.get("LOGLEVEL", "INFO"),
        format='%(asctime)s %(levelname)-8s %(message)s',
    )

    tracer_config = {
        "sampler": {
            "type": "const",
            "param": 1,
        },
        "logging": False,
    }

    jaeger_endpoint = None
    signalfx_agent_host = os.getenv('SIGNALFX_AGENT_HOST')
    if signalfx_agent_host:
        jaeger_endpoint = 'http://' + signalfx_agent_host + ':9080/v1/trace'
        tracer_config["jaeger_endpoint"] = jaeger_endpoint
        logging.info("jaeger_endpoint: %s" % jaeger_endpoint)

    logging.info("tracer_config: %s" % tracer_config)
    tracer = create_tracer(
        config=tracer_config,
        service_name="spark-inbound-relay",
        validate=True,
    )

    hdfs_path = os.environ.get("HDFS_PATH", "")
    logging.info("hdfs_path: %s" % hdfs_path)

    hdfs_base_url = os.environ.get("HDFS_SINK_URL", "")
    logging.info("hdfs_base_url: %s" % hdfs_base_url)

    hdfs_client = hdfs.InsecureClient(hdfs_base_url)
    hdfs_client.delete(hdfs_path, recursive=True)
    hdfs_client.makedirs(hdfs_path)

    app = Flask(__name__)

    chunk_index_lock = threading.Lock()
    chunk_index = 0

    @app.route('/', methods=['POST', "GET"])
    def handle():
        if request.method == 'GET':
            return '', http.HTTPStatus.OK

        span_context = opentracing.tracer.extract(
            format=opentracing.propagation.Format.HTTP_HEADERS,
            carrier=dict(request.headers)
        )

        with opentracing.tracer.start_active_span(
            'handle_chunk',
            child_of=span_context,
            tags={
                opentracing.ext.tags.SPAN_KIND: opentracing.ext.tags.SPAN_KIND_RPC_SERVER,
            }
        ):

            global chunk_index
            data = request.data

            chunk_index_lock.acquire()
            _chunk_index = chunk_index
            chunk_index += 1
            chunk_index_lock.release()

            with opentracing.tracer.start_active_span(
                'send_to_hdfs',
                tags={
                    opentracing.ext.tags.SPAN_KIND: opentracing.ext.tags.SPAN_KIND_RPC_CLIENT,
                }
            ):

                logging.info("sending chunk %s (%s bytes) to hdfs ..." % (_chunk_index, len(data)))
                file_path = '%s/buffer_%s' % (hdfs_path, _chunk_index)
                with hdfs_client.write(file_path) as writer:
                    writer.write(data)

        return '', http.HTTPStatus.OK

    serve(
        app,
        host="0.0.0.0",
        port=8888,
        channel_timeout=100000,
        # threads=concurrent_algo_executions,
    )

    # def signal_handler(signum, frame):
    #    logging.info('received signal %s' % signum)
    #    sys.exit(0)
    # signal.signal(signal.SIGINT, signal_handler)
    # signal.signal(signal.SIGTERM, signal_handler)
    # signal.signal(signal.SIGKILL, signal_handler)
