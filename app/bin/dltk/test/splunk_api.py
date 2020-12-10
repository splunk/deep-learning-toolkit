import os
import logging
import splunklib.client as client
import splunklib.results as results
from splunklib.binding import handler as base_handler
import random
import time
import threading
import re
from urllib.parse import urlparse

splunk = None


def connect():
    global splunk
    if not splunk:
        app_name = os.getenv("DLTK_APP_NAME", "dltk")

        base_request = base_handler()
        prefix = os.getenv("SPLUNK_PATH_PREFIX", "")

        def request_with_prefix(url, message, **kwargs):
            o = urlparse(url)
            url = "%s://%s:%s/%s%s" % (o.scheme, o.hostname, o.port, prefix, o.path)
            if o.query:
                url += "?" + o.query
            return base_request(url, message, **kwargs)

        splunk = client.Service(
            handler=request_with_prefix if prefix else None,
            username=os.getenv("SPLUNK_USERNAME", "admin"),
            password=os.getenv("SPLUNK_PASSWORD", "changeme"),
            host=os.getenv("SPLUNK_HOST", "localhost"),
            scheme=os.getenv("SPLUNK_SCHEME", "https"),
            port=int(os.getenv("SPLUNK_PORT", "8089")),
            sharing="app",
            app=app_name,
            autologin=True,
        )
    return splunk


def search(query, log_search_log=False, raise_on_error=True):
    sid = random.randint(300000, 390000)

    logging.info("run search (id=%s): %s" % (sid, query))

    def follow(file):
        """ Yield each line from a file as they are written. """
        line = ''
        while True:
            tmp = file.readline()
            if tmp is not None:
                line += tmp
                if line.endswith("\n"):
                    yield line
                    line = ''
            else:
                time.sleep(0.1)

    # service.jobs.export
    rr = results.ResultsReader(splunk.jobs.export(query, **{"id": sid}))

    if log_search_log:

        #logging.info("waiting for log file to exist...")
        search_log_path = "/opt/splunk/var/run/splunk/dispatch/%s/search.log" % sid
        while True:
            if os.path.exists(search_log_path):
                break
            time.sleep(0.1)
        #logging.info("all right - go ahead")

        search_log_file = open(search_log_path, 'r')

        ChunkedExternProcessor_expression = re.compile(r".*\s(\S+)\s+ChunkedExternProcessor - (.+)$")

        def log_search_log_thread():
            try:
                #logging.info("search log:")
                for line in follow(search_log_file):
                    groups = ChunkedExternProcessor_expression.match(line)
                    if groups:
                        level = groups.group(1)
                        msg = groups.group(2)
                        #logging.info("%s: %s " % (level, msg))
                        if level == "DEBUG":
                            log = logging.debug
                        elif level == "WARNING" or level == "WARN":
                            log = logging.warning
                        elif level == "ERROR":
                            log = logging.error
                        elif level == "INFO":
                            log = logging.info
                        elif level == "FATAL":
                            log = logging.critical
                        else:
                            log = logging.warning
                            msg = "UNEXPECTED search message type (%s): %s" % (level, msg)
                        log("   %s" % (msg))
                    # else:
                    #    logging.info("non match: %s" % (line))

            except ValueError:
                pass

        thread = threading.Thread(target=log_search_log_thread)
        thread.daemon = True
        thread.start()
    else:
        search_log_file = None
        thread = None

    for result in rr:
        if isinstance(result, results.Message):
            #raise Exception("message (type=%s): %s" % (result.type, result.message))
            #logging.warning("search job message (type=%s): %s" % (result.type, result.message))
            level = result.type
            msg = result.message
            if "Successfully wrote file to" in msg:
                continue
            if level == "DEBUG":
                log = logging.debug
            elif level == "WARNING" or level == "WARN":
                log = logging.warning
            elif level == "ERROR":
                log = logging.error
            elif level == "INFO":
                log = logging.info
            elif level == "FATAL":
                log = logging.critical
                if raise_on_error:
                    raise Exception(msg)
            else:
                log = logging.warning
                msg = "UNEXPECTED search message type (%s): %s" % (level, msg)
            log_msg = "%s - %s" % (level, msg)
            log(log_msg)
        elif isinstance(result, dict):
            yield result

    if log_search_log:
        search_log_file.close()
        thread.join()

    logging.info("search finished")
