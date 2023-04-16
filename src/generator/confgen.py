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

def fill_thread_obj(loop, cpu_affinity, run, sleep):
    thread_obj = {
        "loop" : loop,
        "cpus": f"[{cpu_affinity}]",
        "run" : run,
        "sleep" : sleep
    }

    return thread_obj

#final_json = {
#	"tasks" : {
#		"thread0" : thread_obj
#	},
#	"global" : 9
#}

#for i in range(1, 2):
#    final_json["tasks"][f"thread{i}"] = thread_obj


#with open(f'{RES_DIR}/test.json', 'w') as outfile:
    #json.dump(final_json, indent=4, fp=outfile)

def make_json(duration):
    global global_obj
    global final_json

    global_obj["duration"] = duration

    final_json["global"] = global_obj

    for i in range(1, 2):
        final_json["tasks"][f"thread{i}"] = thread_obj

def global_obj_data(user_data):
    
    # Global object default values
    default_duration = 10
    default_calibration = "CPU0"
    default_policy = "SCHED_OTHER"

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

    user_data["global_duration"] = duration
    user_data["calibration"] = calibration
    user_data["global_default_policy"] = sched_policy

def thread_obj_data(user_data, nthread):
    # Thread object default values
    default_thread_loop = -1
    default_cpu_affinity = 0
    default_thread_run = 500000
    default_thread_sleep = 500000

    loop = input(f"Enter the loop value for thread, default is {default_thread_loop}: ")
    if loop == "" or not loop.isdigit():
        print(f"Invalid loop value, using default value {default_thread_loop}")
        loop = default_thread_loop

    cpu_affinity = input(f"Enter the CPU affinity for thread, default is {default_cpu_affinity}: ")
    if cpu_affinity == "" or not cpu_affinity.isdigit():
        print(f"Invalid CPU affinity value, using default value {default_cpu_affinity}")
        cpu_affinity = default_cpu_affinity

    run = input(f"Enter the run value for thread, default is {default_thread_run} usec: ")
    if run == "" or not run.isdigit():
        print(f"Invalid run value, using default value {default_thread_run}")
        run = default_thread_run
    
    sleep = input(f"Enter the sleep value for thread, default is {default_thread_sleep} usec: ")
    if sleep == "" or not sleep.isdigit():
        print(f"Invalid sleep value, using default value {default_thread_sleep}")
        sleep = default_thread_sleep

    user_data[f"thread_loop{nthread}"] = loop
    user_data[f"thread_cpu_affinity{nthread}"] = cpu_affinity
    user_data[f"thread_run{nthread}"] = run
    user_data[f"thread_sleep{nthread}"] = sleep



def collect_data(): 

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

    user_data["single_json"] = single_json_generation
    user_data["cpu"] = cpu

    # Global object values
    global_obj_data(user_data)

    # thread object values
    nthread = 0
    while True:
        thread_obj_data(user_data, nthread)
        nthread += 1
        if input("Do you want to add another thread? (y/n): ") == "n":
            break
    
    user_data["num_threads"] = nthread  

    return user_data


if __name__ == "__main__":

    user_values = collect_data()

    json_name = ""

    if(user_values["single_json"]): # Single json file generation
        json_name = f"cpu{user_values['cpu']}"
        global_obj = fill_global_obj(user_values["cpu"], user_values["global_duration"], user_values["calibration"], user_values["global_default_policy"] )
        
        for i in range(0, int(user_values["num_threads"])):
            thread_obj = fill_thread_obj(user_values[f"thread_loop{i}"], user_values[f"thread_cpu_affinity{i}"], user_values[f"thread_run{i}"], user_values[f"thread_sleep{i}"])
            print(json.dumps(thread_obj, indent=4))
            print("\n\n")
        json_name = json_name + f"-{user_values['global_duration']}s.json"
        print(json_name)
        print("\n\n")
        print(json.dumps(global_obj, indent=4))
        print("\n\n")
        
    else:
        for i in range(0, int(user_values["cpu"])):
            json_name = f"cpu{i}"
            global_obj = fill_global_obj(i, user_values["global_duration"], user_values["calibration"], user_values["global_default_policy"])
            json_name = json_name + f"-{user_values['duration']}s.json"
            print(json_name)
            print("\n\n")
            print(json.dumps(global_obj, indent=4))

