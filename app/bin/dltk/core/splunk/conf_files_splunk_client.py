import os
from configparser import ConfigParser


class ConfigurationStanza(object):
    _default_parser = None
    _local_parser = None
    _name = None
    _content = None
    _file = None

    def __init__(self, file, name, default_parser, local_parser):
        self._default_parser = default_parser
        self._local_parser = local_parser
        self._name = name
        self._file = file

    @property
    def name(self):
        return self._name

    @property
    def content(self):
        if self._content is None:
            self._content = {}
            if self._default_parser:
                if self._default_parser.has_section("default"):
                    self._content.update(self._default_parser._sections["default"])
                if self._default_parser.has_section(self.name):
                    self._content.update(self._default_parser._sections[self._name])
            if self._local_parser:
                if self._local_parser.has_section("default"):
                    self._content.update(self._local_parser._sections["default"])
                if self._local_parser.has_section(self.name):
                    self._content.update(self._local_parser._sections[self._name])
        return self._content

    def __getitem__(self, key):
        if self._local_parser:
            result = self._local_parser.get(self._name, key, fallback=None)
            if result is None:
                result = self._local_parser.get("default", key, fallback=None)
        else:
            result = None
        if result is None and self._default_parser:
            result = self._default_parser.get(self._name, key, fallback=None)
            if result is None:
                result = self._default_parser.get("default", key, fallback=None)
        return result

    def __contains__(self, key):
        contained = False
        if self._local_parser:
            if not contained:
                contained = self._local_parser.get(self._name, key, fallback=None) is not None
            if not contained:
                contained = self._local_parser.get("default", key, fallback=None) is not None
        if self._default_parser:
            if not contained:
                contained = self._default_parser.get(self._name, key, fallback=None) is not None
            if not contained:
                contained = self._default_parser.get("default", key, fallback=None) is not None
        return contained


class ConfigurationFile(object):
    _default_parser = None
    _local_parser = None
    _name = None

    def __init__(self, name, default_parser, local_parser):
        self._default_parser = default_parser
        self._local_parser = local_parser
        self._name = name

    def __getitem__(self, stanza_name):
        if not self.__contains__(stanza_name):
            raise KeyError("stanza '%s' not found in '%s'" % (
                stanza_name,
                self._name,
            ))
        return ConfigurationStanza(
            self,
            stanza_name,
            self._default_parser,
            self._local_parser,
        )

    def __contains__(self, stanza_name):
        if self._default_parser.has_section(stanza_name):
            return True
        if self._local_parser:
            if self._local_parser.has_section(stanza_name):
                return True
        return False

    def __iter__(self):
        names = set()
        if self._local_parser:
            for n in self._local_parser.sections():
                names.add(n)
        for n in self._default_parser.sections():
            names.add(n)
        for n in names:
            yield self[n]


class Configurations(object):
    service = None
    files = None

    def __init__(self, service):
        self.service = service
        self.files = {}

    def parse(self, path):
        if os.path.exists(path):
            parser = ConfigParser(
                delimiters=('='),
                strict=False,
                default_section="__default__",
            )
            # encoding=encoding
            with open(path, "r") as fp:
                content = fp.read()
            content = content.replace("\\\n", "")
            parser.read_string(content)
            # parser.read(path)
            return parser
        else:
            return None

    def __getitem__(self, key):
        if key in self.files:
            return self.files[key]
        if not key in self:
            raise KeyError("%s not in %s and not in %s" % (key, self.service.default_conf_path, self.service.local_conf_path))
        default_path = os.path.join(self.service.default_conf_path, key + ".conf")
        default_parser = self.parse(default_path)
        local_path = os.path.join(self.service.local_conf_path, key + ".conf")
        local_parser = self.parse(local_path)
        f = ConfigurationFile(key, default_parser, local_parser)
        self.files[key] = f
        return f

    def __contains__(self, key):
        if key in self.files:
            return True
        default_path = os.path.join(self.service.default_conf_path, key + ".conf")
        if os.path.exists(default_path):
            return True
        local_path = os.path.join(self.service.local_conf_path, key + ".conf")
        if os.path.exists(local_path):
            return True
        return False


class Service(object):
    default_conf_path = None
    local_conf_path = None
    _confs = None

    def __init__(self, app_path):
        self.default_conf_path = os.path.join(app_path, "default")
        self.local_conf_path = os.path.join(app_path, "local")
        self._confs = Configurations(self)

    @property
    def confs(self):
        return self._confs
