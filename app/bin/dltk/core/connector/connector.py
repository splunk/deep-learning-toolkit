

__all__ = [
    "Connector",
]

class Connector(object):
    _splunk = None
    _stanza = None

    def __init__(self, splunk, stanza):
        self._splunk = splunk
        self._stanza = stanza

    @property
    def name(self):
        return self._stanza.name

    @property
    def environment_handler(self):
        return self._stanza["environment_handler"]

    _environment_param_names = None

    @property
    def environment_param_names(self):
        if self._environment_param_names is None:
            self._environment_param_names = set()
            if "environment_params" in self._stanza:
                environment_params = self._stanza["environment_params"]
                if environment_params:
                    for name in environment_params.split(","):
                        name = name.strip()
                        if name:
                            self._environment_param_names.add(name)
        return self._environment_param_names

    def get_param(self, name):
        if name in self._stanza.content:
            return self._stanza.content[name]
        else:
            return None

    @property
    def params(self):
        config = dict()
        for name in self.environment_param_names:
            value = self.get_param(name)
            config[name] = value
        return config

    def test_connection(self, environment):
        raise Exception("not implemented")
