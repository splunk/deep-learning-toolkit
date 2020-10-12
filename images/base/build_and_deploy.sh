#!/bin/bash
set -e
set -x

./build.sh golden-image-gpu-4 phdrieger/ 4.0.0
docker tag phdrieger/mltk-container-golden-image-gpu-4:4.0.0 hovu96/dltk-golden-image-gpu:4.0.0
docker push hovu96/dltk-golden-image-gpu:4.0.0