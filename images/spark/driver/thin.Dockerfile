FROM gcr.io/spark-operator/spark-py:v2.4.5

# root folder for everything that is dltk specific
ENV DLTK_DIR /dltk
RUN mkdir -p $DLTK_DIR

RUN apt-get update && apt-get install -y git

# install python packages
COPY pyspark-requirements.txt ${DLTK_DIR}/requirements.txt
RUN pip3 install --no-cache-dir -r ${DLTK_DIR}/requirements.txt
COPY driver/requirements.txt ${DLTK_DIR}/driver-requirements.txt
RUN pip3 install --no-cache-dir -r ${DLTK_DIR}/driver-requirements.txt

# install s3 libraries
ENV SPARK_JARS_DIR /opt/spark/jars/
# from https://mvnrepository.com/artifact/org.apache.hadoop/hadoop-aws/2.7.3
COPY driver/hadoop-aws-2.7.3.jar ${SPARK_JARS_DIR}
# from https://mvnrepository.com/artifact/com.amazonaws/aws-java-sdk/1.7.4
COPY driver/aws-java-sdk-1.7.4.jar ${SPARK_JARS_DIR}

# dltk driver server
ENV DRIVER_DIR $DLTK_DIR/driver
RUN mkdir -p $DRIVER_DIR
COPY driver/*.py ${DRIVER_DIR}/
EXPOSE 8888
