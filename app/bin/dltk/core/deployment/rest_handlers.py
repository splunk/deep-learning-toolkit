from urllib.parse import parse_qs, unquote
import os

from dltk.core.rest import BaseRestHandler

from dltk.core import algorithm
from dltk.core import deployment
from dltk.core import environment
from dltk.core import runtime
from dltk.core import is_truthy

from . core import *
from . get import *
from . jobs import trigger
from . import status
from . params import get_default_param
from dltk.core import get_label_for_name

__all__ = [
    "DeploymentsHandler",
    "DeploymentParamsHandler"
]


class DeploymentParamsHandler(BaseRestHandler):
    def handle_GET(self):
        algorithm_name = self.get_param("algorithm")
        runtime_name = self.get_param("runtime")
        environment_name = self.get_param("environment")
        if algorithm_name and environment_name:
            d = deployment.get(self.splunk, algorithm_name, environment_name)
            a = d.algorithm
            e = d.environment
            r = a.runtime
            def get_default(name): return get_default_param(name, e, algorithm=a)
            def get_value(name): return d.get_param(name, inherit=False)
        if runtime_name and environment_name:
            e = environment.get(self.splunk, environment_name)
            r = runtime.get(self.splunk, runtime_name)
            def get_default(name): return get_default_param(name, e, runtime=r)
            def get_value(_): return None
        params = [{
            "name": name,
            "label": get_label_for_name(name),
            "default": get_default(name),
            "value": get_value(name),
            "type": "text",  # "picker" "text",
            "mandatory": False,
            "important": True,  # True if name == "executor_instance_count" else False,
        } for name in r.deployment_param_names]
        self.send_entries(params)

    def handle_PUT(self):
        algorithm_name = self.get_param("algorithm")
        environment_name = self.get_param("environment")
        if not algorithm_name:
            raise Exception("algorithm missing")
        if not environment_name:
            raise Exception("environment missing")
        d = deployment.get(self.splunk, algorithm_name, environment_name)
        if d is None:
            raise Exception("algorithm_name=%s, environment_name=%s" % (algorithm_name, environment_name))
        r = d.algorithm.runtime
        changed_value = False
        for name in r.deployment_param_names:
            value = self.get_param(name)
            if value is not None:
                d.set_param(name, value)
                changed_value = True
        if changed_value:
            d.trigger_deploying()


class DeploymentsHandler(BaseRestHandler):

    def handle_GET(self):
        algorithm_name = self.get_param("algorithm")
        environment_name = self.get_param("environment")
        if environment_name and algorithm_name:
            deployments = [get(self.splunk, algorithm_name, environment_name)]
        if algorithm_name:
            deployments = get_all_for_algorithm(self.splunk, algorithm_name)
        else:
            deployments = get_all(self.splunk)
        results = []
        for deployment in deployments:
            results.append({
                "algorithm": deployment.algorithm_name,
                "environment": deployment.environment_name,
                "status": deployment.status,
                "status_message": deployment.status_message,
                "editable": deployment.editable,
                "editor_url": deployment.editor_url,
                "disabled": deployment.is_disabled,
                "restart_required": deployment.restart_required,
            })
        self.send_entries(results)

    def handle_POST(self):
        algorithm_name = self.get_param("algorithm")
        environment_name = self.get_param("environment")
        if not algorithm_name:
            raise Exception("missing algorithm")
        if not environment_name:
            raise Exception("missing environment")
        a = algorithm.get(self.splunk, algorithm_name)
        e = environment.get(self.splunk, environment_name)
        enable_schedule = self.get_param("enable_schedule")
        if enable_schedule:
            enable_schedule = is_truthy(enable_schedule)
        else:
            enable_schedule = None
        deployment_params = {}
        for name in a.runtime.deployment_param_names:
            value = self.get_param(name)
            if value is not None:
                deployment_params[name] = value
        create(
            self.splunk,
            a.name,
            e.name,
            enable_schedule=enable_schedule,
            params=deployment_params,
        )

    def handle_PUT(self):
        enable_schedule = self.get_param("enable_schedule")
        if enable_schedule is not None:
            enable_schedule = is_truthy(enable_schedule)
        algorithm_name = self.get_param("algorithm")
        if not algorithm_name:
            raise Exception("algorithm missing")
        environment_name = self.get_param("environment")
        if not environment_name:
            raise Exception("environment missing")
        d = deployment.get(self.splunk, algorithm_name, environment_name)
        restart_required = self.get_param("restart_required")
        if restart_required is not None:
            d.restart_required = is_truthy(restart_required)
        editable = self.get_param("editable")
        if editable is not None:
            d.editable = is_truthy(editable)
        is_disabled = self.get_param("disabled")
        if is_disabled is not None:
            d.is_disabled = is_truthy(is_disabled)
        d.trigger_deploying(
            enable_schedule=enable_schedule,
        )

    def handle_DELETE(self):
        query = self.request['query']
        algorithm_name = query.get("algorithm", "")
        if not algorithm_name:
            raise Exception("missing algorithm")
        environment_name = query.get("environment", "")
        if not environment_name:
            raise Exception("missing environment")
        d = get(self.splunk, algorithm_name, environment_name)
        if not d:
            self.response.setStatus(404)
            return
        payload = self.request["query"]
        enable_schedule = query.get("enable_schedule", "")
        if enable_schedule:
            enable_schedule = is_truthy(enable_schedule)
        else:
            enable_schedule = None
        delete(self.splunk, d, enable_schedule=enable_schedule)

#    def handle_POST(self):
#        deployment = self.get_deployment_from_path()
#        if not deployment:
#            self.response.setStatus(404)
#            return
#        payload = parse_qs(self.request['payload'])
#        if "disabled" in payload:
#            disabled = payload["disabled"][0]
#            deployment.is_disabled = disabled
#        if "editable" in payload:
#            editable = payload["editable"][0]
#            deployment.editable = editable
#        if "restart_required" in payload:
#            restart_required = payload["restart_required"][0]
#            deployment.restart_required = restart_required
#        if "enable_schedule" in payload:
#            enable_schedule = is_truthy(payload["enable_schedule"][0])
#        else:
#            enable_schedule = None
#        prefix = "param."
#        params = {}
#        for key, value in payload.items():
#            if key.startswith(prefix):
#                name = key[len(prefix):]
#                if len(value) == 0:
#                    continue
#                params[name] = value[0]
#        deployment.update_params(params)
#        trigger(
#            self.splunk,
#            deployment,
#            status=status.STATUS_DEPLOYING,
#            enable_schedule=enable_schedule,
#        )
