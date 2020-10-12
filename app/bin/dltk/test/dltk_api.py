import json
import os
from . import splunk_api
import logging
import splunklib
import time


def call(method, path, data=None, return_entries=True):
    path = "dltk/" + path
    logging.info("calling DLTK API: %s %s" % (method, path))
    splunk = splunk_api.connect()
    if data == None:
        data = {}
    earliest_time = time.time()
    try:
        if method == "GET":
            response_reader = splunk.get(
                path,
                **data
            )["body"]
        if method == "DELETE":
            response_reader = splunk.delete(
                path,
                **data
            )["body"]
        if method == "PUT":
            headers = []
            if data:
                headers.append(("Content-Type", "application/x-www-form-urlencoded"))
            response_reader = splunk.put(
                path, headers=headers, **data
            )["body"]
        if method == "POST":
            headers = []
            if data:
                headers.append(("Content-Type", "application/x-www-form-urlencoded"))
            response_reader = splunk.post(
                path, headers=headers, **data
            )["body"]
        if return_entries:
            deployments_result = response_reader.read()
            test = json.loads(deployments_result)
            entries = []
            for entry in test["entry"]:
                content = entry["content"]
                entries.append(content)
            return entries
    except splunklib.binding.HTTPError as e:
        latest_time = time.time()
        if e.status >= 500 or e.status == 400:
            time.sleep(3)
            for event in splunk_api.search("| search earliest=%s latest=%s index=_internal sourcetype=splunk_python" % (
                earliest_time,
                latest_time,
            ), log_serach_log=False):
                raw = event["_raw"]
                logging.warning(raw)
        raise
