from dltk.core import algorithm as algorithms
from dltk.core import environment
from dltk.core import execution
from dltk.core import is_truthy
from dltk.core import get_class
from dltk.core import logging

from . import stanza_name
from . status import *
from . params import get_default_param
from . import jobs


class Deployment(object):
    _splunk = None
    _stanza = None
    _algorithm = None
    _environment = None
    _logger = None

    def __init__(self, splunk, stanza):
        self._splunk = splunk
        self._stanza = stanza

    @property
    def splunk(self):
        return self._splunk

    @property
    def name(self):
        return self._stanza.name

    @property
    def algorithm_name(self):
        name, _ = stanza_name.parse(self._stanza.name)
        return name

    @property
    def environment_name(self):
        _, name = stanza_name.parse(self._stanza.name)
        return name

    @property
    def logger(self):
        if self._logger is None:
            self._logger = logging.wrap({
                "algorithm": self.algorithm_name,
                "environment": self.environment_name,
            })
        return self._logger

    @property
    def algorithm(self):
        if not self._algorithm:
            self._algorithm = algorithms.get(self._splunk, self.algorithm_name)
        return self._algorithm

    @property
    def environment(self):
        if not self._environment:
            self._environment = environment.get(self._splunk, self.environment_name)
        return self._environment

    @property
    def status(self):
        status = self._stanza["status"]
        if status is None:
            status = ""
        return status

    @status.setter
    def status(self, status):
        if self.status != status:
            self._stanza.submit({
                "status": status
            })
            self._stanza.refresh()

    @property
    def is_disabled(self):
        value = self._stanza["disabled"]
        if value is None:
            value = False
        return is_truthy(value)

    @is_disabled.setter
    def is_disabled(self, value):
        value = is_truthy(value)
        if self.is_disabled != value:
            self._stanza.submit({
                "disabled": value
            })
            self._stanza.refresh()

    @property
    def is_deployed(self):
        return self.status == STATUS_DEPLOYED

    @property
    def status_message(self):
        status_message = self._stanza["status_message"]
        if status_message is None:
            status_message = ""
        return status_message

    @status_message.setter
    def status_message(self, status_message):
        if self.status_message != status_message:
            self._stanza.submit({
                "status_message": status_message
            })
            self._stanza.refresh()

    def get_param(self, name, inherit=True):
        if name in self._stanza.content:
            v = self._stanza.content[name]
            if v is None:
                v = ""
            return v
        if inherit:
            return get_default_param(name, self.environment, algorithm=self.algorithm)
        return None

    def set_param(self, name, value):
        self._stanza.submit({
            name: value
        })
        self._stanza.refresh()

    def trigger_deploying(self, enable_schedule=None):
        jobs.trigger(
            self._splunk,
            self,
            status=STATUS_DEPLOYING,
        )

    @property
    def runtime_status(self):
        prefix = "runtime_status."
        status = dict()
        for key, value in self._stanza.content.items():
            if key.startswith(prefix):
                name = key[len(prefix):]
                status[name] = value
        return status

    @runtime_status.setter
    def runtime_status(self, status):
        runtime_status = dict()
        for key, value in status.items():
            runtime_status["runtime_status." + key] = value
        self._stanza.submit(runtime_status)
        self._stanza.refresh()

    @property
    def editable(self):
        value = self._stanza["editable"]
        if value is None:
            return False
        return is_truthy(value)

    @editable.setter
    def editable(self, value):
        value = is_truthy(value)
        if self.editable != value:
            self._stanza.submit({
                "editable": value
            })
            self._stanza.refresh()

    @property
    def restart_required(self):
        value = self._stanza["restart_required"]
        if value is None:
            return False
        return is_truthy(value)

    @restart_required.setter
    def restart_required(self, value):
        value = is_truthy(value)
        if self.restart_required != value:
            self._stanza.submit({
                "restart_required": value
            })
            self._stanza.refresh()

    @property
    def editor_url(self):
        value = self._stanza["editor_url"]
        if value is None:
            value = ""
        return value

    @editor_url.setter
    def editor_url(self, url):
        if self.editor_url != url:
            self._stanza.submit({
                "editor_url": url
            })
            self._stanza.refresh()

    @property
    def guid(self):
        guid = ""
        if "guid" in self._stanza.content:
            guid = self._stanza.content["guid"]
        return guid

    def deploy(self):
        pass

    def undeploy(self):
        pass

    def list_models(self):
        return []

    def create_model(self, model):
        raise Exception("create_model not implemented")

    def delete_model(self, model_name):
        raise Exception("delete_model not implemented")

    def execute(self, method, events, ctx):
        raise Exception("execute not implemented")

    def create_execution(self, context):
        ExecutionClass = execution.Execution
        handler = self.algorithm.runtime.execution_handler
        if handler:
            ExecutionClass = get_class(handler)
        return ExecutionClass(self, context)
