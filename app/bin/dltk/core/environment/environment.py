from dltk.core.splunk import spec as spec_parser
from splunklib.binding import UrlEncoded
from . conf import name as conf_name

__all__ = [
    "Environment",
]


class Environment(object):
    _splunk = None
    _stanza = None
    _connector = None
    _spec = None

    def __init__(self, splunk, stanza, connector):
        self._splunk = splunk
        self._stanza = stanza
        self._connector = connector

    @property
    def spec(self):
        if self._spec == None:
            import os.path
            spec_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "README", conf_name + ".conf.spec")
            with open(spec_path, "r") as spec_file:
                spec_content = spec_file.read()
            self._spec = spec_parser.parse(spec_content)
        return self._spec

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

    def get_param_spec(self, name):
        stanza_spec = self.spec.get_stanza_for_name(self._stanza.name)
        if stanza_spec:
            attribute_spec = stanza_spec.get_attribute(name)
            if attribute_spec:
                return attribute_spec

    def get_param(self, name, inherit=True):
        if name in self._stanza.content:
            v = self._stanza[name]
            if v is None:
                v = ""
            param_spec = self.get_param_spec(name)
            if param_spec:
                value_spec = param_spec.value_spec
                if value_spec == "<password>":
                    passwords_realm = conf_name + "_" + self._stanza.name
                    storage_password_name = UrlEncoded(passwords_realm, encode_slash=True) + ":" + UrlEncoded(name, encode_slash=True)
                    if storage_password_name in self.splunk.storage_passwords:
                        storage_password = self.splunk.storage_passwords[storage_password_name]
                        v = storage_password.clear_password
                return v
        if inherit:
            return self.connector.get_param(name)
        return None

    def set_param(self, name, value):
        param_spec = self.get_param_spec(name)
        if param_spec:
            value_spec = param_spec.value_spec
            if value_spec == "<password>":
                passwords_realm = conf_name + "_" + self._stanza.name
                storage_password_name = UrlEncoded(passwords_realm, encode_slash=True) + ":" + UrlEncoded(name, encode_slash=True)
                if storage_password_name in self.splunk.storage_passwords:
                    storage_password = self.splunk.storage_passwords[storage_password_name]
                else:
                    storage_password = None
                if value:
                    if storage_password:
                        if storage_password.clear_password != value:
                            self.splunk.storage_passwords.delete(name, passwords_realm)
                            storage_password = self.splunk.storage_passwords.create(value, name, passwords_realm)
                    else:
                        storage_password = self.splunk.storage_passwords.create(value, name, passwords_realm)
                else:
                    if storage_password:
                        self.splunk.storage_passwords.delete(name, passwords_realm)
                value = " "
                # TODO fix value = something so that key exists!
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
