#!/bin/bash

clear

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

readonly BASE_DIR=$(dirname $(pwd))
readonly OUTPUT_DIR="$BASE_DIR/output"
readonly DAT_DIR="$OUTPUT_DIR/dat-files"
readonly REP_DIR="$OUTPUT_DIR/reports"
readonly RES_DIR="$BASE_DIR/resources"
readonly CONF_DIR="$RES_DIR/configuration"
readonly SETTING_DIR="$RES_DIR/stock-settings"
readonly RT_LOGS_DIR="$OUTPUT_DIR/rt-app-logs"

# TODO signal Handler SIGINT

cd ..
# Create dirs if not exits
if [ ! -d "$OUTPUT_DIR" ]; then
  echo "...creating $(basename $OUTPUT_DIR) directory"
  mkdir "$OUTPUT_DIR"
fi

if [ ! -d "$DAT_DIR" ]; then
  echo "...creating $(basename $DAT_DIR) directory"
  mkdir "$DAT_DIR"
fi

if [ ! -d "$REP_DIR" ]; then
  echo "...creating $(basename $REP_DIR) directory"
  mkdir "$REP_DIR"
fi

if [ ! -d "$RES_DIR" ]; then
  echo "...creating $(basename $RES_DIR) directory"
  mkdir "$RES_DIR"
fi

if [ ! -d "$CONF_DIR" ]; then
  echo "...creating $(basename $CONF_DIR) directory"
  mkdir "$CONF_DIR"
fi

if [ ! -d "$SETTING_DIR" ]; then
  echo "...creating $(basename $SETTING_DIR) directory"
  mkdir "$SETTING_DIR"
fi

if [ ! -d "$RT_LOGS_DIR" ]; then
  echo "...creating $(basename $RT_LOGS_DIR) directory"
  mkdir "$RT_LOGS_DIR"
fi

# Save current configuration

echo "Frequency range ($MIN_FREQ_MHZ - $BASE_FREQ_MHZ MHz)"

freq=$MIN_FREQ_MHZ

#sleep 5

cd script
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
      exec trace-cmd report $DAT_DIR/traceprov.dat > $REP_DIR/$freq.txt 
    )&

    trace_pid=$!
    
    wait $trace_pid
    echo "trace finito"
    
    kill -SIGINT $read_msr_pid
    wait $read_msr_pid
    

    #sudo trace-cmd record -e sched_switch -f "prev_comm==\"rt-app\" || next_comm==\"rt-app\"" -e read_msr -f "msr==0x19c" rt-app singleCAlter.json && trace-cmd report > toParse.txt 
    
   

    freq=$(($freq + 100))
done