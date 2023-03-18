#!/bin/bash

readonly MAX_FREQ_MHZ=$(lscpu | grep -E '^CPU max MHz' | awk '{print $4}' | awk -F"." '{print $1}')
readonly MIN_FREQ_MHZ=$(lscpu | grep -E '^CPU min MHz' | awk '{print $4}' | awk -F"." '{print $1}')

echo "Starting from $MIN_FREQ_MHZ MHz to $MAX_FREQ_MHZ MHz"

#freq=$MIN_FREQ_MHZ
freq=2500

sleep 5


#$MAX_FREQ_MHZ
while [ $freq -le 2600 ]
do
    echo "freq $freq - MAX $MAX_FREQ_MHZ"

    sudo sh ./set_cpu_freq.sh $freq

    sudo ./rdMsr INF &> /dev/null
    PID=$!

    sudo trace-cmd record -e sched_switch -f "prev_comm==\"rt-app\" || next_comm==\"rt-app\"" -e read_msr -f "msr==0x19c" rt-app singleCAlter.json && trace-cmd report > toParse.txt 
    
   
    sleep 1

    freq=$(($freq + 100))
done