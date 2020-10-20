# Kubernetes

For connecting DLTK to a Kubernetes environment, please use the `kubernetes` *Connector* in the *Create Environment* dialog. Depending on the type of Kubernetes environment you must also specify additional fields. This guide describes how this works for typical Kubernetes Distributions.

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
