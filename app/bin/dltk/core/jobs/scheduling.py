import json

from . config import *
from . search_name import format as format_search_name


def schedule_once(splunk, category, job_name, handler, enable_schedule, *argv):
    repeat_on_success = False
    repeat_on_error = True
    return schedule(
        splunk,
        category,
        job_name,
        repeat_on_success,
        repeat_on_error,
        handler,
        enable_schedule,
        *argv
    )


def schedule_repeatedly(splunk, category, job_name, handler, enable_schedule, *argv):
    repeat_on_success = True
    repeat_on_error = True
    return schedule(
        splunk,
        category,
        job_name,
        repeat_on_success,
        repeat_on_error,
        handler,
        enable_schedule,
        *argv
    )


def schedule(splunk, category, job_name, repeat_on_success, repeat_on_error, handler, enable_schedule, *argv):
    if enable_schedule is None:
        enable_schedule = is_schedule_enabled(splunk)
    search_name = format_search_name(category, job_name)
    if search_name in splunk.saved_searches:
        splunk.saved_searches.delete(search_name)
    search = splunk.saved_searches.create(
        name=search_name,
        search="| job search_name=\"%s\" handler=\"%s\" argv=\"%s\" repeat_on_success=\"%s\" repeat_on_error=\"%s\"" % (
            search_name,
            handler,
            json.dumps(argv).replace("\"", "\\\""),
            repeat_on_success,
            repeat_on_error,
        ),
        **{
            "cron_schedule": "* * * * *",
            "is_scheduled": 1 if enable_schedule else 0,
            "schedule_window": "auto",
            "dispatch.auto_cancel": 0,
            "dispatch.auto_pause": 0,
            "dispatch.max_time": 0,
        }
    )
    if enable_schedule:
        search.dispatch(
            **{
                "dispatch.now": True,
                "force_dispatch": False,
            }
        )
    return search_name, enable_schedule


def stop(splunk, category, job_name, raise_if_not_exists=True):
    search_name = format_search_name(category, job_name)
    try:
        splunk.saved_searches.delete(search_name)
    except KeyError:
        if raise_if_not_exists:
            raise


__all__ = ["schedule", "stop", "schedule_repeatedly", "schedule_once"]
