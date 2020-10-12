[kubernetes]
auth_mode = [cert-key|aws-iam|user-token|in-cluster]
ingress_mode = [ingress|load-balancer|node-port|route]

tag_label = <string>
* Opaque name used for the "tag" label for all Kubernetes objects, being created by this connector.
* Typically this is not used. Internal CI uses it in order to clean up after running integration tests.
* Optional.
