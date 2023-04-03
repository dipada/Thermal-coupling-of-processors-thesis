import os
import sys
import csv
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


CURRENT_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))
CSV_DIR = os.path.join(BASE_DIR, "output/csv/")
PLOT_DIR = os.path.join(BASE_DIR, "output/plots/")
SINGLE_PLOT = True

start_times = {}
end_times = {}
temp_times = {}
temp = {}

def load_data(dir_path):
    print("\nPlotting directory: " + dir_path)

    # subdirs in dir_path, used to get number of cpus
    num_subdir = len([f.path for f in os.scandir(dir_path) if f.is_dir()])

    for i in range(num_subdir):

        cpu = f"{i:03d}"
        folder = os.path.join(dir_path, cpu)
        print(folder)
        executions_file = os.path.join(folder, f"executions_{cpu}.csv")
        msr_readings_file = os.path.join(folder, f"msr_readings_{cpu}.csv")
        
        if os.path.isfile(executions_file):
            start_times[cpu] = []
            end_times[cpu] = []
            with open(executions_file) as f:
                reader = csv.reader(f)
                for row in reader:
                    start_times[cpu].append(float(row[0]))
                    end_times[cpu].append(float(row[1]))

        if os.path.isfile(msr_readings_file):
            temp_times[cpu] = []
            temp[cpu] = []
            with open(msr_readings_file) as f:
                reader = csv.reader(f)
                for row in reader:
                    temp_times[cpu].append(float(row[0]))
                    temp[cpu].append(int(row[1]))
    


print("Plotting...")
print("Current directory: " + CURRENT_DIR)
print(os.path.basename(CURRENT_DIR))

if len(sys.argv) < 2 or len(sys.argv) > 4:
    print("Usage: python plotter.py <path_to_dir> for plot multiple figures by all subdirectories")
    print("Usage: python plotter.py -s <path_to_dir> for plot single figure by directory")
    print("Usage: python plotter.py <path_to_dir> <dir_PREFIX> will add prefix to directory name. Works too with -s option")
    print("Example: python plotter.py -s 01-01-2023-00-00-00/800Mhz/")
    print("Example: python plotter.py 01-01-2023-00-00-00/800Mhz/ my_prefix_")
    exit(1)

if sys.argv[1] == "-s": # if -s is passed, plot single figure using subdirectories
    SINGLE_PLOT = True
    files_dir = os.path.basename(os.path.dirname(sys.argv[2]))
    subdir_to_plot = os.path.basename(sys.argv[2])
    #files_path = os.path.join(CSV_DIR, files_dir)
    files_path = os.path.join(os.path.join(CSV_DIR, files_dir), subdir_to_plot)
    if len(sys.argv) == 4:    
        files_dir = "".join([sys.argv[3],files_dir])
else:                   # will plot multiple figures using all subdirectories 
    SINGLE_PLOT = False
    files_dir = sys.argv[1]
    files_path = os.path.join(CSV_DIR, files_dir)
    if len(sys.argv) == 3:
        files_dir = "".join([sys.argv[2],files_dir])

if not os.path.exists(files_path):
    print("Directory " + files_dir + " does not exists")
    exit(1)

# check if directory for plots exists
if not os.path.exists(PLOT_DIR):
    os.mkdir(PLOT_DIR)

if not os.path.exists(os.path.join(PLOT_DIR, files_dir)):
    os.mkdir(os.path.join(PLOT_DIR, files_dir))

# loading and plotting data
if SINGLE_PLOT:
    #path = os.path.join(files_path, subdir_to_plot)
    load_data(files_path)

    plot_two_subplots(subdir_to_plot)
else:
    for subdir in os.listdir(files_path):
        #print(f"FILES DIR {files_dir}")
    
        subdir_path = os.path.join(files_path, subdir)
        load_data(subdir_path)
        plot_two_subplots(os.path.basename(subdir_path))
        print(subdir)
        print(subdir_path)
        print(files_path)
    #plot_two_subplots(os.path.basename(subdir_path))
    

