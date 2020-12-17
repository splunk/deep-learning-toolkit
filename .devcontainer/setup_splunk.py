import os
import sys

bin_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "bin"))
if bin_path not in sys.path:
    sys.path.insert(0, bin_path)
lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "lib"))
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)

import time
from dltk.test import splunk_api
from kubernetes.config.kube_config import load_kube_config
from kubernetes.client import Configuration
from pathlib import Path
from dltk.core.environment.conf import name as environment_conf_name
from splunklib.binding import AuthenticationError
import traceback
import base64
from urllib.parse import urlparse

if __name__ == "__main__":

    splunk = splunk_api.connect()
    print("logging in ...")
    while True:
        try:
            splunk.login()
            e = None
            break
        except AuthenticationError as e:
            print("authentication error: %s" % e)
            exit(1)
        except Exception as e:
            err_msg = traceback.format_exc()
            print("%s" % err_msg)
            time.sleep(1)

    #print("loading kubernetes config...")
    # try:
    #    print("/root/.kube/config: %s" % os.path.exists("/root/.kube/config"))
    #    load_kube_config()
    #    config = Configuration._default
    # except Exception as e:
    #    err_msg = traceback.format_exc()
    #    print("%s" % err_msg)
    #    exit(1)

    print("creating dltk environment...")
    try:
        environment_name = os.getenv("DLTK_ENVIRONMENT", "")
        print("environment_name: %s" % environment_name)
        environments = splunk.confs[environment_conf_name]
        if environment_name in environments:
            environments.delete(environment_name)
        environment = environments.create(environment_name)
        environment.submit({
            "connector": "kubernetes",
            "auth_mode": "in-cluster",
            "ingress_mode": "ingress",
            "ingress_class": "nginx",
            "ingress_url": "http://ingress-nginx-controller.ingress-nginx",  # os.getenv("INGRESS_URL"),
        })
    except Exception as e:
        err_msg = traceback.format_exc()
        print("%s" % err_msg)
        exit(1)
