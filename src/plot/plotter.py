import os
import sys
import csv
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
import matplotlib.ticker as ticker
import numpy as np
import math
import argparse


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

def plot_grid_sublots(fig_name, ignore_empty=True, running_freq=None, conf_name=None, reads_range=None):
    #https://matplotlib.org/stable/gallery/subplots_axes_and_figures/subplots_demo.html
    
    colors = list(mcolors.TABLEAU_COLORS)

    ncpu = len(temp)
    ncols = 2
    nrows = math.ceil(ncpu / ncols) + 1

    fig = plt.figure(figsize=(10, 8))
    #fig.set_size_inches(h=8, w=10)
    
    hratios = [0.6] * (nrows-1) + [1]
    wratios = [1] * ncols 

    gs = gridspec.GridSpec(nrows, ncols, height_ratios=hratios, width_ratios=wratios)
    

    # plot executions of all cpus
    ex = plt.subplot(gs[nrows-1, :])

    y_position = 0
    height = 1

    for cpu, start_time in start_times.items():

        end_time = end_times[cpu]
        exec_time = np.array(end_time) - np.array(start_time)

        start_duration_list = list(zip(start_time, exec_time))

        ex.broken_barh(start_duration_list, (y_position, height), facecolors=colors[int(int(cpu)%len(colors))], label=f"CPU {cpu}")
        
        y_position += height    
    
    #ex.xaxis.set_major_locator(ticker.MultipleLocator(2))
    #ex.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    ex.yaxis.set_major_locator(ticker.MultipleLocator(2))
    ex.yaxis.set_minor_locator(ticker.MultipleLocator(1))
    ex.set_xlabel('Timestamp (s)')
    ex.set_ylabel('Cores')

    if ignore_empty == False:
        # plot temperatures of all cpus in different subplots
        for row in range(nrows-1):
            for col in range(ncols):
                if row == 0 and col == 0:
                    # cpu 0 temperature
                    if f"{((row*ncols)+col):03d}" in temp_times:
                        tx0 = plt.subplot(gs[row, col], sharex=ex)
                        tx0.plot(temp_times[f"{(row*ncols)+col:03d}"], temp[f"{(row*ncols)+col:03d}"], color=colors[((row*ncols)+col)%len(colors)])
                        #tx0.yaxis.set_major_locator(ticker.MultipleLocator(2))
                        tx0.yaxis.set_minor_locator(ticker.MultipleLocator(1))
                        tx0.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
                        tx0.set_ylabel('Temperature (°C)')
                        #tx0.set_xticklabels([])
                else:
                    if f"{((row*ncols)+col):03d}" in temp_times:
                        tx = plt.subplot(gs[row, col], sharex=ex, sharey=tx0)
                        tx.plot(temp_times[f"{(row*ncols)+col:03d}"], temp[f"{(row*ncols)+col:03d}"], color=colors[((row*ncols)+col)%len(colors)])
                        #tx.tick_params(axis='both', which='both', right=False, labelbottom=False)
    else:

        # plot ignoring empty subplots          
        cpu_id = 0
        for row in range(nrows - 1):
            for col in range(ncols):
                # search for the first cpu that has temperature readings
                while f"{cpu_id:03d}" not in temp_times and cpu_id < ncpu:
                    cpu_id += 1

                if cpu_id == len(start_times):
                    break

                if row == 0 and col == 0:
                    # cpu 0 temperature
                    tx0 = plt.subplot(gs[row, col], sharex=ex)
                    tx0.plot(temp_times[f"{cpu_id:03d}"], temp[f"{cpu_id:03d}"], color=colors[cpu_id%len(colors)])
                    #tx0.yaxis.set_major_locator(ticker.MultipleLocator(2))
                    tx0.yaxis.set_minor_locator(ticker.MultipleLocator(1))
                    tx0.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
                    tx0.set_ylabel('Temperature (°C)')
                    
                else:
                    tx = plt.subplot(gs[row, col], sharex=ex, sharey=tx0)
                    tx.plot(temp_times[f"{cpu_id:03d}"], temp[f"{cpu_id:03d}"], color=colors[cpu_id%len(colors)])
                    #tx.tick_params(axis='both', which='both', right=False, labelbottom=False)
                                    
                cpu_id += 1

    # Scaling last plot and insert legend and configuration text
    pos = ex.get_position()
    ex.set_position([pos.x0, pos.y0, pos.width, pos.height * 0.80])
    #ex.legend( loc='upper left', bbox_to_anchor=(0, -0.5), ncol=3,)
    ex.legend( loc='upper right', bbox_to_anchor=(1, -0.5), ncol=3,)

    # configuration text
    if running_freq is not None or conf_name is not None or reads_range is not None:
        param_txt = f"Parameters:\n"
        if conf_name is not None:
            param_txt += f"configuration: {conf_name}\n"
        if running_freq is not None:
            param_txt += f"Runned at: {running_freq} MHz\n"
        if reads_range is not None:
            param_txt += f"MSR readings every: {reads_range} ms\n"

        ex.text(0, -0.5, param_txt, ha='left', va='top', transform=ex.transAxes)
        #ex.text(1, -.5, param_txt, ha='right', va='top', transform=ex.transAxes)    

    # set graph labels and title
    plt.suptitle('Cores executions and temperatures')
    #plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.tight_layout()

    plt.savefig(os.path.join(PLOT_DIR, files_dir, f"{fig_name}_grid.pdf"))
    plt.savefig(os.path.join(PLOT_DIR, files_dir, f"{fig_name}_grid.png"), dpi=2000)
   
    #plt.show()

