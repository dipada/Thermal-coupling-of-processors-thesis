#!/bin/bash

ROOT_UID=0     # Only users with $UID 0 have root privileges.
E_NOTROOT=67   # Non-root exit error.


readonly BASE_DIR=$(dirname $(pwd))
readonly RES_DIR="$BASE_DIR/resources"
readonly CONF_DIR="$RES_DIR/configuration"

RUN_FREQ=2500

function sigint_handler() {
    trap - SIGINT
    exit 0
}

if [ "$UID" -ne "$ROOT_UID" ]
then
  echo "Must be root to run this script."
  exit $E_NOTROOT
fi

# Set sigint_handler as SIGINT handler 
trap 'sigint_handler' SIGINT

for file in $CONF_DIR/singleCore2sec/*
do
  ./driver.sh -rt "/$(basename $(dirname $file))/$(basename $file)" -f "$RUN_FREQ"
  sleep 2
done

sleep 8

for file in $CONF_DIR/singleCore1sec/*
do
  ./driver.sh -rt "/$(basename $(dirname $file))/$(basename $file)" -f "$RUN_FREQ"
  sleep 2
done

sleep 8

for file in $CONF_DIR/singleCore500ms/*
do
  ./driver.sh -rt "/$(basename $(dirname $file))/$(basename $file)" -f "$RUN_FREQ"
  sleep 2
done

sleep 8

for file in $CONF_DIR/singleCore200ms/*
do
  ./driver.sh -rt "/$(basename $(dirname $file))/$(basename $file)" -f "$RUN_FREQ"
  sleep 2
done

sleep 8

for file in $CONF_DIR/singleCore100ms/*
do
  ./driver.sh -rt "/$(basename $(dirname $file))/$(basename $file)" -f "$RUN_FREQ"
  sleep 2
done

sleep 8

./driver.sh -rt "5sec.json" -f "$RUN_FREQ"

sleep 8

./driver.sh -rt "10sec.json" -f "$RUN_FREQ"
