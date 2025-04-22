#python snailedit.py -u root -t targets.txt -f ./script.sh config.cfg -d /opt/setup -c "chmod +x /opt/setup/script.sh" "/opt/setup/script.sh" -o Filename_IPautoAttached

import argparse
import subprocess
import time
import os
from getpass import getpass, getuser


# Define command-line arguments
parser = argparse.ArgumentParser(description="Run remote commands and copy files to target hosts over SSH")
parser.add_argument("-u", "--user", help="Username for target systems")
parser.add_argument("-t", "--target-list", required=True, help="Path to file containing list of target hosts")
parser.add_argument("-c", "--commands", nargs='+', help="Commands to run on remote systems")
parser.add_argument("-f", "--files", nargs='+', help="Files to transfer to remote systems")
parser.add_argument("-d", "--destination", default="/tmp/", help="Remote destination directory for transferred files")
parser.add_argument("-o", "--output", help="Output file name") # Output file argument
args = parser.parse_args()

# Collect inputs
remote_user = args.user or getuser()
target_list = args.target_list
commands = args.commands or []
files_to_copy =args.files or []
remote_dest = args.destination
output_filename = args.output  # Get output filename
password = getpass("Password for target machines: ")


# Read target hosts
with open(target_list, 'r') as file:
    hosts = file.read().splitlines()

# Loop through each host
for host in hosts:
    full_host = f"{remote_user}@{host}"
    log_message = f"\n[+] Connecting to {full_host}\n" #store message so we don't have to write it twice
    print(log_message)
    # Create host-specific output filename (if specified)
    output_file = None

    # Handle output to file (if specified)
    if output_filename:
        base_filename, ext = os.path.splitext(output_filename)  # Split filename and extension
        output_file = f"{base_filename}_{host}{ext}"

        #open the file
        with open(output_file, 'a') as outfile:
            outfile.write(log_message)

            # Transfer files
            for local_file in files_to_copy:
                transfer_message = f"[*] Copying {local_file} to {remote_dest}\n"
                print(transfer_message)
                if output_file:
                    outfile.write(transfer_message)
                subprocess.run([
                    "sshpass", "-p", password, "scp",
                    "-o", "StrictHostKeyChecking=no",
                    local_file, f"{full_host}:{remote_dest}"
                ])

            # Run commands
            for cmd in commands:
                cmd_message = f"[*] Running: {cmd}\n"
                full_cmd =f'echo "{password}"| sudo -S {cmd}'
                print(cmd_message)
                if output_file:
                    outfile.write(cmd_message)
                proc = subprocess.Popen(
                    ["sshpass", "-p", password, "ssh",
                     "-o", "StrictHostKeyChecking=no", full_host, full_cmd],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=False
                )
                stdout, stderr = proc.communicate()
                if stdout:
                    print(stdout.decode())
                    if output_file:
                        outfile.write(stdout.decode())
                if stderr:
                    print(stderr.decode())
                    if output_file:
                        outfile.write(stderr.decode())
                time.sleep(0.5)

    #If no output file, proceed as before
    else:
        # Transfer files
        for local_file in files_to_copy:
            print(f"[*] Copying {local_file} to {remote_dest}")
            subprocess.run([
                "sshpass", "-p", password, "scp",
                "-o", "StrictHostKeyChecking=no",
                local_file, f"{full_host}:{remote_dest}"
            ])
        # Run commands
        for cmd in commands:
            print(f"[*] Running: {cmd}")
            full_cmd =f'echo "{password}"| sudo -S {cmd}'
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
