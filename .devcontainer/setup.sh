#!/bin/bash -i

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

kind create cluster --wait 5m --name dltk --config=$DIR/kind.yaml

kubectl apply -f $DIR/ingress-nginx.yaml
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s

kubectl create configmap splunk-defaults --from-file=$DIR/default.yml
kubectl apply -f $DIR/splunk.yaml
