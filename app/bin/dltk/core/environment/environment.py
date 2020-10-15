

__all__ = [
    "Environment",
]


class Environment(object):
    _splunk = None
    _stanza = None
    _connector = None

    def __init__(self, splunk, stanza, connector):
        self._splunk = splunk
        self._stanza = stanza
        self._connector = connector

    @property
    def splunk(self):
        return self._splunk

    @property
    def name(self):
        return self._stanza.name

    @property
    def connector_name(self):
        return self._stanza["connector"]

    @property
    def connector(self):
        return self._connector

    @property
    def opentracing_endpoint(self):
        if "opentracing_endpoint" in self._stanza:
            return self._stanza["opentracing_endpoint"]
        else:
            return None

    @property
    def opentracing_user(self):
        if "opentracing_user" in self._stanza:
            return self._stanza["opentracing_user"]
        else:
            return None

    @property
    def opentracing_password(self):
        if "opentracing_password" in self._stanza:
            return self._stanza["opentracing_password"]
        else:
            return None

    def get_param(self, name, inherit=True):
        if name in self._stanza.content:
            v = self._stanza[name]
            if v is None:
                v = ""
            return v
        if inherit:
            return self.connector.get_param(name)
        return None

    def set_param(self, name, value):
        self._stanza.submit({
            name: value
        })
        self._stanza.refresh()

    @property
    def params(self):
        params = dict()
        for name in self.connector.environment_param_names:
            params[name] = self.get_param(name)
        return params
