# Integration Testing

This repository folder contains a couple of integration tests. The tests are build using <https://docs.python.org/3/library/unittest.html> testing framework.

## Running the Tests

### CLI Command

The most simple command for running the tests is:

`$SPLUNK_HOME/bin/splunk cmd python3 -m unittest discover -s .`

The above command discovers and runs all unit tests located in this folder.

Requirements:

- A Splunk Enterprise instance is running at *$SPLUNK_HOME* on the same host
- The environment variable *SPLUNK_PASSWORD* is set to the password of the *admin* user of the Splunk instance
- The DLTK Splunk app is installed on the instance (typically by symlinking the app folder to *SPLUNK_HOME/etc/apps/dltk*)
- DLTK is already configured and connected a Kubernetes execution environment.
- The environment variable *DLTK_ENVIRONMENT* is set to the name of the Kubernetes execution environment
- The environment variable *DLTK_APP_NAME* is set to the name of the DLTK Splunk app (defaults to *dltk*)

## Visual Studio Code Task

This repository contains Visual Stop Code configuration, including a *Task* definition for running the above CLI command.

Simply use the keyboard shortcut `Ctrl+Shift+P` to open the command palette and enter `Tasks: Run Test Task`.

Optionally, environment variables (like *DLTK_ENVIRONMENT* and *SPLUNK_PASSWORD*) can be defined in the file *run.env*, located in this folder.

For example *run.env* file content:

`DLTK_ENVIRONMENT="my-kubernetes-cluster"
SPLUNK_PASSWORD="changeme"`

Note: Since the task wraps the CLI command, the same requirements apply here.

## AWS CodeBuild

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
