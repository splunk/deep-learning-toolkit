from . runtime import Runtime
from dltk.core import get_class

conf_name = "dltk_runtimes"

__all__ = [
    "get",
    "get_all",
    "exists",
    "create",
]


def exists(splunk, name):
    if not name:
        return False
    return name in splunk.confs[conf_name]


def get(splunk, name):
    if not exists(splunk, name):
        raise Exception("runtime '%s' does not exist" % name)
    stanza = splunk.confs[conf_name][name]
    RuntimeClass = Runtime
    if "handler" in stanza:
        handler = stanza["handler"]
        if handler:
            RuntimeClass = get_class(handler)
    return RuntimeClass(splunk, stanza)


def get_all(splunk):
    return [get(splunk, stanza.name) for stanza in splunk.confs[conf_name]]


def create(splunk, name, connector_name):
    stanza = splunk.confs[conf_name].create(name)
    stanza.submit({
        "connector": connector_name,
    })
    stanza.refresh()
    return get(splunk, name)


def delete(splunk, name):
    if not exists(splunk, name):
        raise Exception("runtime '%s' does not exist" % name)
    splunk.confs[conf_name].delete(name)
