# Kubernetes

For connecting DLTK to a Kubernetes environment, please use the `kubernetes` *Connector* in the *Create Environment* dialog. Depending on the type of Kubernetes environment you must also specify additional fields. This guide describes how this works for typical Kubernetes distributions.

If you want to create a new *Environment*, please see the [Connect to Environments](README.md) documentation.

## Docker Desktop

Docker Desktop is an application for MacOS and Windows machines. It ships with a fully functional Kubernetes environment on your desktop.

If you want to learn more about Docker Desktop, please see the official [Docker Desktop](https://www.docker.com/products/docker-desktop) product documentation.

The following steps describe how to connect DLTK to Docker Desktop, running on the same host:

1. Download and install Docker Desktop for Windows or Linux from https://www.docker.com/get-started
2. Open the Docker Desktop settings window, select the *Kubernetes* page and check *Enable Kubernetes*
3. Click the *Apply & Restart* button and wait until Kubernetes is running
4. Open the *kubeconfig* file which is typically located in `~/.kube/config`
5. In the *Create Environment* dialog (see [Connect to Environments](README.md)) make sure the following fields are specified:
    - Set *Auth Mode* to `cert-key`
    - Set *Cluster Url* to `https://kubernetes.docker.internal:6443`
    - Set *Client Cert* to value of `client-certificate-data` in the *kubeconfig*
    - Set *Cluster Ca* to value of `certificate-authority-data` in the *kubeconfig*
    - Set *Client Key* to value of `client-key-data` in the *kubeconfig*
    - Set *Ingress Mode* to `node-port`
    - Set *Node Port Url* to `http://localhost`
    - Set *Storage Class* to `hostpath`

## MicroK8s

MicroK8s is the smallest, fastest, fully-conformant Kubernetes that tracks upstream releases and makes clustering trivial. MicroK8s is great for offline development, prototyping, and testing. If you want to learn more about MicroK8s, please see the official [MicroK8s](https://microk8s.io/docs) product documentation.

The following steps describe how to connect DLTK to MicroK8s, running on the same host:

1. Download and install MicroK8s for Windows, Linux or MacOS from the official [MicroK8s](https://microk8s.io/) site
2. Perform the setup on the CLI to start [MicroK8s](https://microk8s.io/docs)
3. Verify that MicroK8s is running and enable add-ons:
    - Enable dns and storage with `microk8s enable dns storage`
    - Optionally, if you have GPU accessible and properly configured you can enable gpu with `microk8s enable gpu`
    - Enable ingress with `microk8s enable ingress` and modify the ingress configmap using `microk8s kubectl edit configmap -n ingress nginx-load-balancer-microk8s-conf` with the following changes to be added to:
        - `data:`
            - `  proxy-body-size: "0"`
            - `  proxy-read-timeout: "100000"`
            - `  proxy-connect-timeout: "100000"`
            - `  ssl-redirect: "false"`
4. Display the *microk8sconfig* with `microk8s config` and use to fill the information in the following step 5
5. In the *Create Environment* dialog (see [Connect to Environments](README.md)) make sure the following fields are specified:
    - Set *Auth Mode* to `user-password`
    - Set *Cluster Url* to the value `server` of your cluster in the *microk8sconfig*, e.g. `https://your-microk8s-host-or-ip-or-localhost:16443`
    - Set *Cluster Ca* to value of `certificate-authority-data` in the *microk8sconfig*
    - Set *Ingress Mode* to `ingress`
    - Set *Ingress Class* to `nginx`
    - Set *Ingress Url* to the value `server` of your cluster in the *microk8sconfig*, e.g. `http://your-microk8s-host-or-ip-or-localhost` or https if you configure microk8s ingress with certificates
    - Set *User Name* to value of `username` of your user in *microk8sconfig*
    - Set *User Password* to value of `password` of your user in *microk8sconfig*



## Amazon Elastic Kubernetes Service (EKS)

EKS is a fully managed Kubernetes service.

If you want to learn more about EKS, please see the official [Amazon Elastic Kubernetes Service](https://aws.amazon.com/eks/) product documentation.

The following steps describe how to connect DLTK to EKS cluster:

1. Set up and log into your [AWS account](https://portal.aws.amazon.com/billing/signup)
2. Create a EKS cluster by following the [Getting started with Amazon EKS](https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html) guide
3. Setup an [Ingress Controller](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/) in your EKS cluster
4. In the *Create Environment* dialog (see [Connect to Environments](README.md)) make sure the following fields are specified:
    - Set *Auth Mode* to `aws-iam`
    - Set *Aws Access Key Id* to your [IAM Access Key](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html)
    - Set *Aws Secret Access Key* to [IAM Access Secret](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html)
    - Set *Aws Cluster Name* to the name of your EKS cluster
    - Set *Aws Region Name* to the name of the AWS region the EKS cluster runs in
    - Set *Ingress Mode* to `ingress`
    - Set *Ingress Url* to the url of yor *Ingress Controller*
    - Set *Storage Class* to `gp2`

## Azure Kubernetes Service (AKS)

If you want to learn more about AKS, please see the official [Azure Kubernetes Service](https://azure.microsoft.com/en-us/services/kubernetes-service/) product documentation.

## Google Kubernetes Engine (GKE)

If you want to learn more about GKE, please see the official [Google Kubernetes Engine](https://cloud.google.com/kubernetes-engine) product documentation.
