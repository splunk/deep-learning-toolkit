#!/bin/sh
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export FLASK_APP=/dltk/app/index.py
export FLASK_DEBUG=0

umask 002
cp -R -n /dltk/app /srv
cp -R -n /dltk/data /srv
cp -R -n /dltk/examples /srv
cp /dltk/README.ipynb /srv

if [ -w /etc/passwd ]; then
  echo "dltk:x:$(id -u):0:dltk user:/dltk:/sbin/nologin" >> /etc/passwd
fi
export HOME=/dltk

jupyter lab --port=8888 --ip=0.0.0.0 --no-browser --LabApp.base_url=$JUPYTER_BASE_URL_PATH & tensorboard --bind_all --logdir /srv/notebooks/logs/ & mlflow ui -p 6000 -h 0.0.0.0 & flask run -h 0.0.0.0
