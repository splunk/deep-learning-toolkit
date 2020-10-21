# Build Guide

This guide is intended for DLTK developers and anyone who wants to build the DLTK app as well as the container images required by DLTK runtimes.

The [`build`](../../build) folder, located in the root of this repository, contains a AWS CodeBuild specification. It contains all the steps required for setting up the environment, building and testing DLTK:

- Building runtime container images
- Packaging the DLTK Splunk app
- Settings up a local Kubernetes cluster (k3d)
- Instelling an Ingress Controller (HAProxy)
- Starting a HDFS Cluster
- Installing the Spark Operator
- Installing the Splunk Operator
- Starting a Splunk Enterprise instance
- Installing and configuring the DLTK Splunk app
- Running all the tests

If you want to run builds in our AWS account, please see the [AWS CodeBuild](https://docs.aws.amazon.com/codebuild/latest/userguide/welcome.html) use guide.

If you want to run builds locally, please see the [Announcing Local Build Support for AWS CodeBuild](<https://aws.amazon.com/blogs/devops/announcing-local-build-support-for-aws-codebuild/>) blog post. This repository contains a helper script to kick of the local build.
