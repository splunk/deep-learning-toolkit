#!/bin/bash

# This script packages the Splunk app, preforms inspection checks and saves the output file (.tar.gz) to a path (first script argument). When ommitting the path, a temporary path will be used.
# Requirements: slim and splunk-appinspect
# Example usage: build_app.bash /tmp/dltk.tar.gz

set -e
#set -x

BUILD_DIR="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
PACKAGE_OUTPUT_PATH=$1

# create temp folder
TMP_DIR=/tmp/build_app
rm -rf $TMP_DIR
mkdir -p $TMP_DIR

# make 'clean' copy of app
CLEAN_APP=$TMP_DIR/dltk
cp -r $BUILD_DIR/../app $CLEAN_APP
find $CLEAN_APP -name 'test_*.py' -delete
find $CLEAN_APP -name 'pytest_*.py' -delete
find $CLEAN_APP -name '*_test.py' -delete
find $CLEAN_APP -name '.gitignore' -delete
find $CLEAN_APP -name 'local.meta' -delete
find $CLEAN_APP -name 'test' -exec rm -r {} +
find $CLEAN_APP -name 'tests' -exec rm -r {} +
find $CLEAN_APP -name 'local' -exec rm -r {} +
find $CLEAN_APP -name '__MACOSX.' -exec rm -r {} +

# package app
OUTPUT_DIR=$TMP_DIR/output
mkdir -p $OUTPUT_DIR
slim package -o $OUTPUT_DIR $CLEAN_APP
DLTK_PACKAGE=$(find $OUTPUT_DIR -maxdepth 1 -type f -name '*.tar.gz')
DLTK_PACKAGE_NAME=$(basename $DLTK_PACKAGE)
#tar -tvf $DLTK_PACKAGE | grep local

# inspect app
splunk-appinspect inspect --mode test $DLTK_PACKAGE
# https://dev.splunk.com/enterprise/docs/developapps/testvalidate/appinspect/appinspectreferencetopics/splunkappinspectcheck/
# https://dev.splunk.com/enterprise/docs/developapps/testvalidate/appinspect/appinspectreferencetopics/appinspecttagreference

# copy package to target path
if [ -n "$PACKAGE_OUTPUT_PATH" ]; then
    cp $DLTK_PACKAGE $PACKAGE_OUTPUT_PATH
    echo "Output: $PACKAGE_OUTPUT_PATH"
else
    echo "Output: $DLTK_PACKAGE"
fi
