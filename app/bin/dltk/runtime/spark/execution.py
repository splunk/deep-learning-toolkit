

import urllib
import http
from dltk.core import deployment
from dltk.core import execution
from dltk.connector.kubernetes import KubernetesExecution
from kubernetes import client as kubernetes_client
from dltk.core.deployment import status as deployment_status
import logging
import opentracing
import json
import time
import socket
import io
from . import application as spark_application
import hdfs

__all__ = ["SparkExecution"]


class SparkExecution(KubernetesExecution):

    hdfs_client = None
    chunk_index = 0

    @property
    def input_hdfs_data_path(self):
        return self.get_param("input_hdfs_data_path")

    @property
    def relay_hdfs_url(self):
        return self.get_param("relay_hdfs_url")

    @property
    def driver_image(self):
        return self.get_param("driver_image")

    @property
    def executor_image(self):
        return self.get_param("executor_image")

    @property
    def driver_proxy_image(self):
        return self.get_param("driver_proxy_image")

    @property
    def inbound_relay_source_name_suffix(self):
        return self.generate_object_name_suffix("inbound-relay-source")

    @property
    def outbound_relay_sink_name_suffix(self):
        return self.generate_object_name_suffix("outbound-relay-sink")

    @property
    def driver_name_suffix(self):
        return self.generate_object_name_suffix("driver")

    @property
    def driver_url(self):
        return self.deployment.get_ingress_url(self.driver_name_suffix)

    @property
    def inbound_relay_url(self):
        return self.deployment.get_ingress_url(self.inbound_relay_source_name_suffix)

    @property
    def outbound_relay_url(self):
        return self.deployment.get_ingress_url(self.outbound_relay_sink_name_suffix)

    @property
    def executor_cores(self):
        return int(self.get_param("executor_cores"))

    def setup(self):
        if not self.context.is_preop:
            self.logger.warning("checking for existing spark app ...")
            if not self.get_spark_app():
                with opentracing.tracer.start_active_span("start-k8s-objects"):
                    self.logger.warning("deploying inbound relay ...")
                    if self.input_hdfs_data_path == "via_relay":
                        self.deploy_inbound_relay()
                    self.logger.warning("deploying outbound relay ...")
                    outbound_relay_source_service = self.deploy_outbound_relay()
                    self.logger.warning("deploying spark app ...")
                    self.deploy_spark_app(outbound_relay_source_service)
                    self.logger.warning("done")

    output_completed = False
    sent_start_signal = False

    def handle(self, buffer, finished):
        if buffer:
            self.send_events(buffer)
        if self.context.is_preop:
            return
        if not finished:
            return
        if not self.sent_start_signal:
            self.signal_start()
            self.sent_start_signal = True
        if not self.output_completed:
            status = self.get_status()
            if status["status"] == "running":
                pass
            elif status["status"] == "error":
                self.signal_stop()
                return execution.ExecutionResult(
                    error=status["error"]
                )
            elif status["status"] == "completed":
                self.signal_stop()
                self.output_completed = True
            else:
                return execution.ExecutionResult(
                    error="unexpected status: %s" % status["status"]
                )
        received_events = self.receive_events()
        self.logger.warning("received_events: %s" % received_events)
        if received_events:
            return execution.ExecutionResult(
                events=received_events,
                final=False,
            )
        if not self.output_completed:
            return execution.ExecutionResult(
                wait=1,
                final=False,
            )

    is_inbound_relay_ready = False

    def send_events(self, buffer):
        buffer = buffer.getvalue()
        if self.input_hdfs_data_path == "via_relay":
            if not self.is_inbound_relay_ready:
                with opentracing.tracer.start_active_span("wait-for-inbound-relay"):
                    self.wait_for_relay(self.inbound_relay_url, path=None)
                self.is_inbound_relay_ready = True
            # https://github.com/opentracing/specification/blob/master/semantic_conventions.md
            with opentracing.tracer.start_active_span("send_data_to_relay", tags={
                opentracing.ext.tags.HTTP_METHOD: "POST",
                opentracing.ext.tags.HTTP_URL: self.inbound_relay_url,
                opentracing.ext.tags.SPAN_KIND: opentracing.ext.tags.SPAN_KIND_RPC_CLIENT,
            }) as scope:
                headers = {
                    "Content-Type": "application/json",
                }
                opentracing.tracer.inject(
                    span_context=scope.span,
                    format=opentracing.propagation.Format.HTTP_HEADERS,
                    carrier=headers
                )
                request = urllib.request.Request(
                    self.inbound_relay_url,
                    method="POST",
                    data=buffer,
                    headers=headers
                )
                response = urllib.request.urlopen(request)
                scope.span.set_tag(
                    opentracing.ext.tags.HTTP_STATUS_CODE,
                    response.getcode(),
                )
            self.logger.warning("sent %s bytes to inbound relay" % len(buffer))
        elif self.input_hdfs_data_path == "direct":
            base_path = self.get_hdfs_directory_path()
            if not self.hdfs_client:
                with opentracing.tracer.start_active_span(
                    "connect-hdfs",
                    tags={
                        opentracing.ext.tags.SPAN_KIND: opentracing.ext.tags.SPAN_KIND_RPC_CLIENT,
                    },
                ):
                    self.hdfs_client = hdfs.InsecureClient(
                        self.relay_hdfs_url,
                        user="root",
                    )
                    #raise Exception("relay_hdfs_url: %s" % self.hdfs_client)
                    self.hdfs_client.makedirs(base_path)

            with opentracing.tracer.start_active_span(
                "send_to_hdfs",
                tags={
                    opentracing.ext.tags.SPAN_KIND: opentracing.ext.tags.SPAN_KIND_RPC_CLIENT,
                },
            ):
                file_path = '%s/%s_%s' % (base_path, socket.gethostname(), self.chunk_index)
                self.logger.warning("hdfs_url: %s%s" % (self.relay_hdfs_url, file_path))
                with self.hdfs_client.write(file_path) as writer:
                    writer.write(buffer)
            self.logger.warning("sent %s bytes (chunk_index=%s) to hdfs" % (len(buffer), self.chunk_index))
            self.chunk_index += 1
        else:
            raise Exception("unsupported input_hdfs_data_path: %s" % self.input_hdfs_data_path)

    def signal_start(self):
        self.logger.warning("sending start signal to Spark ...")
        with opentracing.tracer.start_active_span("wait-for-spark-driver"):
            errors = 0
            # https://github.com/opentracing/specification/blob/master/semantic_conventions.md
            while True:
                with opentracing.tracer.start_active_span("signal-start", tags={
                    opentracing.ext.tags.SPAN_KIND: opentracing.ext.tags.SPAN_KIND_RPC_CLIENT,  # TODO: SPAN_KIND_PRODUCER?
                }) as scope:
                    headers = {
                        "X-DLTK-RootContext": "%s" % self.context.root_trace_context_string,
                    }
                    opentracing.tracer.inject(
                        span_context=scope.span,
                        format=opentracing.propagation.Format.HTTP_HEADERS,
                        carrier=headers
                    )
                    try:
                        request = urllib.request.Request(
                            urllib.parse.urljoin(self.driver_url, "start"),
                            method="PUT",
                            headers=headers
                        )
                        urllib.request.urlopen(request)
                        break
                    except urllib.error.HTTPError as e:
                        #self.logger.warning("signal_start: HTTPError: %s (%s) (%s)" % (e, e.headers, urllib.parse.urljoin(self.driver_url, "start")))
                        errors += 1
                        if e.code == 404 or e.code == 503 or e.code == 502 or e.code == 504:
                            if errors > 600:
                                raise Exception("Timeout signalling input completed")
                            self.logger.warning("still waiting for Spark (code=%s)" % (e.code))
                        else:
                            raise Exception("Error signalling input completed: %s" % e.code)
                time.sleep(1)
        self.logger.warning("successfully sent start signal to Spark")

    def signal_stop(self):
        self.logger.warning("signal_stop ...")
        with opentracing.tracer.start_active_span("signal-stop", tags={
            opentracing.ext.tags.SPAN_KIND: opentracing.ext.tags.SPAN_KIND_RPC_CLIENT,
        }) as scope:
            headers = {}
            opentracing.tracer.inject(
                span_context=scope.span,
                format=opentracing.propagation.Format.HTTP_HEADERS,
                carrier=headers
            )
            request = urllib.request.Request(
                urllib.parse.urljoin(self.driver_url, "stop"),
                method="PUT",
                headers=headers
            )
            urllib.request.urlopen(request)

    def get_status(self):
        self.logger.info("get_status ...")
        with opentracing.tracer.start_active_span("get-status", tags={
            opentracing.ext.tags.SPAN_KIND: opentracing.ext.tags.SPAN_KIND_RPC_CLIENT,
        }) as scope:
            headers = {}
            opentracing.tracer.inject(
                span_context=scope.span,
                format=opentracing.propagation.Format.HTTP_HEADERS,
                carrier=headers
            )
            request = urllib.request.Request(
                urllib.parse.urljoin(self.driver_url, "status"),
                method="GET",
                headers=headers
            )
            response = urllib.request.urlopen(request)
            content_type = response.headers["Content-Type"] if "Content-Type" in response.headers else ""
            if content_type != "application/json":
                raise Exception("Unsupported content type: %s" % content_type)
            status = json.loads(response.read().decode('utf-8'))
            logging.warning("Spark status is '%s'" % status)
            return status

    is_outbound_relay_ready = False

    def receive_events(self):
        if not self.is_outbound_relay_ready:
            with opentracing.tracer.start_active_span("wait-for-outbound-relay"):
                self.wait_for_relay(self.outbound_relay_url)
            self.is_outbound_relay_ready = True

        pull_url = urllib.parse.urljoin(self.outbound_relay_url, "pull")
        method = "POST"
        # https://github.com/opentracing/specification/blob/master/semantic_conventions.md
        with opentracing.tracer.start_active_span("receive_events", tags={
            opentracing.ext.tags.HTTP_METHOD: method,
            opentracing.ext.tags.HTTP_URL: pull_url,
            opentracing.ext.tags.SPAN_KIND: opentracing.ext.tags.SPAN_KIND_RPC_CLIENT,
        }) as scope:
            headers = {}
            opentracing.tracer.inject(
                span_context=scope.span,
                format=opentracing.propagation.Format.HTTP_HEADERS,
                carrier=headers
            )
            request = urllib.request.Request(pull_url, method=method, headers=headers)
            response = urllib.request.urlopen(request)
            if response.getcode() == 204:  # No Content
                return None
        response_content_type = response.headers["Content-Type"] if "Content-Type" in response.headers else None
        with opentracing.tracer.start_active_span("read_response"):
            response_bytes = response.read()
            decoded_response = response_bytes.decode("utf-8")
            return json.loads(decoded_response)

    def get_spark_app(self):
        custom_objects = self.deployment.custom_objects_api.list_namespaced_custom_object(
            group=spark_application.crd_group,
            version=spark_application.crd_version,
            namespace=self.deployment.environment.namespace,
            plural=spark_application.crd_plural,
            label_selector=self.deployment.generate_object_label_selector(self.get_object_labels())
        )["items"]
        return len(custom_objects) > 0

    def get_hdfs_directory_path(self):
        return "/" + self.context.search_id

    def deploy_spark_app(self, outbound_relay_source_service):
        # https://github.com/GoogleCloudPlatform/spark-on-k8s-operator/blob/master/docs/api-docs.md#sparkoperator.k8s.io/v1beta2.SparkApplication
        editor_service = self.deployment.get_service({
            "component": "editor",
        })
        self.logger.info("creating %s object..." % spark_application.crd_name)

        driver_labels = self.get_object_labels({
            "component": "driver",
        })
        # self.deployment.generate_object_labels(driver_labels)
        driver_service = self.deployment.deploy_service(
            title=self.driver_name_suffix,
            ports=[kubernetes_client.V1ServicePort(
                name="api",
                port=80,
                protocol="TCP",
                target_port="api",
            )],
            pod_labels=driver_labels,
            service_labels=driver_labels,
        )
        # TODO: only deploy if required
        driver_ingress = self.deployment.deploy_ingress(
            driver_service,
            port=80,
            title=self.driver_name_suffix,
            ingress_labels=driver_labels,
        )
        self.deployment.custom_objects_api.create_namespaced_custom_object(
            group=spark_application.crd_group,
            version=spark_application.crd_version,
            namespace=self.deployment.environment.namespace,
            plural=spark_application.crd_plural,
            body={
                "apiVersion": "%s/%s" % (spark_application.crd_group, spark_application.crd_version),
                "kind": spark_application.crd_name,
                "metadata": {
                    "name": self.deployment.generate_object_name(
                        self.generate_object_name_suffix()
                    ),
                    "labels": self.deployment.generate_object_labels(self.get_object_labels()),
                },
                "spec": {
                    "type": "Python",
                    "pythonVersion": "3",
                    "mode": "cluster",
                    "imagePullSecrets": [
                        self.deployment.environment.image_pull_secret,
                    ] if self.deployment.environment.image_pull_secret else [],
                    "imagePullPolicy": self.deployment.environment.image_pull_policy,
                    "mainApplicationFile": "local:///dltk/driver/driver.py",
                    "deps": {
                        "pyFiles": [
                            "http://%s/_dltk/algo_code.py" % editor_service.metadata.name
                        ],
                    },
                    "sparkVersion": "2.4.5",
                    "restartPolicy": {
                        "type": "Never",
                    },
                    "hadoopConf": {
                        "fs.s3a.access.key": self.deployment.get_param("checkpoint_s3_access_key"),
                        "fs.s3a.secret.key": self.deployment.get_param("checkpoint_s3_secret_key"),
                        # "spark.driver.memory": "2",
                        # spark.driver.memory=1433
                    },
                    "driver": {
                        "image": self.driver_image,
                        "memory": "%sm" % self.deployment.get_param("driver_memory_mb"),
                        "labels": self.deployment.generate_object_labels(driver_labels),
                        "serviceAccount": self.deployment.get_param("spark_service_account"),
                        "envVars": {
                            "DLTK_ALGO": self.deployment.algorithm.name,
                            "DLTK_SEARCH_ID": self.context.search_id,
                            "DLTK_ALGO_METHOD": self.context.method.name,
                            "DLTK_RECEIVER_COUNT": self.deployment.get_param("receiver_count"),
                            "DLTK_BATCH_INTERVAL": self.deployment.get_param("batch_interval"),
                            "DLTK_OUTBOUND_RELAY": outbound_relay_source_service.metadata.name,
                            "DLTK_WAIT_TIME_BEFORE_STOP": self.deployment.get_param("wait_time_before_stop"),
                            "DLTK_CHECKPOINT_URL": self.deployment.get_param("checkpoint_url"),
                            "DLTK_HDFS_URL": self.deployment.get_param("spark_hdfs_url"),
                            "DLTK_HDFS_PATH": self.get_hdfs_directory_path(),
                            "DLTK_FIELDS": ','.join(self.context.fields),
                        },
                        "env": [
                            {
                                "name": "SIGNALFX_AGENT_HOST",
                                "valueFrom": {
                                    "fieldRef": {
                                        "apiVersion": "v1",
                                        "fieldPath": "status.hostIP",
                                    }
                                }
                            }
                        ] if self.deployment.environment.has_sfx_smart_agent else [],
                        # "env": [
                        #    {
                        #        "name": "DLTK_ALGO",
                        #        "value": self.deployment.algorithm.name,
                        #    },
                        #    {
                        #        "name": "DLTK_SEARCH_ID",
                        #        "value": self.context.search_id,
                        #    },
                        #    {
                        #        "name": "DLTK_ALGO_METHOD",
                        #        "value": self.context.method,
                        #    },
                        #    {
                        #        "name": "DLTK_RECEIVER_COUNT",
                        #        "value": self.deployment.get_param("receiver_count"),
                        #    },
                        #    {
                        #        "name": "DLTK_BATCH_INTERVAL",
                        #        "value": self.deployment.get_param("batch_interval"),
                        #    },
                        #    {
                        #        "name": "DLTK_OUTBOUND_RELAY",
                        #        "value": outbound_relay_source_service.metadata.name,
                        #    },
                        #    {
                        #        "name": "DLTK_WAIT_TIME_BEFORE_STOP",
                        #        "value": self.deployment.get_param("wait_time_before_stop"),
                        #    },
                        #    {
                        #        "name": "DLTK_CHECKPOINT_URL",
                        #        "value": self.deployment.get_param("checkpoint_url"),
                        #    },
                        #    {
                        #        "name": "DLTK_HDFS_URL",
                        #        "value": self.deployment.get_param("spark_hdfs_url"),
                        #    },
                        #    {
                        #        "name": "DLTK_HDFS_PATH",
                        #        "value": self.get_hdfs_directory_path(),
                        #    },
                        # ],
                        "sidecars": [{
                            "image": self.driver_proxy_image,
                            "name": "proxy",
                            "imagePullPolicy": self.deployment.environment.image_pull_policy,
                            "ports": [{
                                "name": "api",
                                "protocol": "TCP",
                                "containerPort": 80,
                            }],
                        }],
                    },
                    "executor": {
                        "image": self.executor_image,
                        "coreRequest": str(self.executor_cores),
                        "coreLimit": str(self.executor_cores),
                        "instances": int(self.deployment.get_param("executor_instance_count")),
                        "memory": "%sm" % self.deployment.get_param("executor_memory_mb"),
                        "labels": self.deployment.generate_object_labels(self.get_object_labels({
                            "component": "executor",
                        })),
                    }
                }
            }
        )

    def deploy_inbound_relay(self):
        env = []
        deployment_ports = [
            kubernetes_client.V1ContainerPort(
                container_port=8888,
                name="source",
                protocol="TCP"
            ),
            kubernetes_client.V1ContainerPort(
                container_port=8889,
                name="status",
                protocol="TCP"
            ),
        ]
        inbound_relay_ports = [
            kubernetes_client.V1ServicePort(
                name="status",
                port=82,
                protocol="TCP",
                target_port="status",
            ),
        ]
        env.append(kubernetes_client.V1EnvVar(
            name="HDFS_PATH",
            value=self.get_hdfs_directory_path(),
        ))
        env.append(kubernetes_client.V1EnvVar(
            name="HDFS_SINK_URL",
            value=self.relay_hdfs_url,
        ))

        if self.deployment.environment.has_sfx_smart_agent:
            env.append(kubernetes_client.V1EnvVar(
                name="SIGNALFX_AGENT_HOST",
                value_from=kubernetes_client.V1EnvVarSource(
                    field_ref=kubernetes_client.V1ObjectFieldSelector(
                        api_version="v1",
                        field_path="status.hostIP",
                    ),
                ),
            ))

        relay_deployment = self.deployment.deploy_deployment(
            name_suffix=self.generate_object_name_suffix("inbound-relay"),
            container_name="relay",
            image=self.deployment.get_param("inbound_relay_image"),
            cpu_request=self.deployment.get_param("inbound_relay_cpu_request"),
            cpu_limit=self.deployment.get_param("inbound_relay_cpu_limit"),
            memory_mb=int(self.deployment.get_param("inbound_relay_memory_mb")),
            ports=deployment_ports,
            deployment_labels=self.get_object_labels({
                "component": "inbound-relay",
            }),
            pod_labels=self.get_object_labels({
                "component": "inbound-relay",
            }),
            env=env,
        )
        inbound_relay_service = self.deployment.deploy_service(
            title=self.generate_object_name_suffix("inbound-relay-sink"),
            ports=inbound_relay_ports,
            pod_labels=self.get_object_labels({
                "component": "inbound-relay",
            }),
            service_labels=self.get_object_labels({
                "component": "inbound-relay-sink",
            }),
        )
        self.deployment.expose_pods(
            name=self.inbound_relay_source_name_suffix,
            pod_port="source",
            pod_labels=self.get_object_labels({
                "component": "inbound-relay",
            }),
            labels=self.get_object_labels({
                "component": "inbound-relay-source",
            }),
            rewrite_path=True,
        )
        return inbound_relay_service

    def deploy_outbound_relay(self):
        env = []
        if self.deployment.environment.has_sfx_smart_agent:
            env.append(kubernetes_client.V1EnvVar(
                name="SIGNALFX_AGENT_HOST",
                value_from=kubernetes_client.V1EnvVarSource(
                    field_ref=kubernetes_client.V1ObjectFieldSelector(
                        api_version="v1",
                        field_path="status.hostIP",
                    ),
                ),
            ))
        self.deployment.deploy_deployment(
            name_suffix=self.generate_object_name_suffix("outbound-relay"),
            container_name="relay",
            image=self.deployment.get_param("outbound_relay_image"),
            cpu_request=self.deployment.get_param("outbound_relay_cpu_request"),
            cpu_limit=self.deployment.get_param("outbound_relay_cpu_limit"),
            memory_mb=int(self.deployment.get_param("outbound_relay_memory_mb")),
            ports=[
                kubernetes_client.V1ContainerPort(
                    container_port=8888,
                    name="source",
                    protocol="TCP"
                ),
                kubernetes_client.V1ContainerPort(
                    container_port=8890,
                    name="sink",
                    protocol="TCP"
                ),
                kubernetes_client.V1ContainerPort(
                    container_port=8889,
                    name="status",
                    protocol="TCP"
                ),
            ],
            deployment_labels=self.get_object_labels({
                "component": "outbound-relay",
            }),
            pod_labels=self.get_object_labels({
                "component": "outbound-relay",
            }),
            env=env,
        )
        # self.logger.warning("waiting to become ready...")
        # while True:
        #     time.sleep(1)
        #     relay_deployment = self.deployment.get_deployment(
        #         label_selector=self.get_object_labels({
        #             "component": "outbound-relay",
        #         }),
        #     )
        #     if self.deployment.is_deployment_ready(relay_deployment):
        #         break
        outbound_relay_source_service = self.deployment.deploy_service(
            title=self.generate_object_name_suffix("outbound-relay-source"),
            ports=[
                kubernetes_client.V1ServicePort(
                    name="source",
                    port=81,
                    protocol="TCP",
                    target_port="source",
                ),
                kubernetes_client.V1ServicePort(
                    name="status",
                    port=82,
                    protocol="TCP",
                    target_port="status",
                ),
            ],
            pod_labels=self.get_object_labels({
                "component": "outbound-relay",
            }),
            service_labels=self.get_object_labels({
                "component": "outbound-relay-source",
            }),
        )
        self.deployment.expose_pods(
            name=self.outbound_relay_sink_name_suffix,
            pod_port="sink",
            pod_labels=self.get_object_labels({
                "component": "outbound-relay",
            }),
            labels=self.get_object_labels({
                "component": "outbound-relay-sink",
            }),
            rewrite_path=True,
        )
        return outbound_relay_source_service

    def wait_for_relay(self, relay_url, path="ping"):
        self.logger.warning("waiting for relay with URL %s ..." % relay_url)
        if path:
            ping_url = urllib.parse.urljoin(relay_url, path)
        else:
            ping_url = relay_url
        self.logger.info("ping_url: %s" % ping_url)
        retries = 0
        while True:
            error_code = 0
            with opentracing.tracer.start_active_span(
                "ping_relay",
                tags={
                    opentracing.ext.tags.SPAN_KIND: opentracing.ext.tags.SPAN_KIND_RPC_CLIENT,
                },
            ):
                try:
                    request = urllib.request.Request(ping_url, method="GET")
                    response = urllib.request.urlopen(request)
                    return
                except urllib.error.HTTPError as e:
                    self.logger.info("HTTPError: %s" % e)
                    error_code = e.code
            if error_code != 404 and error_code != 503 and error_code != 502 and error_code != 504:
                raise Exception("Error connecting relay: %s" % error_code)
            if retries > 600:
                raise Exception("Relay not ready after %s attempts (code %s)" % (retries, error_code))
            retries += 1
            time.sleep(1)
