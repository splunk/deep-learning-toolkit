import re


class Spec(object):
    def __init__(self, stanzas=[]):
        self.stanzas = stanzas

    def add_stanza(self, stanza):
        self.stanzas.append(stanza)

    def get_stanza_for_name(self, name):
        for s in reversed(self.stanzas):
            if s.match_name(name):
                return s
        return None


placeholder_re = re.compile(r"<[^>]+>")


class Stanza(object):
    def __init__(self, name_pattern):
        self.name_pattern = name_pattern
        name_re_string = re.escape(name_pattern)
        for placeholder in placeholder_re.findall(name_pattern):
            name_re_string = name_re_string.replace(placeholder, ".+")
        self.name_re = re.compile(name_re_string)
        self.attributes = dict()

    def match_name(self, name):
        #raise Exception("name: %s" % self.name_re)
        if self.name_re.match(name):
            return True
        return False

    def add_attribute(self, attribute):
        self.attributes[attribute.name] = attribute

    def get_attribute(self, name):
        if name in self.attributes:
            return self.attributes[name]
        return None


class Attribute(object):
    def __init__(self, name, value_spec, is_required, docs):
        self.name = name
        self.value_spec = value_spec
        self.is_required = is_required
        self.docs = docs


attribute_re = re.compile(r"^(\w+)\s*=\s*(.*)\s*$")


def parse_attribute(lines):
    first_line = lines[0]
    match = attribute_re.match(first_line)
    if not match:
        raise Exception("invalid attribute line: %s" % first_line)
    name = match.group(1)
    value_spec = match.group(2)
    docs = []
    is_required = False
    for line in lines[1:]:
        if not line.startswith("*"):
            continue
        line = line.lstrip("*")
        line = line.lstrip()
        if not line:
            continue
        if line.lower().startswith("required"):
            is_required = True
        docs.append(line)
    a = Attribute(
        name=name,
        value_spec=value_spec,
        is_required=is_required,
        docs=docs,
    )
    return a


def parse_stanza(lines):
    first_line = lines[0]
    stanza_name = first_line[1:-1]
    stanza = Stanza(
        name_pattern=stanza_name,
    )
    current_attribute_lines = []
    for line in lines[1:]:
        match = attribute_re.match(line)
        if match:
            if current_attribute_lines:
                stanza.add_attribute(parse_attribute(current_attribute_lines))
            current_attribute_lines = []
        current_attribute_lines.append(line)
    if current_attribute_lines:
        stanza.add_attribute(parse_attribute(current_attribute_lines))
    return stanza


def parse(spec_string):

    spec = Spec()

    current_stanza_lines = []

    for line in spec_string.splitlines():
        line = line.strip()
        if line.startswith("#"):
            continue
        if line == "":
            continue
        if line == "":
            continue
        is_stanza_name = line.startswith("[") and line.endswith("]")
        if is_stanza_name:
            if current_stanza_lines:
                spec.add_stanza(parse_stanza(current_stanza_lines))
            current_stanza_lines = []
        current_stanza_lines.append(line)

    if current_stanza_lines:
        spec.add_stanza(parse_stanza(current_stanza_lines))

    return spec
