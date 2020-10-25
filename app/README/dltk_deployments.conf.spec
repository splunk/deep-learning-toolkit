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