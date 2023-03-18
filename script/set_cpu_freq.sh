#!/bin/bash

readonly MAX_FREQ_MHZ=$(lscpu | grep -E '^CPU max MHz' | awk '{print $4}' | awk -F"." '{print $1}')
readonly MIN_FREQ_MHZ=$(lscpu | grep -E '^CPU min MHz' | awk '{print $4}' | awk -F"." '{print $1}')

readonly FREQROOT=/sys/devices/system/cpu

# check if arg0 is empty
if [ $# -eq 0 ]; then
  echo "Usage: $0 frequency (MHz)"
  echo "Example: $0 2600"
  exit 1
fi

frequency=$(echo $1);

#re='^[0-9]+(\.[0-9]+)?$'
re='^[0-9]+$'

# check if freq is an integer
echo "$frequency" | grep -E $re > /dev/null   # POSIX compilant

if [ $? -ne 0 ]; then
  echo "$frequency Invalid frequency. Frequency must be an integer number and in MHz"
  exit 1
fi


#https://unix.stackexchange.com/questions/232384/argument-string-to-integer-in-bash

# check if the frequency is supported by the cpu
if [ "$frequency" -lt "$MIN_FREQ_MHZ" ] || [ "$frequency" -gt "$MAX_FREQ_MHZ" ];then
  echo "Unsupported frequency: $frequency. This CPU support this range ($MIN_FREQ_MHZ - $MAX_FREQ_MHZ) MHz"
  exit 1
fi

cpucount=$(cat /proc/cpuinfo|grep processor|wc -l)

# setting frequency using min/max setspeed method not supported on this machine
i=0
while [ $i -ne $cpucount ]
do
  #echo "Setting freq $FREQROOT/cpu"$i"/cpufreq/cpuinfo_max_freq to " $frequency " MHz"
  #echo "Setting cpu-"$i" to" $frequency "MHz"
  FREQMAX="$FREQROOT/cpu"$i"/cpufreq/scaling_max_freq" 
  FREQMIN="$FREQROOT/cpu"$i"/cpufreq/scaling_min_freq"
  echo $(($frequency * 1000)) > $FREQMAX
  echo $(($frequency * 1000)) > $FREQMIN

  i=$(expr $i + 1)
done

echo "CPU frequency set to $frequency MHz"

echo "Currently cores running at: $(cat /proc/cpuinfo | grep "cpu MHz" | awk -F':' '{print $2}')"














