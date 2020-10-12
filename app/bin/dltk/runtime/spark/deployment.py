

import urllib
import http
from dltk.core import deployment
from dltk.connector.kubernetes import KubernetesDeployment
from kubernetes import client as kubernetes_client
from dltk.core.deployment import status as deployment_status, UserFriendlyError
import logging
import opentracing
import json
import time
import socket
import io

from . import application as spark_application

__all__ = ["SparkDeployment"]


class SparkDeployment(KubernetesDeployment):

    def __init__(self, splunk, stanza):
        super().__init__(
            splunk,
            stanza,
            strategy_name="9",
            custom_object_types=[
                (spark_application.crd_group, spark_application.crd_version, spark_application.crd_plural)
            ]
        )

    def deploy(self):
        super().deploy()
        if self.is_disabled:
            self.runtime_status = {
                "relay_url": "",
            }
        else:
            # https://github.com/GoogleCloudPlatform/spark-on-k8s-operator/blob/master/docs/user-guide.md#python-support
            editor_deployment = self.deploy_editor_deployment()
            self.wait_for_deployment(editor_deployment)
            self.expose_editor()
            self.wait_for_ingress("editor", test_path="_dltk/ping")
            self.sync_source_code()
            editor_base_url = self.get_ingress_url("editor")
            #raise dltk_errors.Error("editor url: %s" % editor_base_url)
            notebook_url = urllib.parse.urljoin(editor_base_url, "notebooks/Algo.ipynb")
            self.editor_url = notebook_url
            self.collect_garbage()

    def collect_garbage(self):
        jobs_done = {}

        def filter_done_search_objects(kind, labels):
            if not "search_id" in labels:
                return False
            search_id = labels["search_id"]
            #logging.info("search_id: %s" % search_id)
            if not search_id:
                return True
            if search_id in jobs_done:
                return jobs_done[search_id]
            search_done = True

            # if search_id in self.splunk.jobs:
            #    job = self.splunk.jobs[search_id]
            # else:

            job = None
            for j in self.splunk.jobs:
                test = self.generate_label_value(j.name)
                if search_id == test:
                    job = j
                    break

            if job:
                is_done = job.is_done() or job.content["isFinalized"] == "1" or job.content["isFailed"] == "1"
                logging.info("job %s is done: %s" % (search_id, is_done))
                if not is_done:
                    #logging.info("%s" % job.content)
                    pass
                search_done = is_done
            jobs_done[search_id] = search_done
            return search_done

        self.delete_objects(
            only_outdated=False,
            include_services=True,
            include_workloads=True,
            include_volumes=True,
            include_secrets=True,
            include_ingresses=True,
            additional_label_selector={
                # "search_id"
            },
            delete_filter=filter_done_search_objects
        )

    def expose_editor(self):
        return self.expose_pods(
            "editor",
            pod_port=8888,
            pod_labels={
                "component": "editor",
            },
            labels={
                "component": "editor",
            },
            rewrite_path=False,
        )

    def deploy_editor_deployment(self):
        return super().deploy_deployment(
            name_suffix="editor",
            image=self.get_param("editor_image"),
            cpu_request=self.get_param("editor_cpu_request"),
            cpu_limit=self.get_param("editor_cpu_limit"),
            memory_mb=int(self.get_param("editor_memory_mb")),
            ports=[
                kubernetes_client.V1ContainerPort(
                    container_port=8888,
                    name="web",
                    protocol="TCP"
                ),
            ],
            deployment_labels={
                "component": "editor",
            },
            pod_labels={
                "component": "editor",
            },
            env=[
                kubernetes_client.V1EnvVar(
                    name="JUPYTER_BASE_URL_PATH",
                    value=self.get_ingress_path("editor"),
                )
            ]
        )

    def sync_source_code(self):
        notebook_url = urllib.parse.urljoin(
            self.get_ingress_url("editor"),
            "_dltk/notebook"
        )
        try:
            download_request = urllib.request.Request(notebook_url, method="GET")
            download_response = urllib.request.urlopen(download_request)
            notebook_version = int(download_response.getheader("X-Notebook-Version"))
            if notebook_version is None:
                raise Exception("Did not receive notebook version")
            notebook_code = download_response.read().decode()
        except http.client.RemoteDisconnected as e:
            if self.status == deployment_status.STATUS_DEPLOYING:
                raise deployment_status.StillDeploying("Waiting for connection")
            raise deployment_status.DeploymentError("Could not connect: %s" % e)
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise UserFriendlyError("failed downloading notebook source: %s" % e.code)
            notebook_version = -1
            notebook_code = ""
        if notebook_version > self.algorithm.source_code_version:
            self.algorithm.update_source_code(
                notebook_code,
                notebook_version,
            )
            logging.info("Received and stored updated source code (version %s)" % notebook_version)
        if notebook_version < self.algorithm.source_code_version:
            notebook_data = self.algorithm.source_code.encode()
            #raise Exception("notebook_data: %s" % self.algorithm.source_code)
            upload_request = urllib.request.Request(
                notebook_url,
                data=notebook_data,
                method="PUT",
                headers={
                    "X-Notebook-Version": self.algorithm.source_code_version,
                }
            )
            try:
                urllib.request.urlopen(upload_request)
            except urllib.error.HTTPError as e:
                raise UserFriendlyError("error sending new source code to runtime: %s" % e)
            logging.info("Sent source code (version %s)" % self.algorithm.source_code_version)
