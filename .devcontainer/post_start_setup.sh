#!/bin/bash

set -e
set -x

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "Creating KIND cluster ..."
kind create cluster --wait 5m --name dltk --config=$DIR/kind.yaml
kubectl create clusterrolebinding default-service-account-cluster-admin  --clusterrole=cluster-admin --serviceaccount=default:default

echo "Deploying NGINX ingress controller ..."
kubectl apply -f $DIR/ingress-nginx.yaml
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=5m

echo "Deploying Splunk ..."
kubectl create configmap splunk-defaults --from-file=$DIR/default.yml
kubectl apply -f $DIR/splunk.yaml
kubectl wait \
  --for=condition=ready pod \
  --selector=app=splunk \
  --timeout=5m

echo "Setting up Splunk ..."
python $DIR/setup_splunk.py > $DIR/setup_splunk.log

echo "Done."
