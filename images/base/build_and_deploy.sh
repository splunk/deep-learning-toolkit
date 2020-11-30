#!/bin/bash
set -e
set -x

./build.sh golden-image-gpu-4 phdrieger/ 4.2.1
docker tag phdrieger/mltk-container-golden-image-gpu-4:4.2.1 phdrieger/dltk-base-golden-image-gpu:4.2.1
#docker push phdrieger/dltk-base-golden-image-gpu:4.2.1