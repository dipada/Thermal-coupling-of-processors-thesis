#!/bin/bash

turbo_boost=$(cat /sys/devices/system/cpu/intel_pstate/no_turbo)

# Check if turbo boost is enabled
if [[ $turbo_boost -eq 0 ]]; then
    echo -e "Turbo Boost enabled.\nDisabling..."
    echo 1 > /sys/devices/system/cpu/intel_pstate/no_turbo
    echo "Turbo Boost disabled"
else
    echo "Turbo Boost already disabled."
fi
