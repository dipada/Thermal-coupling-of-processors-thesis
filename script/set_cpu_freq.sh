#!/bin/bash

# This script set the cpu frequency to a given values
# Passing only one argument to the script 
# will set min and max frequency to the same value
# passing two arguments will set min frequency with lower value
# and max frequency with higher value

ROOT_UID=0     # Only users with $UID 0 have root privileges.
E_NOTROOT=67   # Non-root exit error.


if [ "$UID" -ne "$ROOT_UID" ]
then
  echo "Must be root to run this script."
  exit $E_NOTROOT
fi 

readonly MAX_FREQ_MHZ=$(cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq | awk '{print $1/1000}')
readonly MIN_FREQ_MHZ=$(cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_min_freq | awk '{print $1/1000}')

readonly FREQROOT=/sys/devices/system/cpu
readonly PRINT_USAGE="Usage:\t\t$0 frequency (MHz)\n\t\t$0 2600\n\t\t$0 2600 2800"

# check if arg0 is empty
if [ $# -eq 0 ]; then
  echo -e $PRINT_USAGE
  exit 1
fi

if [ $# -eq 1 ]; then
  freq_min=$1
  freq_max=$1
fi

if [ $# -eq 2 ]; then
  if [ $1 -lt $2 ]; then
    freq_min=$1
    freq_max=$2
  else
    freq_min=$2
    freq_max=$1
  fi
fi

re='^[0-9]+$'

# check if freqs are integers
echo "$freq_min" | grep -E $re > /dev/null

if [ $? -ne 0 ]; then
  echo "Invalid frequency $freq_min. Frequency must be an integer number and in MHz"
  exit 1
fi

echo "$freq_max" | grep -E $re > /dev/null   # POSIX compilant

if [ $? -ne 0 ]; then
  echo "Invalid frequency $freq_max. Frequency must be an integer number and in MHz"
  exit 1
fi

# check if the frequency is supported by the cpu
if [ "$freq_min" -lt "$MIN_FREQ_MHZ" ];then
  echo "Unsupported min frequency: $freq_min. This CPU support this range ($MIN_FREQ_MHZ - $MAX_FREQ_MHZ) MHz"
  exit 1
fi

if [ "$freq_max" -gt "$MAX_FREQ_MHZ" ]; then
  echo "Unsupported frequency: $freq_max. This CPU support this range ($MIN_FREQ_MHZ - $MAX_FREQ_MHZ) MHz"
  exit 1
fi

cpucount=$(cat /proc/cpuinfo|grep processor|wc -l)

# setting frequency using min/max setspeed method not supported on this machine
i=0
while [ $i -ne $cpucount ]
do
  FREQMAX="$FREQROOT/cpu"$i"/cpufreq/scaling_max_freq" 
  FREQMIN="$FREQROOT/cpu"$i"/cpufreq/scaling_min_freq"
  echo $(($freq_max * 1000)) > $FREQMAX
  echo $(($freq_min * 1000)) > $FREQMIN

  i=$(expr $i + 1)
done

if [ $freq_min -eq $freq_max ]; then
  echo "CPU frequencies set to $freq_min MHz"
  echo -e "Currently cores running at:\n$(cat /proc/cpuinfo | grep "cpu MHz" | awk -F':' '{print $2}')"
else
  echo "CPU frequencies set to $freq_min MHz (min frequency) - $freq_max MHz (max frequency)"
fi

echo 