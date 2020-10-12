from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.listener import StreamingListener
import os
import logging
import time
import http
import json
import threading
import socket
import io
import traceback
import relay_status
import opentracing
from signalfx_tracing import create_tracer
from server import DriverServer
import output_relay


def send_stream(relay_url, stream):
    # https://spark.apache.org/docs/latest/streaming-programming-guide.html#design-patterns-for-using-foreachrdd
    def send_partition(iter):
        events = []
        for record in iter:
            events.append(record)
            if len(events) > 100000:
                #output_chunk(relay_url, events)
                events = []
        if len(events) > 0:
            #output_chunk(relay_url, events)
            pass

    def send_rdd(rdd):
        rdd.foreachPartition(send_partition)
    stream.foreachRDD(send_rdd)


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
        service_name="dltk-spark-driver",
        validate=True,
    )

    search_id = os.getenv("DLTK_SEARCH_ID", "")
    logging.info("DLTK_SEARCH_ID=%s" % search_id)

    algo_name = os.getenv("DLTK_ALGO", "DLTK")
    logging.info("DLTK_ALGO=%s" % algo_name)
    spark_context = SparkContext(appName=algo_name)
    spark_context.addPyFile(os.path.abspath(output_relay.__file__))

    fields = None
    fields_string = os.getenv("DLTK_FIELDS", "")
    logging.info("fields_string=%s" % fields_string)
    if fields_string:
        fields = fields_string.split(",")
    logging.info("fields=%s" % fields)

    server = DriverServer(tracer)

    outbound_relay_hostname = os.getenv("DLTK_OUTBOUND_RELAY")

    try:

        algo_method_name = os.getenv("DLTK_ALGO_METHOD")
        logging.info("DLTK_ALGO_METHOD=%s" % algo_method_name)
        algo_code = __import__("algo_code")
        method_impl = getattr(algo_code, algo_method_name)

        logging.info("waiting for input completed signal ...")
        server.wait_for_input_completed_signal()

        trace_context = opentracing.tracer.extract(
            format=opentracing.propagation.Format.TEXT_MAP,
            carrier=server.trace_context_dict
        )

        with opentracing.tracer.start_active_span(
            'execution-spark-job',
            child_of=trace_context,
            tags={
                opentracing.ext.tags.SPAN_KIND: opentracing.ext.tags.SPAN_KIND_CONSUMER,
            }
        ):
            hdfs_url_base = os.getenv("DLTK_HDFS_URL", "")
            hdfs_path = os.getenv("DLTK_HDFS_PATH", "")
            hdfs_url = "%s/%s" % (hdfs_url_base.strip("/"), hdfs_path.strip("/"))
            logging.info("hdfs_url: %s" % hdfs_url)
            csv_strings = spark_context.textFile(hdfs_url)
            objects = csv_strings.map(lambda s: {f: v.strip('"') for f, v in zip(fields, s.split(","))})

            with opentracing.tracer.start_active_span('execute-algorithm'):
                output = method_impl(spark_context, objects)

            with opentracing.tracer.start_active_span('wait-for-to-output-relay'):
                relay_status.wait_until_running(outbound_relay_hostname)

            with opentracing.tracer.start_active_span('send-to-output-relay'):
                logging.info("sending output (type=%s) to relay..." % (type(output)))
                from pyspark.rdd import RDD
                if isinstance(output, RDD):
                    output_rdd = output
                    output_relay.send_rdd_to_relay(outbound_relay_hostname, output_rdd)
                else:
                    output_list = output
                    logging.info("algo returned %s events" % len(output_list))
                    output_relay.send_chunks_to_relay(outbound_relay_hostname, [json.dumps(output_list).encode()])
                logging.info("sent output to relay")

            server.signal_output_completed()

    except Exception as e:
        full_exception = traceback.format_exc()
        logging.error("unexpected error: %s" % (full_exception))
        error_message = '%s: %s' % (e, full_exception)
        server.signal_final_error(error_message)

    if server.trace_context:
        server.trace_context.finish()
    if hasattr(tracer, "close"):
        tracer.close()

    server.wait_for_stop_signal()
    logging.info("stopping ...")
    time.sleep(2)
    spark_context.stop()
    logging.info("stopped")

    # elif input_mode == "streaming":
    #    batch_interval = int(os.getenv("DLTK_BATCH_INTERVAL", 1))
    #    logging.info("DLTK_BATCH_INTERVAL=%s" % batch_interval)
    #    receiver_count = int(os.getenv("DLTK_RECEIVER_COUNT", 2))
    #    logging.info("DLTK_RECEIVER_COUNT=%s" % receiver_count)
    #    wait_time_before_stop = int(os.getenv("DLTK_WAIT_TIME_BEFORE_STOP", 30))
    #    logging.info("DLTK_WAIT_TIME_BEFORE_STOP=%s" % wait_time_before_stop)
    #    checkpoint_url = os.getenv("DLTK_CHECKPOINT_URL", "")
    #    logging.info("DLTK_CHECKPOINT_URL=%s" % checkpoint_url)
    #    # https://spark.apache.org/docs/latest/streaming-programming-guide.html
    #    # https://spark.apache.org/docs/latest/api/python/pyspark.streaming.html#pyspark.streaming.StreamingContext
    #    streaming_context = StreamingContext(spark_context, batch_interval)
    #    if checkpoint_url:
    #        streaming_context.checkpoint(checkpoint_url)
    #    input_streams = []
    #    for i in range(receiver_count):
    #        logging.info("create new receiver")
    #        s = streaming_context.socketTextStream(inbound_relay_sink, 81)
    #        input_streams.append(s)
    #    input_stream = streaming_context.union(*input_streams)
    #    event_stream = input_stream.map(lambda line: json.loads(line))
    #    output_stream = method_impl(streaming_context, event_stream)
    #    send_stream(outbound_relay_source_url, output_stream)
    #    wait_for_relay_to_complete_startup(inbound_relay_sink_url)
    #    wait_for_relay_to_complete_startup(outbound_relay_source_url)
    #    streaming_context.start()##
    #    def wait_until_all_events_received():
    #        wait_for_relay_status(inbound_relay_sink_url, "done")
    #    def background_poller():
    #        wait_until_all_events_received()
    #        logging.info("waiting to finish up...")
    #        time.sleep(wait_time_before_stop)
    #        logging.info("stopping context...")
    #        streaming_context.stop(stopSparkContext=False, stopGraceFully=True)
    #    # background_poller_thread = threading.Thread(target=background_poller, args=())
    #    # background_poller_thread.daemon = True
    #    # background_poller_thread.start()
    #    # streaming_context.awaitTermination()
    #    wait_until_all_events_received()
    #    logging.info("waiting to finish up...")
    #    time.sleep(wait_time_before_stop)
    #    logging.info("stopping context...")
    #    streaming_context.stop(stopSparkContext=True, stopGraceFully=True)
    #    close_output(outbound_relay_source_url)
    # else:
    #    logging.error("unsupported processing mode")
