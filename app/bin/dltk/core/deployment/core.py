import uuid
import traceback
from splunklib.binding import HTTPError

from . import status
from . jobs import schedule, trigger
from . get import *
from . import stanza_name

from .conf import conf_name

__all__ = [
    "create",
    "delete",
]


def create(splunk, algorithm_name, environment_name, enable_schedule=None, params={}):
    deploymane_name = stanza_name.format(algorithm_name, environment_name)
    stanza = splunk.confs[conf_name].create(deploymane_name)
    guid = str(uuid.uuid4())[:8]
    stanza.submit({
        **{
            "guid": guid,
        },
        **params,
    })
    stanza.refresh()
    deployment = get(splunk, algorithm_name, environment_name)
    deployment.status = status.STATUS_DEPLOYING
    deployment.status_message = ""
    schedule(splunk, deployment, enable_schedule=enable_schedule)
    return deployment


def delete(splunk, deployment, enable_schedule=None):
    try:
        trigger(
            splunk,
            deployment,
            delete=True,
            status=status.STATUS_UNDEPLOYING,
            enable_schedule=enable_schedule,
        )
        return deployment
    except HTTPError as e:
        if e.status == 404:
            return
        err_msg = traceback.format_exc()
        raise Exception("HTTPError: %s" % err_msg)
