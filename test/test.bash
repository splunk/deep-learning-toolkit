#!/bin/bash

#set +x

env_file="./test.env"
if [ -f "$env_file" ]
then
	echo "Loading variables from $env_file"
  set -a
  source $env_file
  set +a
else
	echo "WARNING: Variable file $env_file not found."
fi

if ! [ -v DLTK_ENVIRONMENT ]; then
  echo "Varaible DLTK_ENVIRONMENT not set"
  exit 1
fi
if ! [ -v SPLUNK_PASSWORD ]; then
  echo "Varaible SPLUNK_PASSWORD not set"
  exit 1
fi
if ! [ -v SPLUNK_HOME ]; then
  SPLUNK_HOME="/opt/splunk/"
  echo "Varaible SPLUNK_HOME not set. Defaulting to $SPLUNK_HOME."
fi
SPLUNK="$SPLUNK_HOME/bin/splunk"
if [ -z "$SPLUNK" ]; then
  echo "Could not find splunk executable: $SPLUNK"
  exit 1
fi

export DLTK_ENVIRONMENT=$DLTK_ENVIRONMENT
export SPLUNK_PASSWORD=$SPLUNK_PASSWORD
$SPLUNK cmd python3 test.py