#!/bin/bash

# options on - off - forceoff
# https://serverfault.com/questions/235825/disable-hyperthreading-from-within-linux-no-access-to-bios

ht=$(cat /sys/devices/system/cpu/smt/active)

# Check if hyper threading is enabled
if [[ $ht -eq 1 ]]; then
    echo -e "Hyper Threading active.\nDisabling..."
    echo off | sudo tee /sys/devices/system/cpu/smt/control
    echo "Hyper Threading disabled"
else
    echo "Hyper Threading already disabled."
fi