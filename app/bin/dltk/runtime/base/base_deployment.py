import urllib
import http
from dltk.core import deployment
from dltk.core import execution
from dltk.connector.kubernetes import KubernetesDeployment
from kubernetes import client as kubernetes_client
from dltk.core.deployment import status as deployment_status, UserFriendlyError
import logging


__all__ = ["BaseDeployment"]


class BaseDeployment(KubernetesDeployment):

    def __init__(self, splunk, stanza):
        super().__init__(splunk, stanza, "9")

    def deploy(self):
        super().deploy()
        if self.is_disabled:
            self.runtime_status = {
                "api_url": "",
            }
        else:
            models_volume_claim = self.deploy_base_volume_claim()
            d = self.deploy_base_deployment(models_volume_claim)
            self.wait_for_deployment(d)

            if self.environment.ingress_mode == "node-port":
                # service = self.deploy_base_service(
                #    service_type="NodePort"
                # )
                # self.wait_for_service(service)
                #hostname = self.get_service_hostname(service)
                #nodeport_jupyter = self.get_service_nodeport(service, "jupyter")
                #self.editor_url = "http://%s:%s" % (hostname, nodeport_jupyter)
                # self.runtime_status = {
                #    "api": "http://%s:%s" % (hostname, self.get_service_nodeport(service, "api")),
                #    # "sparkui": "http://%s:%s" % (hostname, self.get_service_nodeport(service, "sparkui")),
                #    "tensorboard": "http://%s:%s" % (hostname, self.get_service_nodeport(service, "tensorboard")),
                # }
                pass

            elif self.environment.ingress_mode == "ingress":
                # create service
                service = self.deploy_base_service()

                # create ingress for Jupyter Lab editor
                ingress_editor = self.deploy_ingress(
                    service,
                    port=80,
                    title="editor",
                    ingress_labels={"component": "editor"},
                    rewrite_path=False,
                )
                self.editor_url = self.get_ingress_url("editor")

                # create ingress for flask api endpoint
                ingress_api = self.deploy_ingress(
                    service,
                    port=5000,
                    title="api",
                    ingress_labels={"component": "api"},
                    rewrite_path=True,
                )
                self.api_url = self.get_ingress_url("api")
                self.runtime_status = {
                    "api_url": self.api_url,
                }

                self.sync_source_code(self.api_url)
                self.sync_deployment_code(self.api_url)

            else:
                raise UserFriendlyError("Unsupported ingress mode %s. Only node-port is allowed." % self.environment.ingress_mode)

            # self.runtime_status = {
            #     "hostname": hostname,
            # }
            # self.editor_url = "http://%s:80" % hostname
            # self.sync_source_code(service)
            # self.sync_deployment_code(service)

    def deploy_base_volume_claim(self):
        return self.deploy_volume_claim(
            labels={
                "content": "models",
            }
        )

    def deploy_base_service(self, service_type=None):
        return self.deploy_service(
            ports=[
                kubernetes_client.V1ServicePort(
                    name="api",
                    port=5000,
                    protocol="TCP",
                    target_port=5000,
                ),
                kubernetes_client.V1ServicePort(
                    name="jupyter",
                    port=80,
                    protocol="TCP",
                    target_port=8888,
                ),
                kubernetes_client.V1ServicePort(
                    name="tensorboard",
                    port=6006,
                    protocol="TCP",
                    target_port=6006,
                ),
            ],
            service_type=service_type
        )

    def deploy_base_deployment(self, models_volume_claim):
        return self.deploy_deployment(
            self.get_param("image"),
            cpu_count=int(self.get_param("cpu_count")),
            memory_mb=int(self.get_param("memory_mb")),
            ports=[
                kubernetes_client.V1ContainerPort(
                    container_port=5000,
                    name="api",
                    protocol="TCP"
                ),
                kubernetes_client.V1ContainerPort(
                    container_port=8888,
                    name="jupyter",
                    protocol="TCP"
                ),
                kubernetes_client.V1ContainerPort(
                    container_port=6006,
                    name="tensorboard",
                    protocol="TCP"
                ),
                # kubernetes_client.V1ContainerPort(
                #     container_port=4040,
                #     name="sparkui",
                #     protocol="TCP"
                # ),
            ],
            env=[
                kubernetes_client.V1EnvVar(
                    name="JUPYTER_BASE_URL_PATH",
                    value=self.get_ingress_path("editor"),
                )
            ],
            volumes=[
                kubernetes_client.V1Volume(
                    name="data",
                    persistent_volume_claim=kubernetes_client.V1PersistentVolumeClaimVolumeSource(
                        claim_name=models_volume_claim.metadata.name,
                    )
                ),
            ],
            volume_mounts=[
                kubernetes_client.V1VolumeMount(
                    mount_path="/srv",
                    name="data",
                ),
            ],
            run_as_user=1001,
            fs_group=0
        )

    def sync_source_code(self, url):
        url = url + "/notebook"
        try:
            download_request = urllib.request.Request(url, method="GET")
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
                raise Exception("downloading notebook source failed with %s" % e.code)
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
            upload_request = urllib.request.Request(
                url,
                data=notebook_data,
                method="PUT",
                headers={
                    "X-Notebook-Version": self.algorithm.source_code_version,
                    "Content-Type": "application/octet-stream",
                }
            )
            urllib.request.urlopen(upload_request)
            logging.info("Sent source code (version %s)" % self.algorithm.source_code_version)

    def sync_deployment_code(self, url):
        url = url + "/code"
        try:
            download_request = urllib.request.Request(url, method="GET")
            download_response = urllib.request.urlopen(download_request)
            version = int(download_response.getheader("X-Code-Version"))
            if version is None:
                raise Exception("Did not receive code version")
            deployment_code = download_response.read().decode()
        except http.client.RemoteDisconnected as e:
            if self.status == deployment_status.STATUS_DEPLOYING:
                raise deployment_status.StillDeploying("Waiting for connection")
            raise deployment_status.DeploymentError("Could not connect: %s" % e)
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise Exception("downloading code deployment failed with %s" % e.code)
            version = -1
            deployment_code = ""
        if version > self.algorithm.deployment_code_version:
            self.algorithm.update_deployment_code(
                deployment_code,
                version,
            )
            logging.info("Received and stored updated deployment code (version %s)" % version)
        if version < self.algorithm.deployment_code_version:
            data = self.algorithm.deployment_code.encode()
            upload_request = urllib.request.Request(
                url,
                data=data,
                method="PUT",
                headers={
                    "X-Code-Version": self.algorithm.deployment_code_version,
                    "Content-Type": "application/octet-stream",
                }
            )
            urllib.request.urlopen(upload_request)
            logging.info("Sent deployment code (version %s)" % self.algorithm.deployment_code_version)
