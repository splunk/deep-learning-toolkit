from . import algorithm
from . import method_stanza_name


class Method(object):
    _algorithm = None
    _stanza = None
    _name = None

    def __init__(self, splunk, stanza, algorithm=None):
        self._algorithm = algorithm
        self._stanza = stanza

    @property
    def name(self):
        if not self._name:
            self._name = method_stanza_name.parse_method_name(self._stanza.name)
        return self._name

    @property
    def algorithm(self):
        if not self._algorithm:
            algorithm_name = method_stanza_name.parse_algorithm_name(self._stanza.name)
            self._algorithm = algorithm.get(self._splunk, algorithm_name)
        return self._algorithm

    def get_param(self, name, inherit=True):
        if name in self._stanza.content:
            v = self._stanza[name]
            if v is None:
                v = ""
            return v
        if inherit:
            return self.algorithm.get_param(name)
        return None

    @property
    def support_preop(self):
        return True

    @property
    def max_buffer_size(self):
        return self.get_param("max_buffer_size")

    @property
    def command_type(self):
        return self.get_param("command_type")
