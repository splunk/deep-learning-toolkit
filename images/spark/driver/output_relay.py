import logging
import socket
import json


def send_chunks_to_relay(outbound_relay_hostname, chunk_iterator):
    logging.info("connecting to %s:81 ... " % outbound_relay_hostname)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((outbound_relay_hostname, 81))
    try:
        with s.makefile(mode="wb") as f:
            for data in chunk_iterator:
                chunk_size = len(data)
                logging.info("sending chunk (of %s bytes) to sink ..." % chunk_size)
                f.write(("%s\n" % chunk_size).encode())
                f.write(data)
                f.flush()
    finally:
        s.close()


def send_rdd_to_relay(relay_hostname, rdd):
    def send_partition(records):
        events = [r for r in records]
        send_chunks_to_relay(relay_hostname, [json.dumps(events).encode()])
    rdd.foreachPartition(send_partition)
