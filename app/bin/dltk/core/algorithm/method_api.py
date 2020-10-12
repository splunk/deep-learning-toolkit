
from . import method_stanza_name
from . import conf
from . method import Method

__all__ = ["exists", "create", "delete", "get_all", "get"]


def exists(splunk, algorithm_name, method_name):
    stanza_name = method_stanza_name.format(algorithm_name, method_name)
    return stanza_name in conf.get(splunk)


def create(splunk, algorithm_name, method_name):
    if exists(splunk, algorithm_name, method_name):
        raise Exception("method %s already exist in algo %s" % (method_name, algorithm_name))
    stanza_name = method_stanza_name.format(algorithm_name, method_name)
    stanza = conf.get(splunk).create(stanza_name)
    stanza.submit({
        # "runtime": runtime_name,
    })
    stanza.refresh()


def delete(splunk, algorithm_name, method_name):
    if not exists(splunk, algorithm_name, method_name):
        raise Exception("method %s doesn's exist in algo %s" % (method_name, algorithm_name))
    stanza_name = method_stanza_name.format(algorithm_name, method_name)
    conf.get(splunk).delete(stanza_name)


def get(splunk, algorithm, method_name):
    algorithm_name = algorithm.name
    if not exists(splunk, algorithm_name, method_name):
        raise Exception("algorithm %s has not method %s" % (algorithm_name, method_name))
    stanza_name = method_stanza_name.format(algorithm_name, method_name)
    method_stanza = conf.get(splunk)[stanza_name]
    return Method(splunk, method_stanza, algorithm)


def get_all(splunk, algorithm):
    def get_method(stanza):
        method_name = method_stanza_name.parse_method_name(stanza.name)
        return get(splunk, algorithm, method_name)

    def is_algo_method(stanza):
        if not method_stanza_name.is_method(stanza.name):
            return False
        return method_stanza_name.parse_algorithm_name(stanza.name) == algorithm.name
    return [
        get_method(stanza)
        for stanza in conf.get(splunk)
        if is_algo_method(stanza)
    ]
