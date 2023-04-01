import os
import sys


CURRENT_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))
CSV_DIR = os.path.join(BASE_DIR, "output/csv/")
PLOT_DIR = os.path.join(BASE_DIR, "output/plots/")

print("Plotting...")
print("Current directory: " + CURRENT_DIR)
print(os.path.basename(CURRENT_DIR))

if len(sys.argv) < 2 or len(sys.argv) > 3:
    print("Usage: python plotter.py <path_to_dir> for plot files in passed directory")
    print("Example: python plotter.py 01-01-2023-00-00-00/800Mhz/")
    exit(1)

files_dir = sys.argv[1]
files_path = os.path.join(CSV_DIR, files_dir)

if not os.path.exists(files_path):
    print("Directory " + files_dir + " does not exists")
    exit(1)

# check if directorys for plots exists
if not os.path.exists(PLOT_DIR):
    os.mkdir(PLOT_DIR)

if not os.path.exists(os.path.join(PLOT_DIR, files_dir)):
    os.mkdir(os.path.join(PLOT_DIR, files_dir))







