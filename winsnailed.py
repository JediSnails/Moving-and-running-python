 #python winsnailed.py -u administrator -t targets.txt -f C:\anydir\script.sh config.cfg -d C:\users -c "get-process" "get-service"
 
import argparse
import subprocess
import time
from getpass import getpass, getuser

# Define command-line arguments
parser = argparse.ArgumentParser(description="Run remote commands and copy files to target hosts over SSH")
parser.add_argument("-u", "--user", help="Username for target systems")
parser.add_argument("-t", "--target-list", required=True, help="Path to file containing list of target hosts")
parser.add_argument("-c", "--commands", nargs='+', help="Commands to run on remote systems")
parser.add_argument("-f", "--files", nargs='+', help="Files to transfer to remote systems")
parser.add_argument("-d", "--destination", default="/tmp/", help="Remote destination directory for transferred files")
args = parser.parse_args()

# Collect inputs
remote_user = args.user or getuser()
target_list = args.target_list
commands = args.commands or []
files_to_copy = args.files or []
remote_dest = args.destination
password = getpass("Password for target machines: ")

# Read target hosts
with open(target_list, 'r') as file:
    hosts = file.read().splitlines()

# Loop through each host
for host in hosts:
    full_host = f"{remote_user}@{host}"
    print(f"\n[+] Connecting to {full_host}")

    # Transfer files
    for local_file in files_to_copy:
        print(f"[*] Copying {local_file} to {remote_dest}")
        subprocess.run([
            "sshpass", "-p", password, "scp",
            "-o", "StrictHostKeyChecking=no",
            local_file, f"{full_host}:{remote_dest}"
        ])

    for cmd in commands:
        print(f"[*] Running: {cmd}")
        full_cmd = f'powershell.exe -Command "{cmd}"'
        proc = subprocess.Popen(
            ["sshpass", "-p", password, "ssh",
             "-o", "StrictHostKeyChecking=no", full_host, full_cmd],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            shell=False
        )
        stdout, stderr = proc.communicate()
        if stdout:
            print(stdout.decode())
        if stderr:
            print(stderr.decode())
    
        time.sleep(0.5)
