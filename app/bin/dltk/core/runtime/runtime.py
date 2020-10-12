from dltk.core import connector

__all__ = [
    "Runtime",
]


class Runtime(object):
    _splunk = None
    _stanza = None
    _connector = None

    def __init__(self, splunk, stanza):
        self._splunk = splunk
        self._stanza = stanza

    @property
    def name(self):
        return self._stanza.name

    @property
    def connector_name(self):
        return self._stanza["connector"]

    @property
    def connector(self):
        if not self._connector:
            self._connector = connector.get(self._splunk, self.connector_name)
        return self._connector

    _algorithm_param_names = None

    @property
    def algorithm_param_names(self):
        if self._algorithm_param_names is None:
            self._algorithm_param_names = set()
            if "algorithm_params" in self._stanza:
                algorithm_params = self._stanza["algorithm_params"]
                if algorithm_params:
                    for name in algorithm_params.split(","):
                        name = name.strip()
                        if name:
                            self._algorithm_param_names.add(name)
        return self._algorithm_param_names

    @algorithm_param_names.setter
    def set_algorithm_param_names(self, value):
        if not isinstance(value, str):
            value = ','.join(value)
        self._stanza.submit({
            "algorithm_params": value,
        })

    _deployment_param_names = None

    @property
    def deployment_param_names(self):
        if self._deployment_param_names is None:
            self._deployment_param_names = set()
            if "deployment_params" in self._stanza:
                deployment_params = self._stanza["deployment_params"]
                if deployment_params:
                    for name in deployment_params.split(","):
                        name = name.strip()
                        if name:
                            self._deployment_param_names.add(name)
        return self._deployment_param_names

    @property
    def deployment_handler(self):
        return self._stanza["deployment_handler"]

    @property
    def execution_handler(self):
        return self._stanza["execution_handler"]

    @property
    def algorithm_handler(self):
        return self._stanza["algorithm_handler"]

    def get_param(self, name):
        if name in self._stanza.content:
            return self._stanza.content[name]
        else:
            return None

    def set_param(self, name, value):
        self._stanza.submit({
            name: value
        })
        self._stanza.refresh()

    @property
    def deployment_code(self):
        deployment_code = self._stanza["deployment_code"]
        if deployment_code is None:
            deployment_code = ""
        return deployment_code

    @property
    def source_code(self):
        source_code = self._stanza["source_code"]
        if source_code is None:
            source_code = ""
        return source_code
