#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
BUILD_DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
PROJECT_DIR=$(dirname "$BUILD_DIR")
ARTIFACT_DIR="$BUILD_DIR/artifact"

set -e

# https://github.com/aws/aws-codebuild-docker-images/tree/master/local_builds

./codebuild_build.sh -i aws/codebuild/standard:4.0 -a "$ARTIFACT_DIR" -s "$PROJECT_DIR" -b "$BUILD_DIR/buildspec.yml"
