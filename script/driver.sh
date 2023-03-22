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
#readonly MIN_FREQ_MHZ=$(lscpu | grep -E '^CPU min MHz' | awk '{print $4}' | awk -F"." '{print $1}')
readonly MIN_FREQ_MHZ=$(cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_min_freq | awk '{print $1/1000}')
readonly BASE_FREQ_MHZ=$(lscpu | grep 'Model name:' | awk '{print $8}' | cut -c1-4 | awk '{printf "%d", $1 * 1000}')

readonly BASE_DIR=$(dirname $(pwd))
readonly OUTPUT_DIR="$BASE_DIR/output"
readonly DAT_DIR="$OUTPUT_DIR/dat-files"
readonly REP_DIR="$OUTPUT_DIR/reports"
readonly RES_DIR="$BASE_DIR/resources"
readonly CONF_DIR="$RES_DIR/configuration"
readonly SETTING_DIR="$RES_DIR/stock-settings"
readonly RT_LOGS_DIR="$OUTPUT_DIR/rt-app-logs"

EXEC_MODE=0  # 0 = swapper, 1 = rt-app


if [ $# -eq 0 ]; then
  echo "Starting swapper mode ..."
  EXEC_MODE=0
elif [ $1 == "-rt" ]; then
  echo "Starting rt-app mode ..."
  if [ $# -ne 2 ] || [ ! -f $CONF_DIR/$2 ]; then
    echo -e "Error: input file not found\nMake sure the file exists in $(basename $CONF_DIR)/"
    exit 1
  else
    echo "... loading configuration file $2 ..."
    EXEC_MODE=1
  fi 
else
  echo -e "Usage: $0\n$0 [-rt <input_file>]"
  exit 1
fi


# TODO signal Handler SIGINT

cd ..

# compile if needed rdmsr
make

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
echo "Saving current CPU configuration..."
#echo $(lscpu | grep -E '^CPU min MHz') > $SETTING_DIR/stock_settings.txt
echo "min freq $(cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_min_freq | awk '{print $1/1000}')" > $SETTING_DIR/stock_settings.txt
#echo $(lscpu | grep -E '^CPU max MHz') >> $SETTING_DIR/stock_settings.txt
echo "max freq $(cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq | awk '{print $1/1000}')" >> $SETTING_DIR/stock_settings.txt
echo turbo $(cat /sys/devices/system/cpu/intel_pstate/no_turbo) >> $SETTING_DIR/stock_settings.txt
echo hyperthreading $(cat /sys/devices/system/cpu/smt/active) >> $SETTING_DIR/stock_settings.txt



echo "Frequency range ($MIN_FREQ_MHZ - $BASE_FREQ_MHZ MHz)"

freq=$MIN_FREQ_MHZ

#sleep 5

cd script
# disabling turbo
./control_turbo.sh

# disabling hyper threading
./control_ht.sh

# execute tracing on rt-app on frequency range
# every loop frequency will be increased by 100 mhz
while [ $freq -le $BASE_FREQ_MHZ ]
do
    echo "Actual $freq MHz - Target $BASE_FREQ_MHZ MHz"

    ./set_cpu_freq.sh $freq

    (
      cd ..
      #echo $(pwd)
      exec ./bin/read_msr INF > /dev/null
    )&
    read_msr_pid=$!

    (
      cd ..
      
      if [ $EXEC_MODE -eq 0 ]; then
        trace-cmd record -P 0 -e sched_switch -o $DAT_DIR/sw_$freq.dat sleep 1
        exec trace-cmd report $DAT_DIR/sw_$freq.dat > $REP_DIR/sw_$freq.txt 
      else
        # rt-app mode
        trace-cmd record -e sched_switch -f "prev_comm==\"rt-app\" || next_comm==\"rt-app\"" -e read_msr -f "msr==0x19c" -o $DAT_DIR/$freq.dat rt-app $CONF_DIR/$2
        exec trace-cmd report $DAT_DIR/$freq.dat > $REP_DIR/$freq.txt 
      fi      
    )&

    trace_pid=$!
    
    wait $trace_pid
    
    kill -SIGINT $read_msr_pid
    wait $read_msr_pid
    
    echo -e "\n\n< Cooling the engines >\n\n"
    sleep 3

    #sudo trace-cmd record -e sched_switch -f "prev_comm==\"rt-app\" || next_comm==\"rt-app\"" -e read_msr -f "msr==0x19c" rt-app singleCAlter.json && trace-cmd report > toParse.txt 
    
   

    freq=$(($freq + 100))
done

echo $(pwd)
# restore stock configuration
echo "Restoring stock CPU configuration..."
#./control_turbo.sh $(cat $SETTING_DIR/stock_settings.txt | grep -E '^turbo' | awk '{print $2}')
#./control_hyperthreading.sh $(cat $SETTING_DIR/stock_settings.txt | grep -E '^hyperthreading' | awk '{print $2}')
echo $(cat $SETTING_DIR/stock_settings.txt | grep turbo | awk '{print $2}') > /sys/devices/system/cpu/intel_pstate/no_turbo
if [ $(cat $SETTING_DIR/stock_settings.txt | grep hyperthreading | awk '{print $2}') == "1" ]; then
  echo on | sudo tee /sys/devices/system/cpu/smt/control
else
  echo off | sudo tee /sys/devices/system/cpu/smt/control
fi

#S_MIN_FREQ=$(cat $SETTING_DIR/stock_settings.txt | grep -E '^CPU min MHz' | awk '{print $4}' | awk -F"." '{print $1}')
S_MIN_FREQ=$(cat $SETTING_DIR/stock_settings.txt | grep 'min freq' | awk '{print $3}')
#S_MAX_FREQ=$(cat $SETTING_DIR/stock_settings.txt | grep -E '^CPU max MHz' | awk '{print $4}' | awk -F"." '{print $1}')
S_MAX_FREQ=$(cat $SETTING_DIR/stock_settings.txt | grep 'max freq' | awk '{print $3}')

./set_cpu_freq.sh $S_MIN_FREQ $S_MAX_FREQ