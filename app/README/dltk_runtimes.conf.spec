[<uniqueName>]

deployment_params = <param_name>, <param_name>, ...
* Name of Deployment parameters users can configure values in UI
* Optional.

algorithm_params = <param_name>, <param_name>, ...
* Name of Algorithm parameters users can configure values in UI
* Optional.

handler = <string>
* Name of the Python class implementing the low level parameter handling.
* A typical runtime does not need to specify this.
* Syntax: <module_name>.<class_name> (e.g. myruntime.MyRuntimeDeployment)
* Optional.

connector = <string>
* Name of the DLTK Connector (as defined in dltk_connectors.conf) to use for this DLTK Runtime
* E.g. kubernetes

deployment_handler = <string>
* Name of the Python class implementing the deployment process of a DLTK Algorithm.
* Typically DLTK runtimes use a deployment handler for customizing the deployment and undeployment processes.
* Syntax: <module_name>.<class_name> (e.g. myruntime.MyRuntimeDeployment)
* Optional.

execution_handler = <string>
* Name of the Python class implementing the execution process of a DLTK Algorithm.
* DLTK runtimes may use an execution handler for more complex executions. See methods of 'deployment.Execution' base class for details.
* Syntax: <module_name>.<class_name> (e.g. myruntime.MyRuntimeExecution)
* Optional.

algorithm_handler = dltk.core.algorithm.Algorithm
* Name of the Python class implementing default configuration handling of a DLTK Algorithm.
* DLTK runtimes may provide a runtime-specific handler for customizing config behaviour.
* Syntax: <module_name>.<class_name> (e.g. myruntime.MyRuntimeAlgorithm)
* Optional.

source_code = <string>
* Default/Template source code to use for new DLTK Algorithms created for the DLTK Runtime.
* The syntax is DLTK runtime-specific (e.g. for the "spark" runtime, this is the Jupyter notebook source code).
* DLTK treads it as an opaque string.
* Optional.

deployment_code = <string>
* The syntax is DLTK runtime-specific (e.g. for the "spark" runtime, this is source code of a python module).
* No need to explicitly specify this attribute, simply use the algorithm's "update_deployment_code" method.
* DLTK treads it as an opaque string.
* Optional.


[spark]

input_hdfs_data_path = [via_relay|direct]
* Specifies how to send input data to Spark.
* Defaults to 'via_relay'

executor_instance_count = <number>
* Number of Spark executors - responsible for running the tasks.
* Defaults to 2

executor_cores = <number>
* Number of CPU cores for Spark executors.
* Required.

editor_cpu_request = <number>
* Number of CPU cores to request for the editor.
* Required.

editor_cpu_limit = <number>
* Number of CPU cores (as limit) for the editor.
* Required.

editor_memory_mb = <number>
* Memory to request (in MB) for the editor.
* Required.

editor_image = <imageref>
* Container image for the editor.
* Syntax: [hostname[:port]/]username/reponame[:tag]
* Required.

driver_image = <imageref>
* Container image for the driver.
* Syntax: [hostname[:port]/]username/reponame[:tag]
* Required.

driver_proxy_image = <imageref>
* Container image for the driver proxy.
* Syntax: [hostname[:port]/]username/reponame[:tag]
* Required.

driver_memory_mb = <number>
* Memory to request (in MB) for the driver.
* Required.

inbound_relay_cpu_request = <number>
* Number of CPU cores to request for the inbound relay.
* Required.

inbound_relay_cpu_limit = <number>
* Number of CPU cores (as limit) for the inbound relay.
* Required.

inbound_relay_memory_mb = <number>
* Memory to request (in MB) for the inbound relay.
* Required.

inbound_relay_image = <imageref>
* Container image for the inbound relay.
* Syntax: [hostname[:port]/]username/reponame[:tag]
* Required.

outbound_relay_cpu_request = <number>
* Number of CPU cores to request for the outbound relay.
* Required.

outbound_relay_cpu_limit = <number>
* Number of CPU cores (as limit) for the outbound relay.
* Required.

outbound_relay_memory_mb = <number>
* Memory to request (in MB) for the outbound relay.
* Required.

outbound_relay_image = <imageref>
* Container image for the outbound relay.
* Syntax: [hostname[:port]/]username/reponame[:tag]
* Required.

executor_memory_mb = <number>
* Memory to request (in MB) for the executor.
* Required.

executor_image = <imageref>
* Container image for the executor.
* Syntax: [hostname[:port]/]username/reponame[:tag]
* Required.

spark_hdfs_url = <url>
* Container image for the executor.
* Syntax: [hostname[:port]/]username/reponame[:tag]
* Required.

relay_hdfs_url = <url>

spark_service_account

checkpoint_url = <url>

checkpoint_s3_access_key = <string>

checkpoint_s3_secret_key = <string>

receiver_count = <number>
* Number of Spark receivers.
* Required.

batch_interval = <number>

spark_service_account = <string>

[base]

image = <imageref>
* Container image.
* Syntax: [hostname[:port]/]username/reponame[:tag]
* Required.

cpu_count = <number>
* Number of CPU cores to request for the container.
* Required.

memory_mb = <number>
* Memory to request (in MB) for the container.
* Required.

store_models_in_volume = <bool>
* Whether or not to store models on a volume.
* Required.