import os

from . import splunk_api
from . import dltk_api


def get_name():
    name, _ = get_name_and_temp()
    return name


def get_name_and_temp():
    name = os.getenv("DLTK_ENVIRONMENT", "")
    if name:
        return name, False
    else:
        return "in-cluster", True


def set_up():
    splunk = splunk_api.connect()
    environment_name, is_temp_env = get_name_and_temp()
    if is_temp_env:
        environments = splunk.confs["dltk_environments"]
        if environment_name in environments:
            environments.delete(environment_name)
        environment = environments.create(environment_name)
        environment.submit({
            "connector": "kubernetes",
            "auth_mode": "in-cluster",
            "ingress_mode": "ingress",
            "ingress_url": os.getenv("DLTK_INGRESS_URL", "http://ingress"),
            "ingress_class": os.getenv("DLTK_INGRESS_CLASS", "nginx"),
            "relay_hdfs_url": os.getenv("DLTK_HDFS_HTTP_URL", "http://hdfs-namenode:50070"),
            "spark_hdfs_url": os.getenv("DLTK_HDFS_URL", "hdfs://hdfs-namenode/"),
            "namespace": "default",
            "image_pull_policy": "Never",
            "tag_label": "test",
            "executor_cores": "1",
            "executor_instance_count": "1",
        })
        image_pull_policy = os.getenv("DLTK_IMAGE_PULL_POLICY", "")
        if image_pull_policy:
            environment.submit({
                "image_pull_secret": image_pull_policy,
            })


def get_all():
    return dltk_api.call("GET", "environments")


def tear_down():
    splunk = splunk_api.connect()
    environment_name, is_temp_env = get_name_and_temp()
    if is_temp_env:
        environments = splunk.confs["dltk_environments"]
        environments.delete(environment_name)


def exists(name):
    environments = dltk_api.call("GET", "environments")
    filtered = list(filter(lambda c: c["name"] == name, environments))
    return len(filtered)


def create(name, connector, delete_if_already_exists=False):
    if delete_if_already_exists:
        if exists(name):
            delete(name)
    dltk_api.call("POST", "environments", {
        "name": name,
        "connector": connector,
    }, return_entries=False)


def delete(name, skip_if_not_exists=False):
    if skip_if_not_exists:
        if not exists(name):
            return
    dltk_api.call("DELETE", "environments", {
        "name": name,
    }, return_entries=False)


def get_environment_params(connector_name=None, environment_name=None):
    options = {}
    if connector_name:
        options["connector"] = connector_name
    if environment_name:
        options["environment"] = environment_name
    return dltk_api.call(
        "GET",
        "environment_params",
        options
    )


def get_environment_param(param_name, connector_name=None, environment_name=None):
    params = get_environment_params(
        connector_name=connector_name,
        environment_name=environment_name
    )
    for p in params:
        if p["name"] == param_name:
            return p
    return None


def set_environment_params(params, connector_name=None, environment_name=None):
    dltk_api.call(
        "PUT",
        "environment_params",
        {
            **{
                "connector": connector_name,
                "environment": environment_name,
            },
            **params,
        },
        return_entries=False,
    )
