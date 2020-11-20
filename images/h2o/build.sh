#!/bin/sh
image="dltk4splunk/h2o-runtime:devel"
docker stop $image
docker rm $image
docker rmi $image
docker build --rm -t $image -f Dockerfile .

#docker tag phdrieger/mltk-container-golden-image-gpu-4:4.1.0 phdrieger/dltk-base-golden-image-gpu:4.1.0
#docker push phdrieger/dltk-base-golden-image-gpu:4.1.0