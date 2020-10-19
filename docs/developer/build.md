# Build Guide


This folder contains a AWS CodeBuild build specification. It contains all the steps required for setting up a DLTK test environment:

- Building runtime container images
- Settings up a local Kubernetes cluster (k3d)
- Instelling an Ingress Controller (HAProxy)
- Starting a HDFS Cluster
- Installing the Spark Operator
- Installing the Splunk Operator
- Starting a Splunk Enterprice instance
- Installing and configuring the DLTK Splunk app
- Running all the tests

Unlike when using the plain CLI command or the Visual Studio Code Task, this is totally self-contained and has no external dependencies (except for the CodeBuild execution environment).

Use your AWS account and configure AWS CodeBuild to use the build specification, or run builds locally (see <https://aws.amazon.com/blogs/devops/announcing-local-build-support-for-aws-codebuild/> for details). There is a helper script (see `codebuild.sh`) which kicks of the local build script.
