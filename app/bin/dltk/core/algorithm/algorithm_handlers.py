import os
from urllib.parse import parse_qs, unquote

from dltk.core.rest import BaseRestHandler
from . import algorithm_api
from . import method_api

from dltk.core import is_truthy
from dltk.core import deployment
from dltk.core import runtime


__all__ = ["AlgorithmsHandler", "AlgorithmParamsHandler"]


class AlgorithmParamsHandler(BaseRestHandler):
    def handle_GET(self):
        algorithm_name = self.get_param("algorithm")
        runtime_name = self.get_param("runtime")
        include_deployments = is_truthy(self.get_param("include_deployments"))
        if include_deployments and not algorithm_name:
            raise Exception("include_deployments only works with algorithm_name")
        if algorithm_name:
            a = algorithm_api.get(self.splunk, algorithm_name)
            r = a.runtime
            get_default = r.get_param
            def get_value(name): return a.get_param(name, inherit=False)
        elif runtime_name:
            r = runtime.get(self.splunk, runtime_name)
            get_default = r.get_param
            def get_value(_): return None
        else:
            raise Exception("requires algorithm or runtime")
        params = []
        params.extend([{
            "name": name,
            "default": get_default(name),
            "value": get_value(name),
            "type": "text",  # "picker" "text",
            "mandatory": False,
        } for name in r.algorithm_param_names])
        if include_deployments:
            for d in deployment.get_all_for_algorithm(self.splunk, algorithm_name):
                e = d.environment
                params.extend([{
                    "environment": e.name,
                    "name": name,
                    "default": deployment.get_default_param(name, e, algorithm=a),
                    "value": d.get_param(name, inherit=False),
                    "type": "text",  # "picker" "text",
                    "mandatory": False,
                } for name in r.deployment_param_names])
        self.send_entries(params)

    def handle_PUT(self):
        algorithm_name = self.get_param("algorithm")
        runtime_name = self.get_param("runtime")
        if algorithm_name:
            a = algorithm_api.get(self.splunk, algorithm_name)
            r = a.runtime

            def set_value(name, value):
                return a.set_param(name, value)
        elif runtime_name:
            r = runtime.get(self.splunk, runtime_name)

            def set_value(name, value):
                old = r.get_param(name)
                r.set_param(name, value)
        else:
            raise Exception("requires algorithm or runtime")
        changed_value = False
        for name in r.algorithm_param_names:
            value = self.get_param(name)
            if value is not None:
                set_value(name, value)
                changed_value = True
        if changed_value and algorithm_name:
            for d in a.deployments:
                d.trigger_deploying()


class AlgorithmsHandler(BaseRestHandler):
    def handle_GET(self):
        deployed_only = is_truthy(self.get_param("deployed_only", "0"))
        results = []
        for algorithm in algorithm_api.get_all(self.splunk):
            info = {
                "name": algorithm.name,
                "description": algorithm.description,
                "runtime": algorithm.runtime_name,
                "category": algorithm.category,
            }
            status = []
            editor = []
            for d in deployment.get_all_for_algorithm(self.splunk, algorithm.name):
                status.append(d.status)
                editor.append(d.editor_url)
            info["status"] = status
            info["editor"] = editor
            info["can_be_deleted"] = True
            if deployed_only and not len(status) > 0:
                continue
            results.append(info)
        self.send_entries(results)

    def handle_POST(self):
        algorithm_name = self.get_param("name")
        runtime_name = self.get_param("runtime")
        if not algorithm_name:
            raise Exception("missing name")
        if algorithm_api.exists(self.splunk, algorithm_name):
            raise Exception("algo already exist")
        r = runtime.get(self.splunk, runtime_name)
        a = algorithm_api.create(self.splunk, algorithm_name, r.name)
        source_code = self.get_param("source_code")
        if source_code:
            a.update_source_code(
                code=source_code,
            )
        #runtime_name = self.get_param("runtime")

    def handle_DELETE(self):
        query = self.request['query']
        algorithm_name = query.get("name", "")
        if not algorithm_name:
            raise Exception("missing name")
        algorithm_api.delete(self.splunk, algorithm_name)
