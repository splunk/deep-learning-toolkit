from kubernetes import client as kubernetes_client
from kubernetes.client.rest import ApiException

from dltk.core.deployment import status as deployment_status, Deployment
import urllib
import http
import re
from dltk.core import environment
from . import resources

app_label = "app"
app_name = "dltk"
runtime_label = "runtime"
strategy_label = "strategy"
algorithm_label = "algorithm"
deployment_label = "deployment"
tag_label = "tag"


class KubernetesDeployment(Deployment):

    _api_client = None
    strategy_name = None
    custom_object_types = None

    def __init__(self, splunk, stanza, strategy_name="0", custom_object_types=[]):
        super().__init__(splunk, stanza)
        self.strategy_name = strategy_name
        self.custom_object_types = custom_object_types

    def generate_label_value(self, value):
        if len(value) > 60:
            value = value[-60:]
        return re.sub('[^0-9a-zA-Z]+', '-', value)

    def generate_object_name(self, suffix):
        if self.guid:
            name = "%s-%s" % (
                app_name,
                self.guid,
            )
        else:
            name = "%s-%s-%s" % (
                app_name,
                self.algorithm.runtime.name,
                self.algorithm.name,
            )
        if suffix:
            suffix = re.sub('[^0-9a-zA-Z]+', '-', suffix)
            name += "-%s" % suffix
        return name

    def generate_object_labels(self, labels={}):
        if labels is None:
            labels = {}
        result = {}
        if self.environment.tag_label:
            result[tag_label] = self.environment.tag_label
        result.update({
            app_label: app_name,
            runtime_label: self.generate_label_value(self.algorithm.runtime.name),
            strategy_label: self.strategy_name,
            algorithm_label: self.generate_label_value(self.algorithm.name),
            deployment_label: self.guid,
        })
        result.update(labels)
        return result

    def generate_object_label_selector(self, labels={}, return_list=False):
        if labels is None:
            labels = {}
        selector = [
            "%s=%s" % (app_label, app_name),
            "%s=%s" % (runtime_label, self.generate_label_value(self.algorithm.runtime.name)),
            "%s=%s" % (algorithm_label, self.generate_label_value(self.algorithm.name)),
        ]
        if self.guid:
            selector.append(
                "%s=%s" % (deployment_label, self.guid)
            )
        selector.extend([
            "%s=%s" % (k, v)
            for k, v in labels.items()
        ])
        if return_list:
            return selector
        return ",".join(selector)

    def deploy(self):
        self.delete_objects(
            only_outdated=not self.is_disabled,
            include_volumes=False,
            include_services=True,
            include_workloads=True,
            include_secrets=True,
            include_ingresses=True,
        )
        if self.restart_required:
            self.delete_objects(
                only_outdated=False,
                include_volumes=False,
                include_services=False,
                include_workloads=True,
                include_secrets=False,
                include_ingresses=False,
            )
            self.restart_required = False

    def undeploy(self):
        if environment.exists(self.splunk, self.environment_name):
            try:
                self.delete_objects(
                    only_outdated=False,
                    include_volumes=True,
                    include_services=True,
                    include_workloads=True,
                    include_secrets=True,
                    include_ingresses=True,
                )
            except kubernetes_client.rest.ApiException as e:
                if e.status != 401:
                    raise

    @property
    def api_client(self):
        if self._api_client:
            return self._api_client
        self._api_client = self.environment.create_api_client()
        return self._api_client

    _core_api = None

    @property
    def core_api(self):
        if self._core_api:
            return self._core_api
        self._core_api = kubernetes_client.CoreV1Api(self.api_client)
        return self._core_api

    _apps_api = None

    @property
    def apps_api(self):
        if self._apps_api:
            return self._apps_api
        self._apps_api = kubernetes_client.AppsV1Api(self.api_client)
        return self._apps_api

    _extensions_api = None

    @property
    def extensions_api(self):
        if self._extensions_api:
            return self._extensions_api
        self._extensions_api = kubernetes_client.ExtensionsV1beta1Api(self.api_client)
        return self._extensions_api

    _networking_api = None

    @property
    def networking_api(self):
        if self._networking_api:
            return self._networking_api
        self._networking_api = kubernetes_client.NetworkingV1beta1Api(self.api_client)
        return self._networking_api

    _custom_objects_api = None

    @property
    def custom_objects_api(self):
        if self._custom_objects_api:
            return self._custom_objects_api
        self._custom_objects_api = kubernetes_client.CustomObjectsApi(self.api_client)
        return self._custom_objects_api

    def get_service_hostname(self, service):
        for ingress in service.status.load_balancer.ingress:
            if ingress.hostname:
                return ingress.hostname
            if ingress.ip:
                return ingress.ip
        raise Exception("could not find hostname for service %s" % service["metadata"]["name"])

    def get_service_nodeport(self, service, portname):
        for port in service.spec.ports:
            if port.name == portname:
                return port.node_port
            if port.port == portname:
                return port.node_port
        return None

    def wait_for_deployment(self, deployment):
        return self.ensure_deployment_is_ready(deployment, deployment_status.StillDeploying)

    def wait_for_stateful_set(self, stateful_set):
        return self.ensure_stateful_set_is_ready(stateful_set, deployment_status.StillDeploying)

    def wait_for_service(self, service):
        return self.ensure_service_is_ready(service, deployment_status.StillDeploying)

    def wait_for_endpoints_pod_ip(self, endpoints_name):
        endpoints = self.core_api.read_namespaced_endpoints(
            endpoints_name,
            self.environment.namespace,
        )
        if not endpoints:
            raise deployment_status.StillDeploying("Waiting for %s endpoints" % endpoints_name)
        if not endpoints.subsets:
            raise deployment_status.StillDeploying("Waiting for %s endpoints" % endpoints_name)
        pod_ip = None
        for subset in endpoints.subsets:
            for address in subset.addresses:
                pod_ip = address.ip
        if not pod_ip:
            raise deployment_status.StillDeploying("Waiting for %s pod endpoint address" % endpoints_name)
        return pod_ip

    def is_deployment_ready(self, deployment):
        class NotReady(Exception):
            pass
        try:
            self.ensure_deployment_is_ready(deployment, NotReady)
            return True
        except NotReady:
            return False

    def ensure_deployment_is_ready(self, deployment, not_ready_error, title=None):
        is_ready = False
        try:
            if not title:
                title = "deployment %s" % deployment.metadata.name
            if not deployment.status:
                raise not_ready_error("Waiting for %s status" % title)
            # self.logger.info("deployment.spec.replicas: %s" % deployment.spec.replicas)
            # self.logger.info("deployment.status.replicas: %s" % deployment.status.replicas)
            if deployment.status.replicas is None:
                raise not_ready_error("Waiting for %s to become ready (no replicas)" % title)
            if deployment.status.ready_replicas is None:
                raise not_ready_error("Waiting for %s to become ready (no ready_replicas)" % title)
            if deployment.status.ready_replicas != deployment.spec.replicas:
                raise not_ready_error("Waiting for %s to become ready (not enought ready replicas: %s/%s)" % (
                    title,
                    deployment.status.ready_replicas,
                    deployment.spec.replicas,
                ))
            is_ready = True
        finally:
            if not is_ready:
                self.logger.error("deployment.status: %s" % deployment.status)
                self.logger.error("deployment.spec: %s" % deployment.spec)
                label_selector = ",".join([
                    "%s=%s" % (k, v)
                    for k, v in deployment.spec.selector.match_labels.items()
                ])
                pods = self.core_api.list_namespaced_pod(
                    namespace=self.environment.namespace,
                    label_selector=label_selector,
                ).items
                for pod in pods:
                    self.logger.error("pod: %s" % pod.status)

    def is_stateful_set_ready(self, stateful_set):
        class NotReady(Exception):
            pass
        try:
            self.ensure_stateful_set_is_ready(stateful_set, NotReady)
            return True
        except NotReady:
            return False

    def ensure_stateful_set_is_ready(self, stateful_set, not_ready_error, title=None):
        if not title:
            title = "stateful set %s" % stateful_set.metadata.name
        if not stateful_set.status:
            raise not_ready_error("Waiting for %s status" % title)
        if stateful_set.status.ready_replicas != stateful_set.status.replicas:
            raise not_ready_error("Waiting for %s to become ready" % title)

    def get_ingresses(self, label_selector):
        ingresses = self.networking_api.list_namespaced_ingress(
            namespace=self.environment.namespace,
            label_selector=self.generate_object_label_selector(label_selector),
        ).items
        return ingresses

    def get_ingress(self, label_selector):
        ingresses = self.get_ingresses(label_selector)
        if len(ingresses):
            return ingresses[0]
        return None

    def get_ingress_url(self, title):
        return urllib.parse.urljoin(
            self.environment.ingress_base_url,
            self.get_ingress_path(title),
        )

    def get_ingress_path(self, title):
        return "/%s/%s/%s/" % (
            app_name,
            self.guid,
            title,
        )

    def deploy_ingress(self,
                       target_service,
                       port=None,
                       title=None,
                       ingress_labels=None,
                       rewrite_path=True,
                       ):
        ingress = self.get_ingress(ingress_labels)
        if not ingress:
            path = self.get_ingress_path(title)
            annotations = {}
            ingress_path = path
            if self.environment.ingress_class:
                annotations["kubernetes.io/ingress.class"] = self.environment.ingress_class
            if rewrite_path and self.environment.ingress_class:
                if self.environment.ingress_class == "nginx":
                    annotations["nginx.ingress.kubernetes.io/rewrite-target"] = "/$1"
                    ingress_path += "(.*)"
                elif self.environment.ingress_class == "haproxy":
                    # annotations["ingress.kubernetes.io/path-rewrite"] = "%s(.*) /\\1" % path
                    annotations["ingress.kubernetes.io/rewrite-target"] = "/"
            ingress = self.networking_api.create_namespaced_ingress(
                namespace=self.environment.namespace,
                body=kubernetes_client.NetworkingV1beta1Ingress(
                    api_version="networking.k8s.io/v1beta1",
                    kind="Ingress",
                    metadata=kubernetes_client.V1ObjectMeta(
                        name=self.generate_object_name(title),
                        namespace=self.environment.namespace,
                        labels=self.generate_object_labels(ingress_labels),
                        annotations=annotations
                    ),
                    spec=kubernetes_client.NetworkingV1beta1IngressSpec(
                        rules=[
                            kubernetes_client.NetworkingV1beta1IngressRule(
                                http=kubernetes_client.NetworkingV1beta1HTTPIngressRuleValue(
                                    paths=[
                                        kubernetes_client.NetworkingV1beta1HTTPIngressPath(
                                            path=ingress_path,
                                            backend=kubernetes_client.NetworkingV1beta1IngressBackend(
                                                service_name=target_service.metadata.name,
                                                service_port=port,
                                            )
                                        )
                                    ]
                                )
                            ),
                        ],
                    ),
                ),
            )
        return ingress

    def wait_for_ingress(self, title, test_path=None, method="GET"):
        base_url = self.get_ingress_url(title)
        test_url = urllib.parse.urljoin(base_url, test_path)
        request = urllib.request.Request(test_url, method=method)
        try:
            urllib.request.urlopen(request)
        except http.client.RemoteDisconnected as e:
            self.logger.warning("wait_for_ingress (%s): RemoteDisconnected: %s" % (test_url, e))
            if self.status == deployment_status.STATUS_DEPLOYING:
                raise deployment_status.StillDeploying("Waiting for %s ingress" % title)
            raise deployment_status.DeploymentError("Could not connect: %s" % e)
        except urllib.error.HTTPError as e:
            self.logger.warning("wait_for_ingress (%s): HTTPError: %s" % (test_url, e))
            if self.status == deployment_status.STATUS_DEPLOYING:
                if e.code == 404 or e.code == 503 or e.code == 502 or e.code == 504:
                    raise deployment_status.StillDeploying("Waiting for %s ingress" % title)
            raise deployment_status.DeploymentError("HTTP response: %s" % e)
        except urllib.error.URLError as e:
            self.logger.warning("wait_for_ingress (%s): URLError: %s" % (test_url, e))
            if self.status == deployment_status.STATUS_DEPLOYING:
                raise deployment_status.StillDeploying("Waiting for %s ingress" % title)
            raise deployment_status.DeploymentError("URL error: %s" % e)

    def expose_pods(self,
                    name,
                    pod_port,
                    pod_labels,
                    labels=None,
                    rewrite_path=True,
                    ):
        # self.
        service = self.deploy_service(
            title=name,
            ports=[
                kubernetes_client.V1ServicePort(
                    name="app",
                    port=80,
                    protocol="TCP",
                    target_port=pod_port,
                ),
            ],
            pod_labels=pod_labels,
            service_labels=labels,
        )
        return self.deploy_ingress(
            service,
            port=80,
            title=name,
            ingress_labels=labels,
            rewrite_path=rewrite_path,
        )

    def is_service_ready(self, service):
        class NotReady(Exception):
            pass
        try:
            self.ensure_service_is_ready(service, NotReady)
            return True
        except NotReady:
            return False

    def ensure_service_is_ready(self, service, not_ready_error, title=None):
        if not title:
            title = "service %s" % service.metadata.name
        if not service.status:
            raise not_ready_error("Waiting for %s status" % title)
        if service.spec.type == "LoadBalancer":
            if not service.status.load_balancer:
                raise not_ready_error("Waiting for %s load balancer" % title)
            if not service.status.load_balancer.ingress:
                raise not_ready_error("Waiting for %s load balancer" % title)
            load_balancer_ingress_hostnames = []
            for ingress in service.status.load_balancer.ingress:
                if ingress.hostname:
                    load_balancer_ingress_hostnames.append(ingress.hostname)
                if ingress.ip:
                    load_balancer_ingress_hostnames.append(ingress.ip)
            if not len(load_balancer_ingress_hostnames):
                raise not_ready_error("Waiting for %s load balancer" % title)
            for hostname in load_balancer_ingress_hostnames:
                try:
                    import socket
                    socket.gethostbyname(hostname)
                except socket.error:
                    raise not_ready_error("Waiting for %s load balancer" % title)

    def get_services(self, label_selector):
        services = self.core_api.list_namespaced_service(
            namespace=self.environment.namespace,
            label_selector=self.generate_object_label_selector(label_selector),
        ).items
        return services

    def get_service(self, label_selector):
        services = self.get_services(label_selector)
        if len(services):
            return services[0]
        return None

    def deploy_service(
        self,
        ports=[],
        title="",
        pod_labels=None,
        service_labels={},
        cluster_ip=None,
        service_type=None,
    ):
        service = self.get_service(service_labels)
        if not service:
            self.logger.info("creating service (%s)..." % title)
            service = self.core_api.create_namespaced_service(
                namespace=self.environment.namespace,
                body=kubernetes_client.V1Service(
                    api_version="v1",
                    kind="Service",
                    metadata=kubernetes_client.V1ObjectMeta(
                        name=self.generate_object_name(title),
                        namespace=self.environment.namespace,
                        labels=self.generate_object_labels(service_labels)
                    ),
                    spec=kubernetes_client.V1ServiceSpec(
                        cluster_ip=cluster_ip,
                        type=service_type,
                        selector=self.generate_object_labels(pod_labels),
                        ports=ports,
                    ),
                ),
            )
        return service

    def get_secrets(self, label_selector):
        secrets = self.core_api.list_namespaced_secret(
            namespace=self.environment.namespace,
            label_selector=self.generate_object_label_selector(label_selector),
        ).items
        return secrets

    def get_secret(self, label_selector):
        secrets = self.get_secrets(label_selector)
        if len(secrets) > 0:
            return secrets[0]
        return None

    def deploy_secret(self, title, labels, data):
        secret = self.get_secret(labels)
        if not secret:
            self.core_api.create_namespaced_secret(
                namespace=self.environment.namespace,
                body=kubernetes_client.V1Secret(
                    api_version="v1",
                    kind="Secret",
                    type="Opaque",
                    metadata=kubernetes_client.V1ObjectMeta(
                        name="%s-%s-%s-%s" % (
                            app_name,
                            self.algorithm.runtime.name,
                            self.algorithm.name,
                            title,
                        ),
                        namespace=self.environment.namespace,
                        labels=self.generate_object_labels(labels)
                    ),
                    string_data=data,
                ),
            )
        return secret

    def get_pod_status(self, pod_name):
        return self.core_api.read_namespaced_pod_status(
            name=pod_name,
            namespace=self.environment.namespace,
        )

    def get_deployment(self, label_selector):
        try:
            deployments = self.apps_api.list_namespaced_deployment(
                namespace=self.environment.namespace,
                label_selector=self.generate_object_label_selector(label_selector),
            ).items
            if len(deployments):
                return deployments[0]
        except ApiException as e:
            if e.status != 404:
                raise
        return None

    def deploy_deployment(
        self,
        image,
        memory_mb=50,
        cpu_count=None,  # deprecated
        cpu_request=1,
        cpu_limit=None,
        gpu_request=None,
        replicas=1,
        deployment_labels=None,
        pod_labels=None,
        name_suffix=None,
        container_name=None,
        ports=[],
        env=None,
        volumes=[],
        volume_mounts=[],
        run_as_user=None,
        fs_group=None,
    ):
        if not container_name:
            if name_suffix:
                container_name = name_suffix
            else:
                container_name = self.algorithm.runtime.name
            container_name = container_name.replace(".", "-")
        if cpu_count is not None:
            cpu_request_resources = "%s" % cpu_count
            cpu_limit_resources = "%s" % cpu_count
        else:
            if cpu_limit is None:
                cpu_limit = cpu_request
            cpu_request_resources = "%s" % cpu_request
            cpu_limit_resources = "%s" % cpu_limit
        memory_resources = "%sMi" % memory_mb
        if gpu_request != None:
            gpu_request_resources = "%s" % gpu_request
            gpu_limit_resources = gpu_request_resources
        else:
            gpu_request_resources = None
            gpu_limit_resources = None
        deployment = self.get_deployment(deployment_labels)
        if deployment:
            changed = False
            if deployment.spec.replicas != replicas:
                self.logger.info("replicas changed from %s to %s" % (deployment.spec.replicas, replicas))
                deployment.spec.replicas = replicas
                changed = True
            for container in deployment.spec.template.spec.containers:
                if container.name == container_name:
                    if container.image != image:
                        container.image = image
                        changed = True
                        self.logger.info("image changed")
                    if container.resources.requests is None:
                        container.resources.requests = {}
                    if container.resources.limits is None:
                        container.resources.limits = {}
                    if "cpu" not in container.resources.requests or container.resources.requests["cpu"] != cpu_request_resources:
                        container.resources.requests["cpu"] = cpu_request_resources
                        changed = True
                        self.logger.info("cpu_requests_resources requests changed to %s" % cpu_request_resources)
                    if "cpu" not in container.resources.limits or container.resources.limits["cpu"] != cpu_limit_resources:
                        container.resources.limits["cpu"] = cpu_limit_resources
                        changed = True
                        self.logger.info("cpu_limit_resources limits changed to %s" % cpu_limit_resources)
                    if "memory" not in container.resources.requests:
                        container.resources.requests["memory"] = memory_resources
                        changed = True
                        self.logger.info("memory_resources was not set. Now set to '%s'" % (
                            memory_resources,
                        ))
                    elif resources.parse_memory(container.resources.requests["memory"]) != resources.parse_memory(memory_resources):
                        container.resources.requests["memory"] = memory_resources
                        changed = True
                        self.logger.info("memory_resources requests changed from '%s' to '%s'" % (
                            container.resources.requests["memory"],
                            memory_resources,
                        ))
                    if "memory" not in container.resources.limits:
                        container.resources.limits["memory"] = memory_resources
                        changed = True
                        self.logger.info("memory_resources limits was not set. Now set to %s" % memory_resources)
                    elif resources.parse_memory(container.resources.limits["memory"]) != resources.parse_memory(memory_resources):
                        container.resources.limits["memory"] = memory_resources
                        changed = True
                        self.logger.info("memory_resources limits changed from %s to %s" % (
                            container.resources.limits["memory"],
                            memory_resources,
                        ))
                    if "nvidia.com/gpu" not in container.resources.limits:
                        if gpu_limit_resources != None:
                            container.resources.limits["nvidia.com/gpu"] = gpu_limit_resources
                            changed = True
                            self.logger.info("gpu_resources limits was not set. Now set to %s" % gpu_limit_resources)
                    elif container.resources.limits["nvidia.com/gpu"] != gpu_limit_resources:
                        if gpu_limit_resources  != None:
                            container.resources.limits["nvidia.com/gpu"] = gpu_limit_resources
                            changed = True
                            self.logger.info("gpu_resources limits changed from %s to %s" % (
                                container.resources.limits["nvidia.com/gpu"],
                                gpu_limit_resources,
                            ))
                        else:
                            self.logger.info("gpu_resources limits was set to %s but not required anymore" % (
                                container.resources.limits["nvidia.com/gpu"],
                            ))
                            del container.resources.limits["nvidia.com/gpu"]
                            changed = True
                    if "nvidia.com/gpu" not in container.resources.requests:
                        if gpu_request_resources != None:
                            container.resources.requests["nvidia.com/gpu"] = gpu_request_resources
                            changed = True
                            self.logger.info("gpu_resources requests was not set. Now set to %s" % gpu_request_resources)
                    elif container.resources.requests["nvidia.com/gpu"] != gpu_request_resources:
                        if gpu_request_resources != None:
                            container.resources.requests["nvidia.com/gpu"] = gpu_request_resources
                            changed = True
                            self.logger.info("gpu_resources requests changed from %s to %s" % (
                                container.resources.requests["nvidia.com/gpu"],
                                gpu_request_resources,
                            ))
                        else:
                            self.logger.info("gpu_resources requests was set to %s but not required anymore" % (
                                container.resources.requests["nvidia.com/gpu"],
                            ))
                            del container.resources.requests["nvidia.com/gpu"]
                            changed = True
            if changed:
                self.logger.info("patching deployment...")
                self.apps_api.patch_namespaced_deployment(
                    name=deployment.metadata.name,
                    namespace=self.environment.namespace,
                    body=deployment,
                )
                raise deployment_status.StillDeploying("Waiting for %s deployment being patched" % container_name)
        else:
            resource_requirements = kubernetes_client.V1ResourceRequirements(
                requests={
                    "cpu": cpu_request_resources,
                    "memory": memory_resources,
                },
                limits={
                    "cpu": cpu_limit_resources,
                    "memory": memory_resources,
                },
            )
            if gpu_request_resources:
                resource_requirements.requests["nvidia.com/gpu"] = gpu_request_resources
            if gpu_limit_resources:
                resource_requirements.limits["nvidia.com/gpu"] = gpu_limit_resources
            self.logger.info("creating %s deployment..." % container_name)
            deployment = self.apps_api.create_namespaced_deployment(
                namespace=self.environment.namespace,
                body=kubernetes_client.V1Deployment(
                    api_version="apps/v1",
                    kind="Deployment",
                    metadata=kubernetes_client.V1ObjectMeta(
                        name=self.generate_object_name(name_suffix),
                        namespace=self.environment.namespace,
                        labels=self.generate_object_labels(deployment_labels)
                    ),
                    spec=kubernetes_client.V1DeploymentSpec(
                        replicas=replicas,
                        selector=kubernetes_client.V1LabelSelector(
                            match_labels=self.generate_object_labels(pod_labels)
                        ),
                        template=kubernetes_client.V1PodTemplateSpec(
                            metadata=kubernetes_client.V1ObjectMeta(
                                labels=self.generate_object_labels(pod_labels)
                            ),
                            spec=kubernetes_client.V1PodSpec(
                                containers=[
                                    kubernetes_client.V1Container(
                                        name=container_name,
                                        image=image,
                                        image_pull_policy=self.environment.image_pull_policy,
                                        resources=resource_requirements,
                                        env=env,
                                        ports=ports,
                                        volume_mounts=volume_mounts,
                                    ),
                                ],
                                volumes=volumes,
                                security_context=kubernetes_client.V1PodSecurityContext(
                                    run_as_user=run_as_user,
                                    fs_group=fs_group,
                                ),
                            ),
                        ),
                    ),
                ),
            )
        return deployment

    def get_stateful_set(self, label_selector):
        try:
            stateful_sets = self.apps_api.list_namespaced_stateful_set(
                namespace=self.environment.namespace,
                label_selector=self.generate_object_label_selector(label_selector),
            ).items
            if len(stateful_sets):
                return stateful_sets[0]
        except ApiException as e:
            if e.status != 404:
                raise
        return None

    def deploy_stateful_set(
        self,
        component_name,
        headless_service,
        cpu_count,  # deprecated
        memory_mb,
        image,
        replicas,
        stateful_set_labels,
        pod_labels,
        ports=None,
        env=None,
        cpu_request=1,
        cpu_limit=None,
    ):
        if cpu_count is not None:
            cpu_request_resources = "%s" % cpu_count
            cpu_limit_resources = "%s" % cpu_count
        else:
            if cpu_limit is None:
                cpu_limit = cpu_request
            cpu_request_resources = "%s" % cpu_request
            cpu_limit_resources = "%s" % cpu_limit
        memory_resources = "%sMi" % memory_mb
        stateful_set = self.get_stateful_set(stateful_set_labels)
        if stateful_set:
            changed = False
            if stateful_set.spec.replicas != replicas:
                self.logger.info("replicas changed from %s to %s" % (stateful_set.spec.replicas, replicas))
                stateful_set.spec.replicas = replicas
                changed = True
            for container in stateful_set.spec.template.spec.containers:
                if container.name == component_name:
                    if container.image != image:
                        container.image = image
                        changed = True
                        self.logger.info("image changed")
                    if container.resources.requests is None:
                        container.resources.requests = {}
                    if container.resources.limits is None:
                        container.resources.limits = {}
                    if "cpu" not in container.resources.requests or container.resources.requests["cpu"] != cpu_request_resources:
                        container.resources.requests["cpu"] = cpu_request_resources
                        changed = True
                        self.logger.info("cpu requests changed to %s" % cpu_request_resources)
                    if "cpu" not in container.resources.limits or container.resources.limits["cpu"] != cpu_limit_resources:
                        container.resources.limits["cpu"] = cpu_limit_resources
                        changed = True
                        self.logger.info("cpu limit changed to %s" % cpu_limit_resources)
                    if "memory" not in container.resources.requests or container.resources.requests["memory"] != memory_resources:
                        container.resources.requests["memory"] = memory_resources
                        changed = True
                        self.logger.info("memory request changed to %s" % memory_resources)
                    if "memory" not in container.resources.limits or container.resources.limits["memory"] != memory_resources:
                        container.resources.limits["memory"] = memory_resources
                        changed = True
                        self.logger.info("memory limit changed to %s" % memory_resources)
            if changed:
                self.logger.info("patching stateful_set...")
                self.apps_api.patch_namespaced_stateful_set(
                    name=stateful_set.metadata.name,
                    namespace=self.environment.namespace,
                    body=stateful_set,
                )
                raise deployment_status.StillDeploying("Waiting for %s stateful set being patched" % component_name)
        else:
            self.logger.info("creating %s stateful_set..." % component_name)
            stateful_set = self.apps_api.create_namespaced_stateful_set(
                namespace=self.environment.namespace,
                body=kubernetes_client.V1StatefulSet(
                    api_version="apps/v1",
                    kind="StatefulSet",
                    metadata=kubernetes_client.V1ObjectMeta(
                        name=self.generate_object_name(component_name),
                        namespace=self.environment.namespace,
                        labels=self.generate_object_labels(stateful_set_labels)
                    ),
                    spec=kubernetes_client.V1StatefulSetSpec(
                        service_name=headless_service.metadata.name,
                        replicas=replicas,
                        selector=kubernetes_client.V1LabelSelector(
                            match_labels=self.generate_object_labels(pod_labels)
                        ),
                        template=kubernetes_client.V1PodTemplateSpec(
                            metadata=kubernetes_client.V1ObjectMeta(
                                labels=self.generate_object_labels(pod_labels)
                            ),
                            spec=kubernetes_client.V1PodSpec(
                                containers=[
                                    kubernetes_client.V1Container(
                                        name=component_name,
                                        image=image,
                                        image_pull_policy=self.environment.image_pull_policy,
                                        resources=kubernetes_client.V1ResourceRequirements(
                                            requests={
                                                "cpu": cpu_request_resources,
                                                "memory": memory_resources,
                                            },
                                            limits={
                                                "cpu": cpu_limit_resources,
                                                "memory": memory_resources,
                                            },
                                        ),
                                        env=env,
                                        ports=ports,
                                    ),
                                ],
                            ),
                        ),
                    ),
                ),
            )
        return stateful_set

    def delete_service(self, service_name):
        self.logger.info("deleting service '%s' ..." % service_name)
        self.core_api.delete_namespaced_service(
            namespace=self.environment.namespace,
            name=service_name,
            body=kubernetes_client.V1DeleteOptions(),
        )

    def delete_objects(
        self,
        only_outdated,
        include_services,
        include_workloads,
        include_volumes,
        include_secrets,
        include_ingresses,
        additional_label_selector={},
        delete_filter=None
    ):
        if delete_filter is None:
            def delete_all_filter(kind, labels):
                return True
            delete_filter = delete_all_filter
        label_selector_list = self.generate_object_label_selector(
            labels=additional_label_selector,
            return_list=True
        )
        if only_outdated:
            label_selector_list.append(strategy_label + "!=" + self.strategy_name)
        label_selector = ",".join(label_selector_list)
        if include_workloads:
            deployments = self.apps_api.list_namespaced_deployment(
                namespace=self.environment.namespace,
                label_selector=label_selector,
            ).items
            for deployment in deployments:
                if delete_filter(deployment.kind, deployment.metadata.labels):
                    self.logger.info("deleting deployment '%s' ..." % deployment.metadata.name)
                    self.apps_api.delete_namespaced_deployment(
                        namespace=self.environment.namespace,
                        name=deployment.metadata.name,
                        body=kubernetes_client.V1DeleteOptions(),
                    )
            stateful_sets = self.apps_api.list_namespaced_stateful_set(
                namespace=self.environment.namespace,
                label_selector=label_selector,
            ).items
            for stateful_set in stateful_sets:
                if delete_filter(stateful_set.kind, stateful_set.metadata.labels):
                    self.logger.info("deleting stateful set '%s' ..." % stateful_set.metadata.name)
                    self.apps_api.delete_namespaced_stateful_set(
                        namespace=self.environment.namespace,
                        name=stateful_set.metadata.name,
                        body=kubernetes_client.V1DeleteOptions(),
                    )
            for custom_object_type in self.custom_object_types:
                group, version, plural = custom_object_type
                custom_objects = self.custom_objects_api.list_namespaced_custom_object(
                    group=group,
                    version=version,
                    namespace=self.environment.namespace,
                    plural=plural,
                    label_selector=label_selector
                )["items"]
                for custom_object in custom_objects:
                    custom_object_name = custom_object["metadata"]["name"]
                    if delete_filter(custom_object["kind"], custom_object["metadata"]["labels"]):
                        self.logger.info("deleting object '%s' ..." % custom_object_name)
                        self.custom_objects_api.delete_namespaced_custom_object(
                            group=group,
                            version=version,
                            namespace=self.environment.namespace,
                            plural=plural,
                            name=custom_object_name,
                            body=kubernetes_client.V1DeleteOptions(),
                        )
        if include_services:
            services = self.core_api.list_namespaced_service(
                namespace=self.environment.namespace,
                label_selector=label_selector,
            ).items
            for service in services:
                if delete_filter(service.kind, service.metadata.labels):
                    self.delete_service(service.metadata.name)
        if include_volumes:
            volume_claims = self.core_api.list_namespaced_persistent_volume_claim(
                namespace=self.environment.namespace,
                label_selector=label_selector,
            ).items
            for volume_claim in volume_claims:
                if delete_filter(volume_claim.kind, volume_claim.metadata.labels):
                    self.logger.info("deleting claim '%s' ..." % volume_claim.metadata.name)
                    self.core_api.delete_namespaced_persistent_volume_claim(
                        namespace=self.environment.namespace,
                        name=volume_claim.metadata.name,
                        body=kubernetes_client.V1DeleteOptions(),
                    )
        if include_secrets:
            secrets = self.core_api.list_namespaced_secret(
                namespace=self.environment.namespace,
                label_selector=label_selector,
            ).items
            for secret in secrets:
                if delete_filter(secret.kind, secret.metadata.labels):
                    self.logger.info("deleting secret '%s' ..." % secret.metadata.name)
                    self.core_api.delete_namespaced_secret(
                        namespace=self.environment.namespace,
                        name=secret.metadata.name,
                        body=kubernetes_client.V1DeleteOptions(),
                    )
        if include_ingresses:
            ingresses = self.extensions_api.list_namespaced_ingress(
                namespace=self.environment.namespace,
                label_selector=label_selector,
            ).items
            for ingress in ingresses:
                if delete_filter(ingress.kind, ingress.metadata.labels):
                    self.logger.info("deleting ingress '%s' ..." % ingress.metadata.name)
                    self.extensions_api.delete_namespaced_ingress(
                        namespace=self.environment.namespace,
                        name=ingress.metadata.name,
                        body=kubernetes_client.V1DeleteOptions(),
                    )

    def get_volume_claim(self, label_selector):
        try:
            volume_claims = self.core_api.list_namespaced_persistent_volume_claim(
                namespace=self.environment.namespace,
                label_selector=self.generate_object_label_selector(label_selector),
            ).items
            if len(volume_claims):
                return volume_claims[0]
        except ApiException as e:
            if e.status != 404:
                raise
        return None

    def deploy_volume_claim(
        self,
        labels={},
        name_suffix="",
        ports=None,
        env=None,
    ):
        volume_claim = self.get_volume_claim(labels)
        if not volume_claim:
            self.logger.info("creating volume claim (%s) ..." % name_suffix)
            storage_class_name = None
            if self.environment.storage_class:
                storage_class_name = self.environment.storage_class
            volume_claim = self.core_api.create_namespaced_persistent_volume_claim(
                namespace=self.environment.namespace,
                body=kubernetes_client.V1PersistentVolumeClaim(
                    api_version="v1",
                    kind="PersistentVolumeClaim",
                    metadata=kubernetes_client.V1ObjectMeta(
                        name=self.generate_object_name(name_suffix),
                        namespace=self.environment.namespace,
                        labels=self.generate_object_labels(labels),
                    ),
                    spec=kubernetes_client.V1PersistentVolumeClaimSpec(
                        access_modes=["ReadWriteOnce"],
                        resources=kubernetes_client.V1ResourceRequirements(
                            requests={
                                "storage": "1Gi",
                            },
                        ),
                        storage_class_name=storage_class_name,
                    ),
                ),
            )
        return volume_claim
