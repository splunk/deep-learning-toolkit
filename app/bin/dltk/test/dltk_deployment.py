import unittest
import os
import logging
import time
import re

import splunklib.client as client
import splunklib.results as results
from splunklib.binding import HTTPError

from . import dltk_api
from . import splunk_api
from . import dltk_environment

level_prog = re.compile(r'level=\"([^\"]*)\"')
msg_prog = re.compile(r'msg=\"((?:\n|.)*)\"')


def run_job(algorithm_name):
    environment_name = dltk_environment.get_name()
    # raise Exception("| savedsearch job:deploy:%s:%s | %s" % (
    #    algorithm_name,
    #    environment_name,
    #    'rex field=_raw "level=\\"(?<level>[^\\"]*)\\", msg=\\"(?<msg>[^[\\"|\\\\"]*)\\"" | table level msg',
    # ))
    for event in splunk_api.search("| savedsearch job:deploy:%s:%s | %s" % (
        algorithm_name,
        environment_name,
        #'rex field=_raw "level=\\"(?<level>[^\\"]*)\\", msg=\\"(?<msg>.*)\\"" | table _raw level msg',
        #'rex field=_raw "level=\\"(?<level>[^\\"]*)\\", msg=\\"(?<msg>(?:\\n|.)*)\\"" | table _raw level msg',
        'table _raw',
    )):
        raw = event["_raw"]

        if "level" not in event:
            m = level_prog.search(raw)
            if m:
                event["level"] = m.group(1)

        if "msg" not in event:
            m = msg_prog.search(raw)
            if m:
                event["msg"] = m.group(1)

        if "level" in event:
            level = event["level"]
        else:
            #logging.error("missing 'level' field in deploy result: %s" % (event))
            raise Exception("missing 'level' field in deploy result: %s" % raw)
            # continue
        msg = event["msg"]
        if level == "DEBUG":
            log = logging.debug
        elif level == "WARNING":
            log = logging.warning
        elif level == "ERROR":
            log = logging.error
        elif level == "INFO":
            log = logging.info
        else:
            log = logging.warning
            msg = "UNEXPECTED LEVEL (%s): %s" % (level, msg)
        log("   %s" % msg)


def list_deployments(algorithm_name):
    return dltk_api.call(
        "GET",
        "deployments",
        data={
            "algorithm": algorithm_name,
        }
    )


def get_deployment(algorithm_name, environment_name, raise_if_not_exists=True):
    deployments = dltk_api.call(
        "GET",
        "deployments",
        data={
            "algorithm": algorithm_name,
            "environment": environment_name,
        }
    )
    if not len(deployments):
        if raise_if_not_exists:
            raise Exception("could not find deployment")
        return None
    return deployments[0]


def deploy(algorithm_name, params={}):
    undeploy(algorithm_name)
    splunk = splunk_api.connect()
    environment_name = dltk_environment.get_name()
    dltk_api.call("POST", "deployments", data={
        **{
            "algorithm": algorithm_name,
            "environment": environment_name,
            "enable_schedule": False,
        },
        **params,
    }, return_entries=False)
    try:
        while True:
            deployment = get_deployment(algorithm_name, environment_name, raise_if_not_exists=False)
            if deployment:
                deployment = get_deployment(algorithm_name, environment_name)
                status = deployment["status"]
                if status == "deploying":
                    logging.info("still deploying...")
                    run_job(algorithm_name)
                    continue
                if status == "deployed":
                    break
                status_message = deployment["status_message"]
                raise Exception("unexpected deployment status: %s: %s" % (status, status_message))
        logging.info("successfully deployed algo \"%s\"" % algorithm_name)
    except:
        logging.warning("error deploying '%s' to '%s' -> undeploying ..." % (algorithm_name, environment_name))
        # while True:
        #    import time
        #    time.sleep(10)
        undeploy(algorithm_name)
        logging.warning("finished undeploying")
        raise


def undeploy(algorithm_name):
    splunk = splunk_api.connect()
    environment_name = dltk_environment.get_name()
    while True:
        try:
            dltk_api.call("DELETE", "deployments", data={
                "algorithm": algorithm_name,
                "environment": environment_name,
                "enable_schedule": False,
            }, return_entries=False)
        except HTTPError as e:
            logging.error("error calling API: %s" % e)
            if e.status == 404:
                break
            raise
        run_job(algorithm_name)
