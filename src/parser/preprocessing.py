# Program that parse trace-cmd output, extract information per CPU
# and generate two files per CPU. 
# One file contains read mrs reads and other file contains timestamps of when thing executes

import sys
import os
import re
import datetime

CURRENT_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))
REP_DIR = os.path.join(BASE_DIR, "output/reports/")
CSV_DIR = os.path.join(BASE_DIR, "output/csv/")


cpu_state = {}

def sched_switch_occurs(cpu, timestamp, desc):
    start_exec = r'swapper/\d+:0.*==>.*'
    end_exec = r'.*==> swapper/\d+:0.*'

    if re.match(start_exec, desc): # something on current cpu starts executing
        print("start")
        cpu_state[cpu] = {"start": timestamp}
    
    # print(f"sched_switch event at timestamp {timestamp} on cpu {cpu} with description: {desc}")

    elif re.match(end_exec, desc): # something on current cpu ends executing
        if cpu in cpu_state:
            cpu_dir = os.path.join(CSV_DIR, cpu)
            if not os.path.exists(cpu_dir):
                os.mkdir(cpu_dir)

            file_path = os.path.join(cpu_dir, f"executions_{cpu}.csv")
            if not os.path.exists(file_path):
                os.mknod(file_path)
            
            
            with open(file_path, "a") as f:
            
                f.write(cpu_state[cpu]["start"] + "," + timestamp + "\n")
                del cpu_state[cpu]
                
                
        

def read_msr_occurs(cpu, timestamp, desc):
    print(f"read_msr event at timestamp {timestamp} on cpu {cpu} with description: {desc}")

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
                pass
                #read_msr_occurs(cpu_num, time_stamp, description)
