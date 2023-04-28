# Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [How to run](#how-to-run)
4. [Customization](#customization)
5. [Test generation](#test-generation)

## Introduction
This project is part of my bachelor thesis in computer science, developed with the supervision of Prof. Enrico Bini at the University of Torino.
This project aim to investigate the thermal coupling of multicore CPUs. In multicore architectures, CPUs belong to the same silicon die. This implies that if one CPU overheats (due to the running workload), the neighboring CPUs also heats up (due to thermal conductance) preventing them to run at full speed.

This phenomenon is investigated using rt-app for generate sintetic workload, trace-cmd a frontend application to ftrace for event tracing and a program that reads temperature sensors.
At end data will be processed and plotted.

## Prerequisites
This project runs on GNU/Linux.
For run this project you need to have:
- gcc compiler, automake, python, bash
- [rt-app](https://github.com/scheduler-tools/rt-app)
- [trace-cmd](https://www.trace-cmd.org/)
- [matplotlib](https://matplotlib.org/)

## How to run

### 1. Clone this repository
### 2. go to scripts directory
### 3. launch with root privileges
```bash ./driver.sh -rt singleCore1sec/singleCore1sec-cpu0.json -f 2500```
If run this script without -f option, passed configuration file will be runned by the minimum frequency of the cpu at base frequency.
### 3.1 if you want to run multiple tests, launch with root privileges
```bash ./multiple_conf.sh```
### 4. wait for the end of the test
### 5. prompt will display the path of the output file. All plots will be saved in output/plots/ directory

## Customization
You can customize different parameters for fit different needs:
- temperature readings interval: this can be changed in driver.sh script (default 10 ms)
- execution frequency: this can be set when launch ./driver.sh with option -f
- lower and upper bound for the readed temperature: this can be changed in preprocessing.py
- If want run ./multiple_conf.sh with different frequency, you can change the frequency in the script. Frequency will be applied to all tests.

## Test generation
There are 2 mode for generate tests:
- Self-writing a configuration.json according to rt-app syntax and put it in resources/configuration directory
- Using confgen.py script. With this script u will be able to generate a configuration.json file with a specific number of tasks, a specific number of cores and a specific period for each task. This script will generate multiple configuration.json with same parameteres by varying the cpu that will execute the workloads. All json will be under resources/configuration directory.

