#!/bin/bash

ROOT_UID=0     # Only users with $UID 0 have root privileges.
E_NOTROOT=67   # Non-root exit error.


if [ "$UID" -ne "$ROOT_UID" ]
then
  echo "Must be root to run this script."
  exit $E_NOTROOT
fi 

#readonly MAX_FREQ_MHZ=$(lscpu | grep -E '^CPU max MHz' | awk '{print $4}' | awk -F"." '{print $1}')
readonly MIN_FREQ_MHZ=$(lscpu | grep -E '^CPU min MHz' | awk '{print $4}' | awk -F"." '{print $1}')
readonly BASE_FREQ_MHZ=$(lscpu | grep 'Model name:' | awk '{print $8}' | cut -c1-4 | awk '{printf "%d", $1 * 1000}')

readonly DAT_DIR="output/dat-files"
readonly CONF_DIR="resources/configuration"

echo "Starting from $MIN_FREQ_MHZ MHz to $BASE_FREQ_MHZ MHz"

freq=$MIN_FREQ_MHZ

sleep 5


# TODO signal Handler SIGINT

# disabling turbo
./control_turbo.sh

while [ $freq -le $BASE_FREQ_MHZ ]
do
    echo "Actual $freq MHz - Target $BASE_FREQ_MHZ MHz"

    sudo ./set_cpu_freq.sh $freq

    (
      cd ..
      make
     #echo $(pwd)
      exec ./bin/read_msr INF > /dev/null
    )&
    read_msr_pid=$!

    (
      cd ..
      echo $(pwd)
      trace-cmd record -e sched_switch -f "prev_comm==\"rt-app\" || next_comm==\"rt-app\"" -e read_msr -f "msr==0x19c" -o $DAT_DIR/traceprov.dat rt-app $CONF_DIR/singleCAlter.json
      exec trace-cmd report $DAT_DIR/traceprov.dat > output/reports/$freq.txt 
    )&

    trace_pid=$!
    
    wait $trace_pid
    echo "trace finito"
    
    kill -SIGINT $read_msr_pid
    wait $read_msr_pid
    

    #sudo trace-cmd record -e sched_switch -f "prev_comm==\"rt-app\" || next_comm==\"rt-app\"" -e read_msr -f "msr==0x19c" rt-app singleCAlter.json && trace-cmd report > toParse.txt 
    
   

    freq=$(($freq + 100))
done