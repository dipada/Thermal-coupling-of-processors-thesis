# Program that parse trace-cmd output, extract information per CPU
# and generate two files per CPU. 
# One file contains read mrs reads and other file contains timestamps of when thing executes

import sys
import os
import re
import csv
import datetime

TJMAX = 100 # TJMAX value for Intel i7-9750H change this if different on your CPU

# Readed values under min threshold or over max threshold will be ignored
TEMP_MIN_THRESHOLD = 10
TEMP_MAX_THRESHOLD = 120


CURRENT_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))
REP_DIR = os.path.join(BASE_DIR, "output/reports/")
CSV_DIR = os.path.join(BASE_DIR, "output/csv/")

cpu_state = {}
user_date_dir = None

def sched_switch_occurs(cpu, timestamp, desc):
    start_exec = r'swapper/\d+:0.*==>.*'
    end_exec = r'.*==> swapper/\d+:0.*'

    if re.match(start_exec, desc): # something on current cpu starts executing
        cpu_state[cpu] = {"start": timestamp}

    elif re.match(end_exec, desc): # something on current cpu ends executing
        if cpu in cpu_state:

            cpu_dir = os.path.join(in_file_dir, cpu)
            if not os.path.exists(cpu_dir):
                os.mkdir(cpu_dir)

            file_path = os.path.join(cpu_dir, f"executions_{cpu}.csv") 
            # appends to file the start timestamp by dictonary and the end timestamp by the current timestamp
            with open(file_path, "a") as f:
                writer = csv.writer(f)
                writer.writerow([cpu_state[cpu]["start"], timestamp])
                del cpu_state[cpu]



def read_msr_occurs(cpu, timestamp, desc, lower_bound=0, upper_bound=120):
    value_regex = r'19c, value\s+([0-9a-fA-F]+)\b'

    match = re.match(value_regex, desc)
    if match:
        # convert value in hex
        hex_value = int(match.group(1), 16)
        celsius_value = TJMAX - (hex_value >> 16 & 0x7F) # extracted according intel system documentation
        
        cpu_dir = os.path.join(in_file_dir, cpu)
        if not os.path.exists(cpu_dir):
            os.mkdir(cpu_dir)
        
        if (celsius_value >= lower_bound and celsius_value <= upper_bound):
            file_path = os.path.join(cpu_dir, f"msr_readings_{cpu}.csv") 
            with open(file_path, "a") as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, celsius_value])

if len(sys.argv) < 2 or len(sys.argv) > 3:
    print("Usage: python preprocessing.py <file_name> <date_dir>")
    print("Example: python preprocessing.py report.txt 25-03-2023-12-00-00")
    exit(1)    

if len(sys.argv) == 3:
    try:
        user_date_dir = datetime.datetime.strptime(sys.argv[2], "%d-%m-%Y-%H-%M-%S")
    except ValueError:
        print("Incorrect date format, should be DD-MM-YYYY-HH-MM-SS")
        exit(1)
else:
    print("Date dir not specified. Will be generated automatically by this program.")

file_name = sys.argv[1]
file_path = os.path.join(REP_DIR, file_name)

# Check if file exists
if not os.path.exists(file_path):
    print("File " + file_name + " does not exist "  + file_path)
    exit(1)

print("Preprocessing - " + file_name + " >> Started...")

# check if CSV directory exists and create it if not
if not os.path.exists(CSV_DIR):
    os.mkdir(CSV_DIR)

# Makes needed directories       
if user_date_dir is not None:
    date_dir = os.path.join(CSV_DIR, user_date_dir.strftime("%d-%m-%Y-%H-%M-%S"))
else:
    date_dir = os.path.join(CSV_DIR, datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S"))

if not os.path.exists(date_dir):
    os.mkdir(date_dir)

in_file_dir = os.path.join(date_dir, file_name.split(".")[0])
if not os.path.exists(in_file_dir):
    os.mkdir(in_file_dir)

# Regexs to match different parts of the line
proc_info = r'\s+(.)'
cpu = r'\s+\[(\d+)\]'
timestamp = r'\s+(\d+\.\d+):'
event = r'\s+(\S+):'
desc = r'\s+(.*)'

#regex = proc_name + proc_id + cpu + timestamp + event + desc
regex =  r'.*' + cpu + timestamp + event + desc
patter = re.compile(regex)

with open(file_path, "r") as f:
    for line in f:
        match = patter.match(line)
        if match:
            cpu_num = match.group(1)
            time_stamp = match.group(2)
            event_type = match.group(3)
            description = match.group(4)
            
            if event_type == "sched_switch":
                sched_switch_occurs(cpu_num, time_stamp, description)
                
            elif event_type == "read_msr":
                read_msr_occurs(cpu_num, time_stamp, description, TEMP_MIN_THRESHOLD, TEMP_MAX_THRESHOLD)

if user_date_dir is None:
    print("Preprocessing - " + file_name + " >> Done!\nFiles are in " + os.path.relpath(date_dir) + " directory.")
else:
    print("Preprocessing - " + file_name + " >> Done!")