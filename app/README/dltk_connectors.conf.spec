
[<connector_name>>]
handler = <string>
environment_handler = <string>
environment_params = <string>

[kubernetes]

tag_label = <string>
* Opaque name used for the "tag" label for all Kubernetes objects, being created by this connector.
* Typically this is not used. Internal CI uses it in order to clean up after running integration tests.
* Optional.

node_port_url = <string>
auth_mode = [cert-key|aws-iam|user-token|in-cluster]
namespace = <string>
storage_class = <string>
node_selector = <string>
aws_access_key_id = <string>
aws_cluster_name = <string>
aws_region_name = <string>
aws_secret_access_key = <string>

ingress_url = <string>
ingress_class = <string>
ingress_mode = [ingress|load-balancer|node-port|route]
image_pull_policy = <string>
image_pull_secret = <string>