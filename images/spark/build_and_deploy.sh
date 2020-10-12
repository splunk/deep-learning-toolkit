#!/bin/bash
set -e
set -x

# editor
docker build --rm -f "./editor/thin.Dockerfile" -t hovu96/dltk-spark-runtime:editor-thin .
docker push hovu96/dltk-spark-runtime:editor-thin

# driver
docker build --rm -f "./driver/thin.Dockerfile" -t hovu96/dltk-spark-runtime:driver-thin .
docker push hovu96/dltk-spark-runtime:driver-thin

# driver-proxy
docker build --rm -f "./driver-proxy/Dockerfile" -t hovu96/dltk-spark-runtime:driver-proxy .
docker push hovu96/dltk-spark-runtime:driver-proxy

# inbound-relay
docker build --rm -f "./inbound-relay/Dockerfile" -t hovu96/dltk-spark-runtime:inbound-relay .
docker push hovu96/dltk-spark-runtime:inbound-relay

# outbound-relay
docker build --rm -f "./outbound-relay/Dockerfile" -t hovu96/dltk-spark-runtime:outbound-relay .
docker push hovu96/dltk-spark-runtime:outbound-relay
