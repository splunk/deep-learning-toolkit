from dltk.core import get_class
from dltk.core import algorithm as algorithms

from . deployment import Deployment
from . import stanza_name

from .conf import conf_name

__all__ = [
    "exists",
    "get",
    "get_all",
    "get_all_for_algorithm",
    "get_environment_names_for_algorithm",
]


def exists(splunk, algorithm_name, environment_name):
    deployment_name = stanza_name.format(algorithm_name, environment_name)
    return deployment_name in splunk.confs[conf_name]


def get(splunk, algorithm_name, environment_name):
    deployment_name = stanza_name.format(algorithm_name, environment_name)
    deployments = splunk.confs[conf_name]
    if deployment_name not in deployments:
        return None
    stanza = deployments[deployment_name]
    DeploymentClass = Deployment
    algorithm = algorithms.get(splunk, algorithm_name)
    handler = algorithm.runtime.deployment_handler
    if handler:
        DeploymentClass = get_class(handler)
    return DeploymentClass(splunk, stanza)


def get_all(splunk):
    def map(stanza):
        algorithm_name, environment_name = stanza_name.parse(stanza.name)
        return get(splunk, algorithm_name, environment_name)
    return [
        map(stanza)
        for stanza in splunk.confs[conf_name]
    ]


def get_all_for_algorithm(splunk, algorithm_name):
    def is_target_algorithm(stanza):
        test, _ = stanza_name.parse(stanza.name)
        return test == algorithm_name

    def map(stanza):
        _, environment_name = stanza_name.parse(stanza.name)
        return get(splunk, algorithm_name, environment_name)
    return [
        map(stanza)
        for stanza in splunk.confs[conf_name]
        if is_target_algorithm(stanza)
    ]


def get_environment_names_for_algorithm(splunk, algorithm_name):
    def is_target_algorithm(stanza):
        test, _ = stanza_name.parse(stanza.name)
        return test == algorithm_name

    def map(stanza):
        _, environment_name = stanza_name.parse(stanza.name)
        return environment_name
    return [
        map(stanza)
        for stanza in splunk.confs[conf_name]
        if is_target_algorithm(stanza)
    ]
