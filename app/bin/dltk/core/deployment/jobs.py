import traceback

from dltk.core import jobs
from dltk.core.logging import get_logger

from . get import get, get_all, exists
from . import stanza_name
from . import status
from . conf import conf_name
from . import errors

job_category_deploy = "deploy"


def schedule(splunk, deployment, delete=False, enable_schedule=None):
    return jobs.schedule_repeatedly(
        splunk,
        job_category_deploy,
        deployment.name,
        "dltk.core.deployment.run",
        enable_schedule,
        deployment.algorithm_name,
        deployment.environment_name,
        delete
    )


def trigger(splunk, deployment, delete=False, status=None, enable_schedule=None):
    jobs.stop(
        splunk,
        job_category_deploy,
        deployment.name,
        False
    )
    if status:
        deployment.status = status
        deployment.status_message = ""
    return schedule(splunk, deployment, delete, enable_schedule=enable_schedule)


def run(splunk, algorithm_name, environment_name, delete=False):
    from dltk.core import model
    deployment = get(splunk, algorithm_name, environment_name)
    deployment.logger.info("executing deployment job for algorithm %s in environment %s (guid=%s,delete=%s) ..." % (
        algorithm_name,
        environment_name,
        deployment.guid,
        delete,
    ))
    try:
        if delete:
            deployment.undeploy()
            for model in model.get_all_in_deployment(splunk, algorithm_name, environment_name):
                deployment.logger.info("deleting model '%s' ..." % (model.name))
                model.delete(splunk, model.name, False)
            deployment_name = stanza_name.format(algorithm_name, environment_name)
            splunk.confs[conf_name].delete(deployment_name)
            raise jobs.Stop()
        deployment.deploy()
        if deployment.is_disabled:
            deployment.editor_url = ""
            raise status.Disabled()
        model_names = set(deployment.list_models())
        for model_name in model_names:
            if not model.exists(splunk, model_name):
                deployment.logger.info("deleting model '%s' as it's not in configured anymore" % (model_name))
                deployment.delete_model(model_name)
        for model in model.get_all_in_deployment(splunk, algorithm_name, environment_name):
            if model.name not in model_names:
                deployment.logger.info("creating model '%s' as it's not deployed yet" % model.name)
                deployment.create_model(model)
        raise status.Deployed()
    except status.DeploymentStatus as e:
        if e.message:
            deployment.logger.info("deployment status: %s (%s)" % (e.status, e.message))
        else:
            deployment.logger.info("deployment status: %s" % (e.status))
        deployment.status = e.status
        deployment.status_message = e.message
        deployment.logger.error("deployment job (delete=%s) completed with status: %s" % (delete, deployment.status))
    except jobs.Stop:
        deployment.logger.error("deployment job (delete=%s) stopped" % delete)
        raise
    except errors.UserFriendlyError as e:
        #err_msg = traceback.format_exc()
        deployment.logger.error("deployment job (delete=%s) failed: %s" % (delete, e))
        deployment.status = status.STATUS_ERROR
        deployment.status_message = '%s' % (e)
    except Exception as e:
        err_msg = traceback.format_exc()
        deployment.logger.error("deployment job (delete=%s) failed: %s" % (delete, err_msg))
        deployment.status = status.STATUS_ERROR
        deployment.status_message = '%s: %s' % (e, err_msg)


# update


def update(splunk, enable_schedule=None):
    logger = get_logger()
    for deployment in get_all(splunk):
        if not jobs.exists(splunk, job_category_deploy, deployment.name):
            schedule(splunk, deployment, enable_schedule=enable_schedule)
            deployment.logger.info("created deploy job for \"%s\"" % (deployment.name))
    for deployment_stanza_name in jobs.get_jobs(splunk, job_category_deploy):
        algorithm_name, environment_name = stanza_name.parse(deployment_stanza_name)
        if not exists(splunk, algorithm_name, environment_name):
            logger.warning("deployment stanza \"%s\" unknown -> killing job ..." % deployment_stanza_name)
            jobs.stop(splunk, job_category_deploy, deployment_stanza_name, False)
