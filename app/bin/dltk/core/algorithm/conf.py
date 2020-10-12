

__all__ = ["name", "get"]


name = "dltk_algorithms"


def get(splunk):
    return splunk.confs[name]
