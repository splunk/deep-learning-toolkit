# Test Guide

This guide is intended for DLTK developers and anyone who wants to create and run DLTK tests.

## Running Tests

The main script for running tests is [`test/test.py`](../../test/test.py), located in the root of the repository. The following sections describe possible ways for executing the test script.

### From Shell

The most straightforward approach is running the [test/test.bash](../../test/test.bash) shell script.

The following illustrates the how to run the tests:

```bash
cd $DLTK_REPO/test
./test.bash
```

Requirements:

- A Splunk Enterprise instance is running at `$SPLUNK_HOME` on the same host
- The environment variable `SPLUNK_PASSWORD` is set to the password of the *admin* user of the Splunk instance
- The DLTK Splunk app is installed on the instance (typically by symlinking the `app` folder to `SPLUNK_HOME/etc/apps/dltk`)
- DLTK is already configured and connected a Kubernetes execution environment.
- The environment variable `DLTK_ENVIRONMENT` is set to the name of the Kubernetes execution environment
- The environment variable `DLTK_APP_NAME` is set to the name of the DLTK Splunk app (defaults to `dltk`)

### From Visual Studio Code

This repository contains Visual Stop Code configuration, including a *Task* definition (see [.vscode/tasks.json](../../.vscode/tasks.json)) for running the tests.

Use the keyboard shortcut `Ctrl+Shift+P` to open the command palette and enter `Tasks: Run Test Task`.

Optionally, environment variables (like `DLTK_ENVIRONMENT` and `SPLUNK_PASSWORD`) can be defined in the file `run.env`, located in the [test/](../../test/) folder. For example:

```bash
DLTK_ENVIRONMENT="my-kubernetes-cluster"
SPLUNK_PASSWORD="changeme"`
```

Note: Since the task wraps the [test/test.bash](../../test/test.bash) shell script, the same requirements apply here.

### From Building DLTK

One of the steps that are part of the DLTK build process is running the tests.

If you are looking for documentation on how to build DLTK, please see the [Build Guide](build.md).

## Creating Tests

If you want to create and add tests for DLTK, create the test_*.py file in the module that contains the code that you want to test.

Tests are build using the <https://docs.python.org/3/library/unittest.html> Python testing framework.

TODO: Explain the different type of tests and provide a examples
