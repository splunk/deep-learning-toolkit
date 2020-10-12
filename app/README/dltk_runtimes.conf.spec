[<uniqueName>]

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
* Number of CPU cores for Spark executors,
* Defaults to 2
