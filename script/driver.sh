#!/bin/bash

clear

ROOT_UID=0     # Only users with $UID 0 have root privileges.
E_NOTROOT=67   # Non-root exit error.


if [ "$UID" -ne "$ROOT_UID" ]
then
  echo "Must be root to run this script."
  exit $E_NOTROOT
fi 

readonly MIN_FREQ_MHZ=$(cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_min_freq | awk '{print $1/1000}')
readonly BASE_FREQ_MHZ=$(lscpu | grep 'Model name:' | awk '{print $8}' | cut -c1-4 | awk '{printf "%d", $1 * 1000}')

readonly BASE_DIR=$(dirname $(pwd))
readonly OUTPUT_DIR="$BASE_DIR/output"
readonly SRC_DIR="$BASE_DIR/src"
readonly DAT_DIR="$OUTPUT_DIR/dat-files"
readonly REP_DIR="$OUTPUT_DIR/reports"
readonly CSV_DIR="$OUTPUT_DIR/csv"
readonly RES_DIR="$BASE_DIR/resources"
readonly CONF_DIR="$RES_DIR/configuration"
readonly SETTING_DIR="$RES_DIR/stock-settings"
readonly RT_LOGS_DIR="$OUTPUT_DIR/rt-app-logs"

readonly MSR_READING_INTERVAL_MS=10 # in ms
readonly MSR_READING_NS=$(( $MSR_READING_INTERVAL_MS*1000000 )) # in ns

function sigint_handler() {
    echo -e "\nRestoring stock configuration..."
    restore_stock_configuration
    echo "Exiting..."
    trap - SIGINT
    exit 0
}

function restore_stock_configuration(){
  echo $(cat $SETTING_DIR/stock_settings.txt | grep sched_rt_runtime_us | awk '{print $2}') | sudo tee /proc/sys/kernel/sched_rt_runtime_us > /dev/null
  echo $(cat $SETTING_DIR/stock_settings.txt | grep turbo | awk '{print $2}') | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo > /dev/null
  if [ $(cat $SETTING_DIR/stock_settings.txt | grep hyperthreading | awk '{print $2}') -eq 1 ]; then
    echo on | sudo tee /sys/devices/system/cpu/smt/control > /dev/null
  else
    echo off | sudo tee /sys/devices/system/cpu/smt/control > /dev/null
  fi

  S_MIN_FREQ=$(cat $SETTING_DIR/stock_settings.txt | grep 'min freq' | awk '{print $3}')
  S_MAX_FREQ=$(cat $SETTING_DIR/stock_settings.txt | grep 'max freq' | awk '{print $3}')
}



# -rt option start rt-app mode and need a configuration file

