

from dltk.core import is_truthy


conf_name = "dltk_jobs"


def is_schedule_enabled(splunk):
    return is_truthy(splunk.confs[conf_name]["general"]["enableSched"])


__all__ = ["is_schedule_enabled"]
