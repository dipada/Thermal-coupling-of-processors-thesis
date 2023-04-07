#!/bin/bash

ROOT_UID=0     # Only users with $UID 0 have root privileges.
E_NOTROOT=67   # Non-root exit error.


if [ "$UID" -ne "$ROOT_UID" ]
then
  echo "Must be root to run this script."
  exit $E_NOTROOT
fi

./driver.sh "-rt" "singleCDeadLine.json"
echo "Cooling..."
sleep 30
./driver.sh "-rt" "fastAlternDL.json"
echo "Cooling..."
sleep 30
./driver.sh "-rt" "alterHalfDL.json"

