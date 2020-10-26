#!/bin/bash

# This script builds the container images using the local docker CLI. The first argument is the image ref account/user name, the second argument is the tag name.
# Requirements: Docker CLI
# Example usage: build_images.bash dltk4splunk devel

set -e
set -x

BUILD_DIR="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

DOCKER_ACCOUNT=$1
BUILD_TAG_NAME=$2
source $BUILD_DIR/set_image_refs.bash
IMAGES_DIR=$BUILD_DIR/../images

# build spark-runtime images
cd $IMAGES_DIR/spark
docker build --rm -f "./driver/thin.Dockerfile" -t $DLTK_SPARK_RUNTIME_DRIVER_IMAGE .
docker build --rm -f "./driver/thin.Dockerfile" -t $DLTK_SPARK_RUNTIME_EXECUTOR_IMAGE .
docker build --rm -f "./driver-proxy/Dockerfile" -t $DLTK_SPARK_RUNTIME_DRIVER_PROXY_IMAGE .
docker build --rm -f "./editor/thin.Dockerfile" -t $DLTK_SPARK_RUNTIME_EDITOR_IMAGE .
docker build --rm -f "./inbound-relay/Dockerfile" -t $DLTK_SPARK_RUNTIME_INBOUND_RELAY_IMAGE .
docker build --rm -f "./outbound-relay/Dockerfile" -t $DLTK_SPARK_RUNTIME_OUTBOUND_RELAY_IMAGE .

# build base-runtime images
cd $IMAGES_DIR/base
./build.sh golden-image-gpu-4 phdrieger/ 4.0.0
docker tag phdrieger/mltk-container-golden-image-gpu-4:4.0.0 $DLTK_BASE_RUNTIME_IMAGE
