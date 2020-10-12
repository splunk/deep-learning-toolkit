from waitress import serve
from flask import Flask, request, jsonify
import logging
import threading
import http
import base64
import json
import opentracing


class DriverServer(object):

    trace_context = None
    trace_context_dict = None

    final_error = None
    output_completed = False

    def __init__(self, tracer):
        self.tracer = tracer

        self.input_completed = threading.Event()
        self.final_event = threading.Event()
        self.stop_event = threading.Event()

        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()

    def wait_for_input_completed_signal(self):
        self.input_completed.wait()

    def signal_output_completed(self):
        if self.final_event.is_set():
            logging.warning("signal_output_completed: final_event already set")
            return
        self.output_completed = True
        self.final_event.set()

    def signal_final_error(self, error_message):
        if self.final_event.is_set():
            logging.warning("signal_final_error: final_event already set")
            return
        self.final_error = '%s' % error_message
        self.final_event.set()

    def run(self):
        app = Flask(__name__)
        app.add_url_rule('/start', view_func=self.start_handler, methods=["PUT"])
        app.add_url_rule('/status', view_func=self.status_handler, methods=["GET"])
        app.add_url_rule('/stop', view_func=self.stop_handler, methods=["PUT"])
        serve(
            app,
            host="0.0.0.0",
            port=8888,
            channel_timeout=100000,
            threads=3,
        )

    def start_handler(self):
        logging.info("received start signal")
        span_context = self.tracer.extract(
            format=opentracing.propagation.Format.HTTP_HEADERS,
            carrier=dict(request.headers)
        )
        with self.tracer.start_active_span(
            'start_handler',
            child_of=span_context,
            tags={
                opentracing.ext.tags.SPAN_KIND: opentracing.ext.tags.SPAN_KIND_RPC_SERVER,
            }
        ):
            trace_context_string = request.headers['X-DLTK-RootContext']
            if trace_context_string:
                trace_context_bytes = trace_context_string.encode()
                trace_context_bytes = base64.b64decode(trace_context_bytes)
                trace_context_dict = json.loads(trace_context_bytes)
                trace_context = opentracing.tracer.extract(
                    format=opentracing.propagation.Format.TEXT_MAP,
                    carrier=trace_context_dict
                )
            with self.tracer.start_active_span(
                'signal_start',
                tags={
                    opentracing.ext.tags.SPAN_KIND: opentracing.ext.tags.SPAN_KIND_PRODUCER,
                }
            ) as scope:
                self.trace_context_dict = {}
                opentracing.tracer.inject(
                    span_context=scope.span,
                    format=opentracing.propagation.Format.TEXT_MAP,
                    carrier=self.trace_context_dict
                )
                # self.trace_context
                self.input_completed.set()
            return '', http.HTTPStatus.OK

    def status_handler(self):
        span_context = self.tracer.extract(
            format=opentracing.propagation.Format.HTTP_HEADERS,
            carrier=dict(request.headers)
        )
        with self.tracer.start_active_span(
            'status_handler',
            child_of=span_context,
            tags={
                opentracing.ext.tags.SPAN_KIND: opentracing.ext.tags.SPAN_KIND_RPC_SERVER,
            }
        ):
            if self.final_event.is_set():
                if self.output_completed:
                    logging.info("reporting status to Splunk: %s" % "completed")
                    return jsonify({
                        "status": "completed",
                    })
                if self.final_error:
                    logging.info("reporting status to Splunk: %s" % "error")
                    return jsonify({
                        "status": "error",
                        "error": self.final_error,
                    })
                logging.info("reporting status to Splunk: %s" % "error")
                return jsonify({
                    "status": "error",
                    "error": "unknown",
                })
            logging.info("reporting status to Splunk: %s" % "running")
            return jsonify({
                "status": "running",
            })

    def stop_handler(self):
        logging.info("received stop signal")
        span_context = self.tracer.extract(
            format=opentracing.propagation.Format.HTTP_HEADERS,
            carrier=dict(request.headers)
        )
        with self.tracer.start_active_span(
            'stop_handler',
            child_of=span_context,
            tags={
                opentracing.ext.tags.SPAN_KIND: opentracing.ext.tags.SPAN_KIND_RPC_SERVER,
            }
        ):
            self.stop_event.set()
            return '', http.HTTPStatus.OK

    def wait_for_stop_signal(self):
        logging.info("wait_for_stop_signal...")
        self.stop_event.wait()