def plot_stacked_subplots(fig_name, running_freq=None, conf_name=None, reads_range=None):
    
    colors = list(mcolors.TABLEAU_COLORS)

    ncpu = len(temp)

    nrows = ncpu + 1

    hratios = [1] * (nrows-1) + [2]
    wratios = [1]
    
    fig = plt.figure(figsize=(8,8))
    gs = gridspec.GridSpec(nrows=nrows, ncols=1, height_ratios=hratios, width_ratios=wratios)
    
    ex = plt.subplot(gs[nrows-1])
    
    y_position = 0
    height = 1

    for cpu, start_time in start_times.items():

        end_time = end_times[cpu]
        exec_time = np.array(end_time) - np.array(start_time)

        start_duration_list = list(zip(start_time, exec_time))

        ex.broken_barh(start_duration_list, (y_position, height), facecolors=colors[int(int(cpu)%len(colors))], label=f"CPU {cpu}")
        
        y_position += height
    
    ex.set_xlabel('Timestamp (s)')
    ex.set_ylabel('Cores')
    ex.yaxis.set_major_locator(ticker.MultipleLocator(2))
    ex.yaxis.set_minor_locator(ticker.MultipleLocator(1))
    #ex.xaxis.set_major_locator(ticker.MultipleLocator(1))
    #ex.xaxis.set_minor_locator(ticker.MultipleLocator(0.1))


    for row in range(nrows-1):
        if row == 0:
            # cpu 0 temperature
            if f"{row:03d}" in temp_times:
                tx0 = plt.subplot(gs[row], sharex=ex)
                tx0.plot(temp_times[f"{row:03d}"], temp[f"{row:03d}"], color=colors[row%len(colors)])
                tx0.yaxis.set_minor_locator(ticker.MultipleLocator(1))
                tx0.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
                tx0.set_ylabel('Temperature (°C)')
                tx0.tick_params(axis='both', which='both', right=False, labelbottom=False)
        else:
            if f"{row:03d}" in temp_times:
                tx = plt.subplot(gs[row], sharex=ex, sharey=tx0)
                tx.plot(temp_times[f"{row:03d}"], temp[f"{row:03d}"], color=colors[row%len(colors)])
                tx.tick_params(axis='both', which='both', right=False, labelbottom=False)
    
    # Scaling last plot and insert legend and configuration text
    pos = ex.get_position()
    ex.set_position([pos.x0, pos.y0, pos.width, pos.height * 0.80])
    #ex.legend( loc='upper left', bbox_to_anchor=(0, -0.5), ncol=3,)
    ex.legend( loc='upper right', bbox_to_anchor=(1, -0.5), ncol=3,)

    # configuration text
    if running_freq is not None or conf_name is not None or reads_range is not None:
        param_txt = f"Parameters:\n"
        if conf_name is not None:
            param_txt += f"configuration: {conf_name}\n"
        if running_freq is not None:
            param_txt += f"Runned at: {running_freq} MHz\n"
        if reads_range is not None:
            param_txt += f"MSR readings every: {reads_range} ms\n"

        ex.text(0, -0.5, param_txt, ha='left', va='top', transform=ex.transAxes)
        #ex.text(1, -.5, param_txt, ha='right', va='top', transform=ex.transAxes)    

    plt.suptitle('Cores executions and temperatures')
    plt.tight_layout()
    #plt.show()
    plt.savefig(os.path.join(PLOT_DIR, files_dir, f"{fig_name}_stacked.pdf"))
    plt.savefig(os.path.join(PLOT_DIR, files_dir, f"{fig_name}_stacked.png"), dpi=2000)


parser = argparse.ArgumentParser(description="Plot temperature and execution times of a set of cpus.")

# add arguments
parser.add_argument("path_to_dir", help="path to parent directory of cpus directories")
parser.add_argument("-s", "--single-plot", action="store_true", help="Just plot all subdirectories of a single directory")
parser.add_argument("prefix", nargs="?", default="", help="Will add a prefix to the output directory name")
parser.add_argument("-f", "--freq", nargs="?", default=None, help="Frequency at which the experiment was run")
parser.add_argument("-c", "--conf", nargs="?", default=None, help="Configuration file name")
parser.add_argument("-r", "--range-reads", nargs="?", default=None, help="MSR readings range")

# parse arguments
args = parser.parse_args()

running_freq = args.freq
conf_name = args.conf
reads_range = args.range_reads

SINGLE_PLOT = args.single_plot
files_dir = args.path_to_dir
files_path = os.path.join(CSV_DIR, files_dir)

if SINGLE_PLOT:
    subdir_to_plot = os.path.basename(files_dir)
    files_dir = os.path.basename(os.path.dirname(files_dir))
    files_path = os.path.join(os.path.join(CSV_DIR, files_dir), subdir_to_plot)

files_dir = "".join([args.prefix, files_dir])

if not os.path.exists(files_path):
    print(f"Directory {files_dir} does not exist")
    exit(1)

# check if directory for plots exists
if not os.path.exists(PLOT_DIR):
    os.mkdir(PLOT_DIR)

if not os.path.exists(os.path.join(PLOT_DIR, files_dir)):
    os.mkdir(os.path.join(PLOT_DIR, files_dir))

# loading and plotting data
if SINGLE_PLOT:
    load_data(files_path)

    #plot_two_subplots(subdir_to_plot)
    plot_grid_sublots(subdir_to_plot, False, running_freq, conf_name, reads_range)
    plot_stacked_subplots(subdir_to_plot, running_freq, conf_name, reads_range)
else:
    for subdir in os.listdir(files_path):
            
        subdir_path = os.path.join(files_path, subdir)
        load_data(subdir_path)
        #plot_two_subplots(os.path.basename(subdir_path))
        plot_grid_sublots(os.path.basename(subdir_path), False, running_freq, conf_name, reads_range)
        plot_stacked_subplots(os.path.basename(subdir_path), running_freq, conf_name, reads_range)
    
    

