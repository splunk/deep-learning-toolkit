from dltk.core import connector, get_class
from . environment import Environment
from . conf import conf_name, get_conf

__all__ = [
    "exists",
    "get",
    "get_all",
    "connect",
]


def exists(splunk, name):
    if name in get_conf(splunk):
        return True
    else:
        return False


def get(splunk, name):
    stanza = get_conf(splunk)[name]
    connector_name = stanza["connector"]
    EnvironmentClass = Environment
    c = None
    if connector_name:
        c = connector.get(splunk, connector_name)
        handler = c.environment_handler
        if handler:
            EnvironmentClass = get_class(handler)
    return EnvironmentClass(splunk, stanza, c)


def get_all(splunk):
    return [
        get(splunk, stanza.name)
        for stanza in get_conf(splunk)
    ]


def connect(splunk, name):
    return object()


def create(splunk, name, connector_name):
    stanza = get_conf(splunk).create(name)
    stanza.submit({
        "connector": connector_name,
    })
    stanza.refresh()


def delete(splunk, name):
    if not exists(splunk, name):
        raise Exception("environment '%s' does not exist" % name)
    get_conf(splunk).delete(name)
