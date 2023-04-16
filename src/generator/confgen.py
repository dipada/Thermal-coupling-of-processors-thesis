# python script to generate configuration json for rt-app

import json
import os
import re

CURRENT_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))
RES_DIR = os.path.join(BASE_DIR, "resources/configuration/")

def fill_global_obj(cpu, duration, calibration, default_policy):
  
    global_obj = {
        "duration" : duration,
        "calibration" : calibration,
        "default_policy" : default_policy,
        "pi_enabled" : False,
        "lock_pages" : False,
        "logdir" : "output/rt-app-logs/",
        "log_basename" : f"cpu{cpu}-{duration}s",
        "gnuplot" : False
    }

    return global_obj

thread_obj = {
    "loop" : -1,
    "cpus": [2],
    "run" : 400000,
    "sleep" : 400000
}

final_json = {
	"tasks" : {
		"thread0" : thread_obj
	},
	"global" : 9
}

for i in range(1, 2):
    final_json["tasks"][f"thread{i}"] = thread_obj


#with open(f'{RES_DIR}/test.json', 'w') as outfile:
    #json.dump(final_json, indent=4, fp=outfile)

def make_json(duration):
    global global_obj
    global final_json

    global_obj["duration"] = duration

    final_json["global"] = global_obj

    for i in range(1, 2):
        final_json["tasks"][f"thread{i}"] = thread_obj


def collect_data(): 
    # Global object default values
    default_duration = 10
    default_calibration = "CPU0"
    default_policy = "SCHED_OTHER"

    # Thread object default values
    default_thread_loop = -1


    user_data = {}

    single_json_generation = False  # If true, a single json file will be generated
                                    # if false same json file will be generated for each cpus

    if (input("Do you want to generate a single json file? (y/n): ") == "y"):
        single_json_generation = True
    
    if single_json_generation:
        cpu = input("Enter the CPU number: ")
    else:
        cpu = input("Enter total number of CPUs:")
    
    if cpu == "" or not cpu.isdigit() or int(cpu) < -1 or (not single_json_generation and int(cpu) < 1):
        print("Invalid CPU number")
        exit(1)

    # Global object values
    duration = input("Enter the duration of the experiment, default is 10s: ")

    if duration == "" or not duration.isdigit():
        print(f"Invalid duration, using default value ({default_duration}))")
        duration = default_duration
    
    calibration = input("Enter the calibration value, default is \"CPU0\":")

    if calibration == "" or calibration == -1 or (not calibration.isdigit() and not re.compile(r"CPU[0-9]+").match(calibration)):
        print(f"Invalid calibration value, using default value ({default_calibration})")
        calibration = default_calibration

    sched_policy = input("Enter the default policy, default is \"SCHED_OTHER\": ")

    if sched_policy != "SCHED_OTHER" and sched_policy != "SCHED_FIFO" and sched_policy != "SCHED_RR" and sched_policy != "SCHED_DEADLINE":
        print(f"Invalid policy, using default value ({default_policy})")
        sched_policy = default_policy

    # thread object values
    loop = input("Enter the loop value for thread, default is -1: ")
    if loop == "" or not loop.isdigit():
        print(f"Invalid loop value, using default value {default_thread_loop}")
        loop = default_thread_loop
    

    user_data["single_json"] = single_json_generation
    user_data["cpu"] = cpu
    user_data["global_duration"] = duration
    user_data["calibration"] = calibration
    user_data["global_default_policy"] = sched_policy

    return user_data


if __name__ == "__main__":

    user_values = collect_data()

    json_name = ""

    if(user_values["single_json"]): # Single json file generation
        json_name = f"cpu{user_values['cpu']}"
        global_obj = fill_global_obj(user_values["cpu"], user_values["global_duration"], user_values["calibration"], user_values["global_default_policy"] )
        json_name = json_name + f"-{global_obj['duration']}s.json"
        print(json_name)
        print("\n\n")
        print(json.dumps(global_obj, indent=4))
    else:
        for i in range(1, int(user_values["cpu"])):
            json_name = f"cpu{i}"
            global_obj = fill_global_obj(i, user_values["global_duration"], user_values["calibration"], user_values["global_default_policy"])
            json_name = json_name + f"-{global_obj['duration']}s.json"
            print(json_name)
            print("\n\n")
            print(json.dumps(global_obj, indent=4))

