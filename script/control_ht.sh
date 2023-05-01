#!/bin/bash

# This script disable hyper threading (SMT) if enabled

ROOT_UID=0     # Only users with $UID 0 have root privileges.
E_NOTROOT=67   # Non-root exit error.


if [ "$UID" -ne "$ROOT_UID" ]
then
  echo "Must be root to run this script."
  exit $E_NOTROOT
fi 

ht=$(cat /sys/devices/system/cpu/smt/active)

# Check if hyper threading is enabled
if [[ $ht -eq 1 ]]; then
    echo -e "Hyper Threading active.\nDisabling..."
    echo off | sudo tee /sys/devices/system/cpu/smt/control
    echo "Hyper Threading disabled"
else
    echo "Hyper Threading already disabled."
fi