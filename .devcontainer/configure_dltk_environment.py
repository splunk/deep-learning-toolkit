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

if __name__ == "__main__":

    splunk = splunk_api.connect()
    print("logging in ...")
    while True:
        try:
            splunk.login()
            e = None
            break
        except:
            time.sleep(1)

    environment_name = "host_docker_internal"
    environments = splunk.confs["dltk_environments"]
    if environment_name in environments:
        environments.delete(environment_name)
    environment = environments.create(environment_name)
    environment.submit({
        "connector": "kubernetes",
        "auth_mode": "cert-key",
    })
