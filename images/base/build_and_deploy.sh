#!/bin/bash
set -e
set -x

./build.sh golden-image-gpu-4 phdrieger/ 4.1.0
docker tag phdrieger/mltk-container-golden-image-gpu-4:4.1.0 phdrieger/dltk-base-golden-image-gpu:4.1.0
docker push phdrieger/dltk-base-golden-image-gpu:4.1.0