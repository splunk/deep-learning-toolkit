#!/bin/sh
image="dltk4splunk/h2o-runtime:devel"
docker stop $image
docker rm $image
docker rmi $image
docker build --rm -t $image -f Dockerfile .

