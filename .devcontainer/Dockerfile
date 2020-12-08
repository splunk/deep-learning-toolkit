# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.148.1/containers/python-3/.devcontainer/base.Dockerfile

FROM docker:dind

# Install Bash
RUN apk update && apk upgrade && apk add bash bash-doc bash-completion

# Install CLI tools
RUN apk add git curl \
    && rm /var/cache/apk/*

# Install Python
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

# Install Kubectl
RUN /usr/bin/curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl \
    && chmod +x ./kubectl  \
    && mv ./kubectl /usr/bin/kubectl

# Install Helm
#RUN curl -s https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash -

# Install KIND
RUN curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.9.0/kind-linux-amd64 \
    && chmod +x ./kind \
    && mv ./kind /usr/bin/kind

# Install Python Dependencies
COPY requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
    && rm -rf /tmp/pip-tmp

RUN git config --global core.autocrlf true