if [ $# -eq 2 ] && [ $1 == "-rt" ]; then
  if [ ! -f $CONF_DIR/$2 ]; then
    echo -e "Error: input file not found\nMake sure the file exists in $(basename $CONF_DIR)/"
    exit 1
  else
    echo "... loading configuration file $2 ..."
  fi 
else
  echo -e "Usage: $0\n$0 [-rt <input_file>]"
  exit 1
fi

cd ..

# compile if needed rdmsr
make

# cleaning old dat-files and reports
rm -f $DAT_DIR/*
rm -f $REP_DIR/*

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

# Save current cpu configuration
echo "Saving current CPU configuration..."
echo "min freq $(cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_min_freq | awk '{print $1/1000}')" > $SETTING_DIR/stock_settings.txt
echo "max freq $(cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq | awk '{print $1/1000}')" >> $SETTING_DIR/stock_settings.txt
echo turbo $(cat /sys/devices/system/cpu/intel_pstate/no_turbo) >> $SETTING_DIR/stock_settings.txt
echo hyperthreading $(cat /sys/devices/system/cpu/smt/active) >> $SETTING_DIR/stock_settings.txt
echo sched_rt_runtime_us $(cat /proc/sys/kernel/sched_rt_runtime_us) >> $SETTING_DIR/stock_settings.txt

# unbounded execution time of real-time tasks
echo "Setting unbounded execution time for real-time tasks"
$(echo -1 > /proc/sys/kernel/sched_rt_runtime_us)


echo "Frequency range ($MIN_FREQ_MHZ - $BASE_FREQ_MHZ MHz)"

# Set sigint_handler as SIGINT handler 
trap 'sigint_handler' SIGINT

#freq=$MIN_FREQ_MHZ
freq=2500

cd script
# disabling turbo
./control_turbo.sh

# disabling hyper threading
./control_ht.sh


# execute tracing on rt-app on frequency range
# every loop frequency will be increased by 100 mhz
#BASE_FREQ_MHZ
while [ $freq -le 2500 ]
do
    echo "Actual $freq MHz - Target $BASE_FREQ_MHZ MHz"

    ./set_cpu_freq.sh $freq

    # start read msr program on all cpus
    n_cpus_act=$(nproc)
    rd_msr_pids=()
    
    cd ..
    for ((i=0; i<$n_cpus_act; i++))
    do
      
      echo -e "\nStarting read_msr on [CPU $i]"
      exec ./bin/read_msr "-U" "-r$MSR_READING_NS" "-c$i"&
      rd_msr_pids+=($!)

      echo -e "\nSetting scheduling policy"
      chrt -f -p 50 $!
      chrt -p $!
      
      echo -e "\nSetting cpu affinity"
      mask=$((1 << i))
      taskset -p "$mask" "$!"
      printf "pid $! affinity [cpu $i] - mask [0x%x]\n" $mask

    done

    cd script

    # Starting trace on rt-app and read_msr events
    (
      cd ..
      echo "Collecting pids to trace ..."
      
      # pid list for trace-cmd trace
      pids_list=""
      for pid in "${rd_msr_pids[@]}"; do
        pids_list="$pids_list -P $pid"
      done
      echo "$pids_list"

      chrt -f 80 trace-cmd record -P0 $pids_list -e sched_switch -e read_msr -f "msr==0x19c" -o $DAT_DIR/sw_$freq.dat rt-app $CONF_DIR/$2
      exec trace-cmd report $DAT_DIR/sw_$freq.dat > $REP_DIR/sw_$freq.txt   
    )&

    trace_pid=$!
    
    wait $trace_pid
    
    echo "Stopping read_msr programs..."
    for pid in ${rd_msr_pids[@]}
    do
      printf "Killing $pid..."
      kill -SIGINT $pid
      wait $pid
      printf " Done\n"
    done
    
    echo -e "\n\n< Cooling the engines >\n\n"
    sleep 3  
   
    freq=$(($freq + 100))
done

# restore stock configuration
restore_stock_configuration

./set_cpu_freq.sh $S_MIN_FREQ $S_MAX_FREQ

# parse generated reports
cd $REP_DIR
date=$(date +%d-%m-%Y-%H-%M-%S)


mkdir $CSV_DIR/$date

for file in *.txt
do
  python3 $SRC_DIR/parser/preprocessing.py "$file" "$date"&
done

wait

echo -e "Done!\nFiles are in $(dirname $OUTPUT_DIR)/csv/$date directory"


# plot generated csv files
file_name=$(basename $2)
file_name=${file_name%.*}


cd $CSV_DIR/$date

mkdir $OUTPUT_DIR/plots/$file_name-$date

for dir in * 
do
  running_freq=$(echo $dir | awk -F'_' '{print $2}')
  python3 $SRC_DIR/plot/plotter.py "-s" "$date/$dir" "$file_name-" "-f $running_freq" "-c $file_name" "-r $MSR_READING_INTERVAL_MS"  > /dev/null &
done

wait

$(chmod -R u+w "$OUTPUT_DIR/plots/$file_name-$date")

echo -e "Done!\nFiles are in $(dirname $OUTPUT_DIR)/plots/$file_name-$date directory"
