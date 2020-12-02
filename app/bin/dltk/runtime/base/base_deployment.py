import urllib
from urllib.parse import urlparse
import http
from dltk.core import execution, deployment, is_truthy
from dltk.connector.kubernetes import KubernetesDeployment
from kubernetes import client as kubernetes_client
from dltk.core.deployment import status as deployment_status, UserFriendlyError


__all__ = ["BaseDeployment"]


class BaseDeployment(KubernetesDeployment):

    @property
    def store_models_in_volume(self):
        return is_truthy(self.get_param("store_models_in_volume"))

    @property
    def cpu_count(self):
        return int(self.get_param("cpu_count"))

    @property
    def gpu_request(self):
        value = self.get_param("gpu_request")
        if not value:
            return None
        return int(value)

    def __init__(self, splunk, stanza):
        super().__init__(splunk, stanza, "11")

    def deploy(self):
        super().deploy()
        if self.is_disabled:
            self.runtime_status = {
                "api_url": "",
            }
        else:
            if self.store_models_in_volume:
                models_volume_claim = self.deploy_base_volume_claim()
            else:
                models_volume_claim = None
            d = self.deploy_base_deployment(models_volume_claim)
            self.wait_for_deployment(d)

            if self.environment.ingress_mode == "node-port":
                service = self.deploy_base_service(
                    service_type="NodePort"
                )
                self.wait_for_service(service)
                api_node_port = self.get_service_nodeport(service, "api")
                jupyter_node_port = self.get_service_nodeport(service, "jupyter")
                tensorboard_node_port = self.get_service_nodeport(service, "tensorboard")
                mlflow_node_port = self.get_service_nodeport(service, "mlflow")
                node_port_url = self.environment.node_port_url
                self.logger.warning("%s" % node_port_url)
                o = urlparse(node_port_url)
                self.api_url = "%s://%s:%s" % (o.scheme, o.hostname, api_node_port)
                self.editor_url = "%s://%s:%s" % (o.scheme, o.hostname, jupyter_node_port)
                self.tensorboard_url = "%s://%s:%s" % (o.scheme, o.hostname, tensorboard_node_port)
                self.mlflow_url = "%s://%s:%s" % (o.scheme, o.hostname, mlflow_node_port)

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

                # create ingress for Tensorboard
                ingress_mlflow = self.deploy_ingress(
                    service,
                    port=6006,
                    title="tensorboard",
                    ingress_labels={"component": "tensorboard"},
                    rewrite_path=False,
                )
                self.tensorboard_url = self.get_ingress_url("tensorboard")

                # create ingress for MLflow UI
                ingress_mlflow = self.deploy_ingress(
                    service,
                    port=6000,
                    title="mlflow",
                    ingress_labels={"component": "mlflow"},
                    rewrite_path=False,
                )
                self.mlflow_url = self.get_ingress_url("mlflow")

                # create ingress for flask api endpoint
                ingress_api = self.deploy_ingress(
                    service,
                    port=5000,
                    title="api",
                    ingress_labels={"component": "api"},
                    rewrite_path=True,
                )
                self.api_url = self.get_ingress_url("api")

            else:
                raise UserFriendlyError("Unsupported ingress mode %s. Only node-port is allowed." % self.environment.ingress_mode)

            self.runtime_status = {
                "api_url": self.api_url,
                "tensorboard_url": self.tensorboard_url,
                "mlflow_url": self.mlflow_url,
                "editor_url": self.editor_url,
            }
            self.sync_source_code(self.api_url)

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
                    name="mlflow",
                    port=6000,
                    protocol="TCP",
                    target_port=6000,
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
        juypter_base_url = ""
        if self.environment.ingress_mode == "ingress":
            juypter_base_url = self.get_ingress_path("editor")

        if models_volume_claim:
            volumes = [
                kubernetes_client.V1Volume(
                    name="data",
                    persistent_volume_claim=kubernetes_client.V1PersistentVolumeClaimVolumeSource(
                        claim_name=models_volume_claim.metadata.name,
                    )
                ),
            ]
            volume_mounts = [
                kubernetes_client.V1VolumeMount(
                    mount_path="/srv",
                    name="data",
                ),
            ]
        else:
            volumes = []
            volume_mounts = []

        return self.deploy_deployment(
            self.get_param("image"),
            cpu_count=self.cpu_count,
            gpu_request=self.gpu_request,
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
                    container_port=6000,
                    name="mlflow",
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
                    value=juypter_base_url,
                )
            ],
            volume_mounts=volume_mounts,
            volumes=volumes,
            run_as_user=1001,
            fs_group=0
        )

    def sync_source_code(self, url):
        url = urllib.parse.urljoin(url, "notebook")
        self.logger.warning("notebookurl: %s" % url)
        try:
            download_request = urllib.request.Request(url, method="GET")
            download_response = urllib.request.urlopen(download_request, timeout=7)
            container_notebook_version_string = download_response.getheader("X-Notebook-Version")
            if container_notebook_version_string is None:
                remote_notebook_version = -1
            else:
                remote_notebook_version = int(container_notebook_version_string)
            remote_notebook_code = download_response.read().decode()
        except http.client.RemoteDisconnected as e:
            if self.status == deployment_status.STATUS_DEPLOYING:
                raise deployment_status.StillDeploying("Waiting for connection")
            raise deployment_status.DeploymentError("Could not connect: %s" % e)
        except urllib.error.HTTPError as e:
            if e.code != 404 and e.code != 503 and e.code != 502 and e.code != 504:
                raise Exception("downloading notebook source failed with code %s" % e.code)
            raise deployment_status.StillDeploying("Waiting for connection to container")
        if remote_notebook_version > self.algorithm.source_code_version:
            self.algorithm.update_source_code(
                remote_notebook_code,
                remote_notebook_version,
            )
            self.logger.info("Received and stored updated source code (version %s)" % remote_notebook_version)
        if remote_notebook_version < self.algorithm.source_code_version:
            local_notebook_data = self.algorithm.source_code.encode()
            upload_request = urllib.request.Request(
                url,
                data=local_notebook_data,
                method="PUT",
                headers={
                    "X-Notebook-Version": self.algorithm.source_code_version,
                    "Content-Type": "application/octet-stream",
                }
            )
            try:
                upload_response = urllib.request.urlopen(upload_request)
                self.logger.info("Sent source code (version %s)" % self.algorithm.source_code_version)
                python_code = upload_response.read().decode()
                #self.logger.info("Resulting python code:\n%s" % python_code)
            except urllib.error.HTTPError as e:
                if e.code != 404 and e.code != 503 and e.code != 502 and e.code != 504:
                    raise Exception("Error uploading sourcecode: %s" % e.code)
                raise deployment_status.StillDeploying("Waiting for connection to container")
