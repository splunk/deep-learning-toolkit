[<algorithm>:<environment>]

guid = <string>
* Globally unique identifier which is generated automatically by DLTK when creating Deployments.
* Used to distinguish deployments from deployments on other Splunk environments.

status = [deploying|deployed|undeploying|disabling|disabled|error]
* Status of the deployment which is automatically updated by the DLTK runtime.

status_message = <string>
* Message explaining or describing the status of the deployment.
* Automatically updated by the DLTK runtime.

editor_url = <string>
* URL of the an editor for the algorithm source code.

editable = <bool>
* TODO

restart_required = <bool>
* TODO

cpu_count = <number>
* Number of CPU cores to be requested for the deployment 

gpu_request = <number>
* Number of GPUs to be requested for the deployment

runtime_status.api_url = <string>
* Current state of the deployment API endpoint
* Typically contains the URL of the API endpoint