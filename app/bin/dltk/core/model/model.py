
from dltk.core import deployment
from dltk.core import environment
from dltk.core import algorithm

__all__ = ["Model"]


class Model(object):
    _splunk = None
    _stanza = None
    _deployment = None
    _algorithm = None
    _environment = None

    def __init__(self, splunk, stanza):
        self._splunk = splunk
        self._stanza = stanza

    @property
    def name(self):
        return self._stanza.name

    @property
    def algorithm_name(self):
        return self._stanza["algorithm"]

    @property
    def environment_name(self):
        return self._stanza["environment"]

    @property
    def deployment(self):
        if not self._deployment:
            algorithm_name = self.algorithm_name
            environment_name = self.environment_name
            self._deployment = deployment.get(self._splunk, algorithm_name, environment_name)
        return self._deployment

    @property
    def algorithm(self):
        if not self._algorithm:
            algorithm_name = self.algorithm_name
            self._algorithm = algorithm.get(self._splunk, algorithm_name)
        return self._algorithm

    @property
    def environment(self):
        if not self._environment:
            environment_name = self.environment_name
            self._environment = environment.get(self._splunk, environment_name)
        return self._environment

    @property
    def runtime(self):
        return self.algorithm.runtime
