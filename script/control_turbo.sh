#!/bin/bash

ROOT_UID=0     # Only users with $UID 0 have root privileges.
E_NOTROOT=67   # Non-root exit error.


if [ "$UID" -ne "$ROOT_UID" ]
then
  echo "Must be root to run this script."
  exit $E_NOTROOT
fi 

turbo_boost=$(cat /sys/devices/system/cpu/intel_pstate/no_turbo)

# Check if turbo boost is enabled
if [[ $turbo_boost -eq 0 ]]; then
    echo -e "Turbo Boost enabled.\nDisabling..."
    echo 1 > /sys/devices/system/cpu/intel_pstate/no_turbo
    echo "Turbo Boost disabled"
else
    echo "Turbo Boost already disabled."
fi
