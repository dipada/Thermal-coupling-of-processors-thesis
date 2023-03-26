# Program that parse trace-cmd output, extract information per CPU
# and generate two files per CPU. 
# One file contains read mrs reads and other file contains timestamps of when thing executes

import sys
import os
import re
import csv
import datetime

TJMAX = 100 # TJMAX value for Intel i7-9750H

CURRENT_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))
REP_DIR = os.path.join(BASE_DIR, "output/reports/")
CSV_DIR = os.path.join(BASE_DIR, "output/csv/")

cpu_state = {}

def sched_switch_occurs(cpu, timestamp, desc):
    start_exec = r'swapper/\d+:0.*==>.*'
    end_exec = r'.*==> swapper/\d+:0.*'

    if re.match(start_exec, desc): # something on current cpu starts executing
        cpu_state[cpu] = {"start": timestamp}
    
    # print(f"sched_switch event at timestamp {timestamp} on cpu {cpu} with description: {desc}")

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



def read_msr_occurs(cpu, timestamp, desc):
    value_regex = r'19c, value\s+([0-9a-fA-F]+)\b'

    match = re.match(value_regex, desc)
    if match:
        # convert value in hex
        value = int(match.group(1), 16)
        
        cpu_dir = os.path.join(in_file_dir, cpu)
        if not os.path.exists(cpu_dir):
            os.mkdir(cpu_dir)

        file_path = os.path.join(cpu_dir, f"msr_readings_{cpu}.csv") 
        with open(file_path, "a") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, TJMAX - (value >> 16 & 0x7F)])

if len(sys.argv) != 2:
    print("Usage: python3 preprocessing.py <trace_file>")
    exit(1)    

file_name = sys.argv[1]
file_path = os.path.join(REP_DIR, file_name)

# Check if file exists
if not os.path.exists(file_path):
    print("File " + file_name + " does not exist "  + file_path)
    exit(1)

# check if CSV directory exists and create it if not
if not os.path.exists(CSV_DIR):
    os.mkdir(CSV_DIR)

# Makes needed directories       
date_dir = os.path.join(CSV_DIR, datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S"))
if not os.path.exists(date_dir):
    os.mkdir(date_dir)

in_file_dir = os.path.join(date_dir, file_name.split(".")[0])
if not os.path.exists(in_file_dir):
    os.mkdir(in_file_dir)

# Regexs to match different parts of the line
#proc_name = r'\s+(\S+)'  #
#proc_name = r'\s+(.+?)-'

#proc_id = r'(?:-(\d+))?'
#proc_id = r'-(\d+)' #

#proc_name = r'(\w+(?:[-:]\w+)*)'
#proc_id = r'(\d+)'

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
                read_msr_occurs(cpu_num, time_stamp, description)

print("Preprocessing >> Done!\nFiles are in " + os.path.relpath(date_dir) + " directory.")