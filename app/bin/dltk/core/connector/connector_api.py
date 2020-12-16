
from dltk.core import get_class
from . connector import Connector

conf_name = "dltk_connectors"

__all__ = [
    "get",
    "get_all",
    "exists",
    "create",
    "delete",
]


def exists(splunk, name):
    if name in splunk.confs[conf_name]:
        return True
    else:
        return False


def get(splunk, name):
    stanza = splunk.confs[conf_name][name]
    ConnectorClass = Connector
    if "handler" in stanza:
        handler = stanza["handler"]
        if handler:
            ConnectorClass = get_class(handler)
    return ConnectorClass(splunk, stanza)


def get_all(splunk):
    return [get(splunk, stanza.name) for stanza in splunk.confs[conf_name]]


def create(splunk, name):
    stanza = splunk.confs[conf_name].create(name)
    stanza.submit({
    })
    stanza.refresh()


def delete(splunk, name):
    if not exists(splunk, name):
        raise Exception("connector '%s' does not exist" % name)
    splunk.confs[conf_name].delete(name)
