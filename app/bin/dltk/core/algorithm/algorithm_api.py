from dltk.core import deployment
from dltk.core import runtime
from dltk.core import get_class

from . method_stanza_name import is_method
from . import conf
from . import method_api

__all__ = ["create", "exists", "get", "get_all", "delete"]


def exists(splunk, algorithm_name):
    return algorithm_name in conf.get(splunk)


def create(splunk, algorithm_name, runtime_name):
    if exists(splunk, algorithm_name):
        raise Exception("algorithm with name %s already exists" % algorithm_name)
    r = runtime.get(splunk, runtime_name)
    stanza = conf.get(splunk).create(algorithm_name)
    stanza.submit({
        "runtime": runtime_name,
    })
    stanza.refresh()
    algorithm = get(splunk, algorithm_name)
    algorithm.update_source_code(
        code=r.source_code,
        version=1,
    )
    algorithm.update_deployment_code(
        code=r.deployment_code,
        version=1,
    )
    return algorithm


def delete(splunk, algorithm_name):
    a = get(splunk, algorithm_name)
    if not a.can_be_deleted:
        raise Exception("Cannot be deleted")
    deleting_deployments = False
    for d in deployment.get_all_for_algorithm(splunk, algorithm_name):
        deployment.delete(splunk, d)
        deleting_deployments = True
    if deleting_deployments:
        raise Exception("Triggered deleting deployments. Try again later.")

    for m in method_api.get_all(splunk, a):
        method_api.delete(splunk, algorithm_name, m.name)

    conf.get(splunk).delete(algorithm_name)


def get(splunk, algorithm_name):
    if not exists(splunk, algorithm_name):
        raise Exception("algorithm with name %s doesn't exist" % algorithm_name)
    algorithm_stanza = conf.get(splunk)[algorithm_name]
    runtime_name = algorithm_stanza["runtime"]
    if not runtime.exists(splunk, runtime_name):
        raise Exception("algorithm '%s' refers to runtime '%s' which is unknown" % (
            algorithm_name,
            runtime_name,
        ))
    r = runtime.get(splunk, runtime_name)
    algorithm_handler = r.algorithm_handler
    AlgorithmClass = get_class(algorithm_handler)
    return AlgorithmClass(splunk, algorithm_stanza)


def get_all(splunk):
    return [
        get(splunk, stanza.name)
        for stanza in conf.get(splunk)
        if not is_method(stanza.name)
    ]
