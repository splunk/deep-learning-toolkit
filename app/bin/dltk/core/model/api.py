
from dltk.core import deployment

from .model import *

conf_name = "dltk_models"

__app__ = [
    "create",
    "delete",
    "get",
    "exists",
    "get_all",
    "get_all_in_deployment",
]


def create(splunk, model_name, algorithm_name, environment_name):
    d=deployment.get(splunk, algorithm_name, environment_name)
    stanza = splunk.confs[conf_name].create(model_name)
    stanza.submit({
        "algorithm": algorithm_name,
        "environment": environment_name,
    })
    stanza.refresh()
    model = get(splunk, model_name)
    d.trigger_deploying()
    return model


def delete(splunk, model_name, update_deployment=True):
    model = get(splunk, model_name)
    splunk.confs[conf_name].delete(model.name)
    if update_deployment:
        d = model.deployment
        d.trigger(trigger_deploying)


def get(splunk, model_name):
    try:
        stanza = splunk.confs[conf_name][model_name]
    except KeyError:
        raise Exception("Model '%s' doesn't exist" % model_name)
    return Model(splunk, stanza)


def exists(splunk, model_name):
    return model_name in splunk.confs[conf_name]


def get_all(splunk):
    for stanza in splunk.confs[conf_name]:
        yield get(splunk, stanza.name)


def get_all_in_deployment(splunk, algorithm_name, environment_name):
    for model in get_all(splunk):
        if model.algorithm_name != algorithm_name:
            continue
        if model.environment_name != environment_name:
            continue
        yield model
