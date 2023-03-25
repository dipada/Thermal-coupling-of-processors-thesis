# Program that parse trace-cmd output, extract information per CPU
# and generate two files per CPU. 
# One file contains read mrs reads and other file contains timestamps of when thing executes


import sys
import os

CURRENT_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))
REP_DIR = os.path.join(BASE_DIR, "output/reports/")

if len(sys.argv) != 2:
    print("Usage: python3 preprocessing.py <trace_file>")
    exit(1)    

file_name = sys.argv[1]
file_path = os.path.join(REP_DIR, file_name)

# Check if file exists
if not os.path.exists(file_path):
    print("File " + file_name + " does not exist "  + file_path)
    exit(1)
