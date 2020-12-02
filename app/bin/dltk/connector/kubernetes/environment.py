from kubernetes import client as kubernetes_client, config as kubernetes_config

import base64
import tempfile
import re
from dltk.core.deployment import status as deployment_status
import urllib
import http
from dltk.core import is_truthy
from dltk.core.environment import Environment


class KubernetesEnvironment(Environment):

    @property
    def namespace(self):
        return self.get_param("namespace")

    @property
    def storage_class(self):
        return self.get_param("storage_class")

    @property
    def auth_mode(self):
        return self.get_param("auth_mode")

    @property
    def aws_region_name(self):
        return self.get_param("aws_region_name")

    @property
    def aws_access_key_id(self):
        return self.get_param("aws_access_key_id")

    @property
    def aws_secret_access_key(self):
        return self.get_param("aws_secret_access_key")

    @property
    def aws_cluster_name(self):
        return self.get_param("aws_cluster_name")

    @property
    def client_cert(self):
        return self.get_param("client_cert")

    @property
    def client_key(self):
        return self.get_param("client_key")

    @property
    def cluster_ca(self):
        return self.get_param("cluster_ca")

    @property
    def user_token(self):
        return self.get_param("user_token")

    @property
    def user_name(self):
        return self.get_param("user_name")

    @property
    def user_password(self):
        return self.get_param("user_password")

    @property
    def cluster_url(self):
        return self.get_param("cluster_url")

    @property
    def image_pull_policy(self):
        return self.get_param("image_pull_policy")

    @property
    def image_pull_secret(self):
        return self.get_param("image_pull_secret")

    @property
    def ingress_mode(self):
        return self.get_param("ingress_mode")

    @property
    def tag_label(self):
        return self.get_param("tag_label")

    @property
    def ingress_base_url(self):
        if "ingress_url" in self._stanza:
            return self._stanza["ingress_url"]
        else:
            return None

    @property
    def node_port_url(self):
        if "node_port_url" in self._stanza:
            return self._stanza["node_port_url"]
        else:
            return None

    @property
    def ingress_class(self):
        if "ingress_class" in self._stanza:
            return self._stanza["ingress_class"]
        else:
            return None

    @property
    def has_sfx_smart_agent(self):
        if "sfx_smart_agent" in self._stanza:
            return is_truthy(self._stanza["sfx_smart_agent"])
        else:
            return None

    def create_api_client(self):
        client_config = self.create_client_config()
        return kubernetes_client.ApiClient(client_config)

    def create_client_config(self):
        config = kubernetes_client.Configuration()

        if self.auth_mode == "aws-iam":
            # https://github.com/kubernetes-sigs/aws-iam-authenticator
            # https://aws.amazon.com/de/about-aws/whats-new/2019/05/amazon-eks-simplifies-kubernetes-cluster-authentication/
            # https://github.com/aws/aws-cli/blob/develop/awscli/customizations/eks/get_token.py

            # get cluster info
            import boto3
            eks_client = boto3.client(
                'eks',
                region_name=self.aws_region_name,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
            cluster_info = eks_client.describe_cluster(name=self.aws_cluster_name)
            aws_cluster_ca = cluster_info['cluster']['certificateAuthority']['data']
            aws_cluster_url = cluster_info['cluster']['endpoint']

            # get authentication token
            from botocore.signers import RequestSigner  # pylint: disable=import-error
            STS_TOKEN_EXPIRES_IN = 60
            session = boto3.Session(
                region_name=self.aws_region_name,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
            sts_client = session.client('sts')
            service_id = sts_client.meta.service_model.service_id
            token_signer = RequestSigner(
                service_id,
                self.aws_region_name,
                'sts',
                'v4',
                session.get_credentials(),
                session.events
            )
            signed_url = token_signer.generate_presigned_url(
                {
                    'method': 'GET',
                    'url': 'https://sts.{}.amazonaws.com/?Action=GetCallerIdentity&Version=2011-06-15'.format(self.aws_region_name),
                    'body': {},
                    'headers': {
                        'x-k8s-aws-id': self.aws_cluster_name
                    },
                    'context': {}
                },
                region_name=self.aws_region_name,
                expires_in=STS_TOKEN_EXPIRES_IN,
                operation_name=''
            )
            base64_url = base64.urlsafe_b64encode(
                signed_url.encode('utf-8')).decode('utf-8')
            auth_token = 'k8s-aws-v1.' + re.sub(r'=*', '', base64_url)

            config.host = aws_cluster_url
            ca_data = base64.standard_b64decode(aws_cluster_ca)
            fp = tempfile.NamedTemporaryFile(delete=False)   # TODO when to delete?
            fp.write(ca_data)
            fp.close()
            config.ssl_ca_cert = fp.name
            config.api_key["authorization"] = auth_token
            config.api_key_prefix["authorization"] = "Bearer"

        elif self.auth_mode == "cert-key":
            config.host = self.cluster_url

            if self.client_cert:
                try:
                    cert_data = base64.standard_b64decode(
                        self.client_cert)
                    fp = tempfile.NamedTemporaryFile(
                        delete=False)   # TODO when to delete?
                    fp.write(cert_data)
                    fp.close()
                    config.cert_file = fp.name
                except Exception as e:
                    raise Exception("Error applying cluster cert: %s" % (e))

            if self.client_key:
                try:
                    key_data = base64.standard_b64decode(self.client_key)
                    fp = tempfile.NamedTemporaryFile(
                        delete=False)   # TODO when to delete?
                    fp.write(key_data)
                    fp.close()
                    config.key_file = fp.name
                except Exception as e:
                    raise Exception(
                        "Error applying cluster key: %s" % (e))

            if self.cluster_ca:
                try:
                    cluster_ca_data = base64.standard_b64decode(self.cluster_ca)
                    fp = tempfile.NamedTemporaryFile(
                        delete=False)   # TODO when to delete?
                    fp.write(cluster_ca_data)
                    fp.close()
                    config.ssl_ca_cert = fp.name
                except Exception as e:
                    raise Exception(
                        "Error applying cluster ca: %s" % (e))

            config.verify_ssl = False

        elif self.auth_mode == "user-token":
            # TODO: should cluster_ca be used here too?
            config.host = self.cluster_url
            config.api_key["authorization"] = self.user_token
            config.api_key_prefix["authorization"] = "Bearer"
            config.verify_ssl = False

        elif self.auth_mode == "user-password":
            if self.cluster_ca:
                try:
                    cluster_ca_data = base64.standard_b64decode(self.cluster_ca)
                    fp = tempfile.NamedTemporaryFile(
                        delete=False)   # TODO when to delete?
                    fp.write(cluster_ca_data)
                    fp.close()
                    config.ssl_ca_cert = fp.name
                except Exception as e:
                    raise Exception(
                        "Error applying cluster ca: %s" % (e))
            config.host = self.cluster_url

            import urllib3
            config.api_key["authorization"] = urllib3.util.make_headers(
                basic_auth=self.user_name + ':' + self.user_password
            ).get('authorization')

            config.verify_ssl = False

        elif self.auth_mode == "in-cluster":
            kubernetes_config.load_incluster_config()
            config = kubernetes_client.Configuration._default

        else:
            raise Exception("invalid auth mode '%s'" % self.auth_mode)

        return config
