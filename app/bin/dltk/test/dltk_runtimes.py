import os

from . import splunk_api
from . import dltk_api


def set_up():
    splunk = splunk_api.connect()
    runtimes = splunk.confs["dltk_runtimes"]
    spark_runtime = runtimes["spark"]
    spark_driver_image = os.getenv("DLTK_SPARK_RUNTIME_DRIVER_IMAGE", "")
    if spark_driver_image:
        spark_runtime.submit({
            "driver_image": spark_driver_image,
        })


def tear_down():
    pass


def exists(name):
    runtimes = dltk_api.call("GET", "runtimes")
    filtered = list(filter(lambda c: c["name"] == name, runtimes))
    return len(filtered)


def create(name, connector, delete_if_already_exists=False, params={}):
    if delete_if_already_exists:
        if exists(name):
            delete(name, skip_if_not_exists=True)
    dltk_api.call(
        "POST",
        "runtimes",
        {
            **{
                "name": name,
                "connector": connector,
            },
            **params,
        },
        return_entries=False,
    )


def delete(name, skip_if_not_exists=False):
    if skip_if_not_exists:
        if not exists(name):
            return
    dltk_api.call("DELETE", "runtimes", {
        "name": name,
    }, return_entries=False)


def get_algorithm_params(name):
    return dltk_api.call(
        "GET",
        "algorithm_params", {
            "runtime": name,
        }
    )

def get_algorithm_param(runtime_name, param_name):
    params = get_algorithm_params(runtime_name)
    for p in params:
        if p["name"] == param_name:
            return p
    return None


def set_algorithm_params(name, params):
    dltk_api.call(
        "PUT",
        "algorithm_params",
        {
            **{
                "runtime": name,
            },
            **params,
        },
        return_entries=False,
    )
