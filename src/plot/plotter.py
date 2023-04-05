import os
import sys
import csv
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
import numpy as np
import math


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

# plot two subplots one for cpus temperature and one for cpus executions
def plot_two_subplots(fig_name):

    fig, ax = plt.subplots(2, sharex=True)
    y_position = 0
    height = 1

    # plot executions
    for cpu, start_time in start_times.items():
        end_time = end_times[cpu]
        exec_time = np.array(end_time) - np.array(start_time)

        for start_time, duration in zip(start_time, exec_time):
            ax[1].broken_barh([(start_time, duration)], (y_position, height))
            
        y_position += height

    # plot temperatures
    for cpu, cpu_time in temp_times.items():
        cpu_temp = temp[cpu]        
        ax[0].plot(cpu_time, cpu_temp, label=f"Temperature core {cpu}")


    # set graph labels and title
    plt.suptitle('Cores executions and temperatures')

    ax[0].set_ylabel('Temperature (°C)')
    ax[0].set_yscale('linear')

    ax[1].set_xlabel('Timestamp')
    ax[1].set_ylabel('Cores')
    ax[1].set_yscale('linear')

    # Set legends
    box = ax[0].get_position()
    ax[0].set_position([box.x0, box.y0, box.width * 0.66, box.height])

    box = ax[1].get_position()
    ax[1].set_position([box.x0, box.y0, box.width * 0.66, box.height])
    
    # Put legends to the right of the current axis of subplots
    ax[0].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax[1].legend(["Executions"], loc='center left', bbox_to_anchor=(1, 0.5))   

    plt.savefig(os.path.join(PLOT_DIR, files_dir, f"{fig_name}.png"), dpi=2000)
    plt.savefig(os.path.join(PLOT_DIR, files_dir, f"{fig_name}.pdf"))
    #plt.show()
    
    start_times.clear()
    end_times.clear()
    temp_times.clear()
    temp.clear()

def plot_seven_sublots(fig_name):
    #https://matplotlib.org/stable/gallery/subplots_axes_and_figures/subplots_demo.html
    
    colors = list(mcolors.TABLEAU_COLORS)

    ncpu = len(temp)
    ncols = 2
    nrows = math.ceil(ncpu / ncols) + 1

    fig = plt.figure()
    
    gs = gridspec.GridSpec(nrows, ncols)
    

    # plot executions of all cpus
    ex = plt.subplot(gs[nrows-1, :])

    y_position = 0
    height = 1

    for cpu, start_time in start_times.items():

        end_time = end_times[cpu]
        exec_time = np.array(end_time) - np.array(start_time)

        start_duration_list = list(zip(start_time, exec_time))

        ex.broken_barh(start_duration_list, (y_position, height), facecolors=colors[int(int(cpu)%len(colors))])
        y_position += height

    # plot temperatures of all cpus in different subplots
    for row in range(nrows-1):
        for col in range(ncols):
            if row == 0 and col == 0:
                # cpu 0 temperature
                if f"{((row*ncols)+col):03d}" in temp_times:
                    tx0 = plt.subplot(gs[row, col], sharex=ex)
                    tx0.plot(temp_times[f"{(row*ncols)+col:03d}"], temp[f"{(row*ncols)+col:03d}"], color=colors[((row*ncols)+col)%len(colors)])
            else:
                if f"{((row*ncols)+col):03d}" in temp_times:
                    tx = plt.subplot(gs[row, col], sharex=ex, sharey=tx0)
                    tx.plot(temp_times[f"{(row*ncols)+col:03d}"], temp[f"{(row*ncols)+col:03d}"], color=colors[((row*ncols)+col)%len(colors)] ,label=f"Temperature core {(row*ncols)+col:03d}")

            print(f"{fig_name} --> row: {row}, col: {col}, cpu: {(row*ncols)+col:03d}")

    
    

    # set graph labels and title
    plt.suptitle('Cores executions and temperatures')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    plt.savefig(os.path.join(PLOT_DIR, files_dir, f"{fig_name}.png"), dpi=2000)
    plt.savefig(os.path.join(PLOT_DIR, files_dir, f"{fig_name}.pdf"))
    #plt.show()

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

    #plot_two_subplots(subdir_to_plot)
    plot_seven_sublots(subdir_to_plot)
else:
    for subdir in os.listdir(files_path):
        #print(f"FILES DIR {files_dir}")
    
        subdir_path = os.path.join(files_path, subdir)
        load_data(subdir_path)
        #plot_two_subplots(os.path.basename(subdir_path))
        plot_seven_sublots(os.path.basename(subdir_path))
        print(subdir)
        print(subdir_path)
        print(files_path)
    #plot_two_subplots(os.path.basename(subdir_path))
    

