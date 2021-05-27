import os
import time
import uuid
import subprocess

# Global variables. ADJUST THEM TO YOUR NEEDS
chia_executable = os.path.expanduser('~')+"/chia-blockchain/venv/bin/chia" # directory of chia binary file
numberOfLogicalCores = 16 # number of logical cores that you want to use overall
run_loop_interval = 10 # seconds of delay before this algorithm executes another loop
refresh_logs_interval = 10 # seconds of delay before this algorithm will try to re-read all logs after adding plot
logs_location = os.path.expanduser('~')+"/.chia/mainnet/plotter/" # location of the log files. Remove all corrupted and interrupted log files!
string_contained_in_all_logs = ".txt"  # shared part of the name of all the log files (all logfiles must have it!)
phase_one_finished = "Time for phase 1 =" # part of the log file that means 1/2 core should be freed
phase_four_finished = "Time for phase 4 =" # part of the log file that means 2/2 core should be freed
temporary_directory = "/srv/chia/plots/" # plotting final destination
final_directory = "/mnt/chia/plots/" # plotting directory
farmer_public_key = "8536d991e929298b79570ad16ee1150d3905121a44251eda3740f550fcb4285578a2a22448a406c5e73c2e9d77cd7eb2" # change to your key
pool_public_key = "907f125022f2b5bf75ea5ef1f108b0c9110931891a043f421837ba6edcaa976920c5b2c5ba8ffdfb00c0bd71e7b5a2b1" # change to your key


# Functions
def fetch_file_content(file_path):
    if not os.path.isfile(file_path):
        print('File does not exist.')
    else:
        with open(file_path) as file:
            return file.readlines()


def fetch_logs():
    item_in_location_list = os.listdir(logs_location)
    content_path_list = list(map(lambda log: logs_location + log, item_in_location_list))
    text_file_list = list(filter(lambda path: string_contained_in_all_logs in path, content_path_list))
    logs_content = list(map(fetch_file_content, text_file_list))
    return logs_content


def count_used_cores(logs):
    print("===START COUNTING===")
    used_cores_counter = 0
    for (index, log) in enumerate(logs):
        print(f"Starting log #{index}")
        print("Potentially it's still in phase one assigning 2 cores")
        used_cores_counter += 2
        for line in log:
            if phase_one_finished in line:
                print("Phase one was finished in the log, deallocating one core")
                used_cores_counter -= 1
            if phase_four_finished in line:
                print("Phase four was finished in the log, deallocating one core")
                used_cores_counter -= 1
    print(f"===FINISH COUNTING: {used_cores_counter} USED CORES===")
    return used_cores_counter


def use_all_cores():
    log_list = fetch_logs()
    cores_used = count_used_cores(log_list)
    while numberOfLogicalCores > cores_used +1:
        print("There are two cores free, adding new plot!")
        add_plot()
        time.sleep(refresh_logs_interval)
        log_list = fetch_logs()
        cores_used = count_used_cores(log_list)


def add_plot():
    command = f"{chia_executable} plots create -k 32 -b 3724 -n 1 -r4 -t /srv/chia/plots/ -2 /srv/chia/plots/ -d /mnt/chia/plots &"
    unique_filename = str(uuid.uuid4())
    new_log_file_path = f"{logs_location}/{unique_filename}{string_contained_in_all_logs}"
    with open(new_log_file_path, "w") as file:
        subprocess.run(command, shell=True, stdout=file)


def run_loop():
    while True:
        use_all_cores()
        time.sleep(run_loop_interval)


# Entry point
run_loop()
