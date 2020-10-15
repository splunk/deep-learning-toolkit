FROM gcr.io/spark-operator/spark-py:v2.4.5

# root folder for everything that is dltk specific
ENV DLTK_DIR /dltk
RUN mkdir -p $DLTK_DIR

# install python packages
COPY pyspark-requirements.txt ${DLTK_DIR}/requirements.txt
RUN pip3 install --no-cache-dir -r ${DLTK_DIR}/requirements.txt
RUN pip3 install --no-cache-dir jupyterlab_server

# storage location for algos
ENV NOTEBOOK_PATH $DLTK_DIR/notebooks
RUN mkdir -p $NOTEBOOK_PATH
WORKDIR $NOTEBOOK_PATH

# dltk packages for algos
ENV DLTK_LIB_DIR $DLTK_DIR/libs
#COPY lib/ $DLTK_LIB_DIR/
RUN mkdir -p $DLTK_LIB_DIR

# configure pyspark
ENV PYSPARK_PYTHON /usr/bin/python3
ENV PYSPARK_DRIVER_PYTHON /usr/bin/python3
ENV DLTK_EDITOR 1

# jupyter editor
ENV EDITOR_PATH $DLTK_DIR/editor
RUN mkdir -p $EDITOR_PATH
COPY editor/*.py ${EDITOR_PATH}/
EXPOSE 8888
ENTRYPOINT python3 $EDITOR_PATH/main.py
