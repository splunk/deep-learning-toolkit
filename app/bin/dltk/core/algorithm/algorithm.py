from dltk.core import runtime
from dltk.core import is_truthy

from . import method_api

__all__ = ["Algorithm"]


class Algorithm(object):
    _splunk = None
    _stanza = None
    _runtime = None
    _methods = None
    _deployments = None

    def __init__(self, splunk, stanza):
        self._splunk = splunk
        self._stanza = stanza

    @property
    def name(self):
        return self._stanza.name

    @property
    def can_be_deleted(self):
        return is_truthy(self._stanza.access["removable"])

    @property
    def runtime_name(self):
        return self._stanza["runtime"]

    @property
    def runtime(self):
        if not self._runtime:
            self._runtime = runtime.get(self._splunk, self.runtime_name)
        return self._runtime

    @property
    def category(self):
        category = self._stanza["category"]
        if category is None:
            category = ""
        return category

    @category.setter
    def category(self, category):
        if self.category != category:
            self._stanza.submit({
                "category": category
            })
            self._stanza.refresh()

    @property
    def description(self):
        description = self._stanza["description"]
        if description is None:
            description = ""
        return description

    @description.setter
    def description(self, description):
        if self.description != description:
            self._stanza.submit({
                "description": description
            })
            self._stanza.refresh()

    @property
    def source_code(self):
        source_code = self._stanza["source_code"]
        if source_code is None:
            source_code = ""
        return source_code

    @property
    def source_code_version(self):
        source_code_version = self._stanza["source_code_version"]
        if source_code_version is None:
            source_code_version = 0
        return int(source_code_version)

    def update_source_code(self, code, version=None):
        if code != self.source_code or (version is not None and version != self.source_code_version):
            if version is None:
                version = self.source_code_version + 1
            self._stanza.submit({
                "source_code": code,
                "source_code_version": version,
            })
            self._stanza.refresh()

    @property
    def deployment_code(self):
        deployment_code = self._stanza["deployment_code"]
        if deployment_code is None:
            deployment_code = ""
        return deployment_code

    @property
    def deployment_code_version(self):
        deployment_code_version = self._stanza["deployment_code_version"]
        if deployment_code_version is None:
            deployment_code_version = 0
        return int(deployment_code_version)

    def update_deployment_code(self, code, version):
        if code != self.deployment_code or version != self.deployment_code_version:
            self._stanza.submit({
                "deployment_code": code,
                "deployment_code_version": version,
            })
            self._stanza.refresh()

    def get_param(self, name, inherit=True):
        if name in self._stanza.content:
            v = self._stanza[name]
            if v is None:
                v = ""
            return v
        if inherit:
            return self.runtime.get_param(name)
        return None

    def set_param(self, name, value):
        self._stanza.submit({
            name: value
        })
        self._stanza.refresh()

    @property
    def methods(self):
        if self._methods is None:
            self._methods = method_api.get_all(self._splunk, self)
        return self._methods

    def get_method(self, name):
        for m in self.methods:
            if m.name == name:
                return m
        return None

    @property
    def deployments(self):
        if self._deployments is None:
            from dltk.core.deployment import get_all_for_algorithm
            self._deployments = get_all_for_algorithm(self._splunk, self.name)
        return self._deployments

    @property
    def default_method(self):
        default_method = self._stanza["default_method"]
        if default_method == "":
            default_method = None
        return default_method

    @default_method.setter
    def default_method(self, method):
        if method is None:
            method = ""
        self._stanza.submit({
            "default_method": method
        })
        self._stanza.refresh()
