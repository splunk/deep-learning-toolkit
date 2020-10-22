import os

from . import splunk_api
from . import dltk_api


def set_up():
    splunk = splunk_api.connect()
    runtimes = splunk.confs["dltk_runtimes"]
    # spark
    spark_runtime = runtimes["spark"]
    spark_driver_image = os.getenv("DLTK_SPARK_RUNTIME_DRIVER_IMAGE", "")
    if spark_driver_image:
        spark_runtime.submit({
            "driver_image": spark_driver_image,
        })
    spark_executor_image = os.getenv("DLTK_SPARK_RUNTIME_EXECUTOR_IMAGE", "")
    if spark_executor_image:
        spark_runtime.submit({
            "executor_image": spark_executor_image,
        })
    spark_driver_proxy_image = os.getenv("DLTK_SPARK_RUNTIME_DRIVER_PROXY_IMAGE", "")
    if spark_driver_proxy_image:
        spark_runtime.submit({
            "driver_proxy_image": spark_driver_proxy_image,
        })
    spark_editor_image = os.getenv("DLTK_SPARK_RUNTIME_EDITOR_IMAGE", "")
    if spark_editor_image:
        spark_runtime.submit({
            "editor_image": spark_editor_image,
        })
    spark_inbound_relay_image = os.getenv("DLTK_SPARK_RUNTIME_INBOUND_RELAY_IMAGE", "")
    if spark_inbound_relay_image:
        spark_runtime.submit({
            "inbound_relay_image": spark_inbound_relay_image,
        })
    spark_outbound_relay_image = os.getenv("DLTK_SPARK_RUNTIME_OUTBOUND_RELAY_IMAGE", "")
    if spark_outbound_relay_image:
        spark_runtime.submit({
            "outbound_relay_image": spark_outbound_relay_image,
        })
    # base
    base_runtime = runtimes["base"]
    base_runtime_image = os.getenv("DLTK_BASE_RUNTIME_IMAGE", "")
    if base_runtime_image:
        base_runtime.submit({
            "image": base_runtime_image,
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
