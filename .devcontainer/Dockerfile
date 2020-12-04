# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.148.1/containers/python-3/.devcontainer/base.Dockerfile

#FROM splunk/splunk:8.0-debian
FROM python:3.7

# [Optional] If your pip requirements rarely change, uncomment this section to add them to the image.
COPY requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
    && rm -rf /tmp/pip-tmp

# [Optional] Uncomment this section to install additional OS packages.
#RUN apt-get update \
#    && apt-get -y install --no-install-recommends git

RUN git config --global core.autocrlf true
#RUN git config --global user.email "you@example.com"
#RUN git config --global user.name "Your Name"
