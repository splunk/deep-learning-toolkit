

__all__ = [
    "name",
    "get_conf",
]


name = "dltk_environments"


def get_conf(splunk):
    try:
        conf = splunk.confs[name]
    except KeyError:
        raise Exception("conf %s not found (ns=%s)" % (
            name,
            splunk.namespace,
        ))
    return conf
