import re

from json.encoder import encode_basestring_ascii as json_encode_string


_arguments_re = re.compile(r"""
    ^\s*
    (?P<options>     # Match a leading set of name/value pairs
        (?:
            (?:(?=\w)[^\d]\w*)                         # name
            \s*=\s*                                    # =
            (?:"(?:\\.|""|[^"])*"|(?:\\.|[^\s"])+)\s*  # value
        )*
    )\s*
    (?P<fieldnames>  # Match a trailing set of field names
        (?:
            (?:"(?:\\.|""|[^"])*"|(?:\\.|[^\s"])+)\s*
        )*
    )\s*$
    """, re.VERBOSE | re.UNICODE)

_options_re = re.compile(r"""
    # Captures a set of name/value pairs when used with re.finditer
    (?P<name>(?:(?=\w)[^\d]\w*))                   # name
    \s*=\s*                                        # =
    (?P<value>"(?:\\.|""|[^"])*"|(?:\\.|[^\s"])+)  # value
    """, re.VERBOSE | re.UNICODE)


def parse_options(args, valid_options, ignore_unknown=False):
    valid_options = set(valid_options)
    options = {}
    for a in args:
        i = a.find("=")
        if i >= 0:
            name = a[:i]
            value = a[i + 1:]
            if name not in valid_options and not ignore_unknown:
                raise ValueError(
                    'Unrecognized command option: {}={}'.format(name, json_encode_string(value)))
            options[name] = unquote(value)
    # | compute <mathod> using <algorithm> in <environment> for <target_field> from <feature_fields> as <renamed_target_field>
    return options


_escaped_character_re = re.compile(r'(\\.|""|[\\"])')


def unquote(string):
    """ Removes quotes from a quoted string.

    Splunk search command quote rules are applied. The enclosing double-quotes, if present, are removed. Escaped
    double-quotes ('\"' or '""') are replaced by a single double-quote ('"').

    **NOTE**

    We are not using a json.JSONDecoder because Splunk quote rules are different than JSON quote rules. A
    json.JSONDecoder does not recognize a pair of double-quotes ('""') as an escaped quote ('"') and will
    decode single-quoted strings ("'") in addition to double-quoted ('"') strings.

    """
    if len(string) == 0:
        return ''

    if string[0] == '"':
        if len(string) == 1 or string[-1] != '"':
            raise SyntaxError('Poorly formed string literal: ' + string)
        string = string[1:-1]

    if len(string) == 0:
        return ''

    def replace(match):
        value = match.group(0)
        if value == '""':
            return '"'
        if len(value) < 2:
            raise SyntaxError('Poorly formed string literal: ' + string)
        return value[1]

    result = re.sub(_escaped_character_re, replace, string)
    return result
