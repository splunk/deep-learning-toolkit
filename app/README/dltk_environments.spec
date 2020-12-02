


[<environment_name>]

connector =
* Required.

#######################################################################
# Kubernetes connector settings

node_port_url = <string>
* See dltk_connectors.conf.spec for details.
* Defaults what's set 'node_port_url' in the 'kubernetes' connector.

auth_mode = [cert-key|aws-iam|user-token|in-cluster]
* See dltk_connectors.conf.spec for details.
* Defaults what set set 'auth_mode' in the 'kubernetes' connector.

namespace = <string>
* See dltk_connectors.conf.spec for details.
* Defaults what set set 'namespace' in the 'kubernetes' connector.

storage_class = <string>
* See dltk_connectors.conf.spec for details.
* Defaults what set set 'storage_class' in the 'kubernetes' connector.

node_selector = <string>
* See dltk_connectors.conf.spec for details.
* Defaults what set set 'node_selector' in the 'kubernetes' connector.

aws_access_key_id = <string>
* See dltk_connectors.conf.spec for details.
* Defaults what set set 'aws_access_key_id' in the 'kubernetes' connector.

aws_cluster_name = <string>
* See dltk_connectors.conf.spec for details.
* Defaults what set set 'aws_cluster_name' in the 'kubernetes' connector.

aws_region_name = <string>
* See dltk_connectors.conf.spec for details.
* Defaults what set set 'aws_region_name' in the 'kubernetes' connector.

aws_secret_access_key = <string>
* See dltk_connectors.conf.spec for details.
* Defaults what set set 'aws_secret_access_key' in the 'kubernetes' connector.

ingress_url = <string>
* See dltk_connectors.conf.spec for details.
* Defaults what set set 'ingress_url' in the 'kubernetes' connector.

ingress_class = <string>
* See dltk_connectors.conf.spec for details.
* Defaults what set set 'ingress_class' in the 'kubernetes' connector.

ingress_mode = [ingress|load-balancer|node-port|route]
* See dltk_connectors.conf.spec for details.
* Defaults what set set 'ingress_mode' in the 'kubernetes' connector.

image_pull_policy = <string>
* See dltk_connectors.conf.spec for details.
* Defaults what set set 'image_pull_policy' in the 'kubernetes' connector.

image_pull_secret = <string>
* See dltk_connectors.conf.spec for details.
* Defaults what set set 'image_pull_secret' in the 'kubernetes' connector.

client_cert = <string>
* Defaults what set set 'client_cert' in the 'kubernetes' connector.

client_key = <string>
* Defaults what set set 'client_key' in the 'kubernetes' connector.

cluster_ca = <string>
* Defaults what set set 'cluster_ca' in the 'kubernetes' connector.

user_token = <string>
* Defaults what set set 'user_token' in the 'kubernetes' connector.

cluster_url = <string>
* Defaults what set set 'cluster_url' in the 'kubernetes' connector.

user_password = <string>
* Defaults what set set 'user_password' in the 'kubernetes' connector.

user_name = <string>
* Defaults what set set 'user_name' in the 'kubernetes' connector.
