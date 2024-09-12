import subprocess
import paramiko #.venv\scripts\pip3 install paramiko
from rich import print as rprint

from rich.console import Console
console = Console(log_path=False)

# https://github.com/RainingComputers/whipFTP
# https://stackoverflow.com/questions/28411960/execute-a-command-on-remote-machine-in-python

import psutil
import os
import platform

import yaml    
import time

import typer
app = typer.Typer()

def read_config_file(yaml_filename: str):
    with open('./' + yaml_filename, 'r', encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return config

def run_command_over_ssh(host, username, password, command):
    # Initialize SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the host
    ssh.connect(host, username=username, password=password)

    # Execute a command (without opening an interactive shell)
    stdin, stdout, stderr = ssh.exec_command(command)

    # Read output
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')

    # Close the connection
    ssh.close()

    # Return the output and any error
    return output, error

def read_remote_file(remote_file_path):
    global ssh_client
    sftp_client = ssh_client.open_sftp()
    with sftp_client.file(remote_file_path, 'r') as remote_file:
        file_content = remote_file.read().decode('utf-8')
    return file_content
    sftp_client.close()

def write_remote_file(remote_file_path, modified_content):
    global ssh_client
    sftp_client = ssh_client.open_sftp()
    with sftp_client.file(remote_file_path, 'w') as remote_file:
        remote_file.write(modified_content.encode('utf-8'))
    print(f"File {remote_file_path} has been updated successfully.")
    sftp_client.close()

def add_dns_zone_to_named_conf(configuration_file_path, zone_name, zone_config):
    # Append the zone configuration to the content
    
    # file_content = read_remote_file(configuration_file_path)
    file_content = read_remote_file_with_sudo(configuration_file_path)
    
    if zone_name not in file_content:
        file_content += zone_config
        print(f"Zone {zone_name} added.")
        
        # write_remote_file(configuration_file_path, file_content)
        write_content_to_remote_file(configuration_file_path, file_content)
    else:
        print(f"Zone {zone_name} already exists.")

    return file_content

def connect_ssh(hostname, port, username, password):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname, port=port, username=username, password=password)
    return ssh_client

def read_remote_file_with_sudo(remote_file_path):
    global ssh_client
    command = f"sudo cat {remote_file_path}"
    stdin, stdout, stderr = ssh_client.exec_command(command)
    
    # Check if there's an error (e.g., permission denied, sudo requiring a password)
    error = stderr.read().decode('utf-8')
    if error:
        raise Exception(f"Error reading file: {error}")
    
    # Read the file content
    file_content = stdout.read().decode('utf-8')
    return file_content



    
def write_content_to_remote_file(remote_file_path, modified_content):
    global ssh_client
    # Create a temporary file on the remote server
    temp_file_path = f"{remote_file_path}.tmp"
    
    # Write the content to the temporary file
    command = f"sudo tee {temp_file_path} > /dev/null <<< '{modified_content}'"
    stdin, stdout, stderr = ssh_client.exec_command(command)
    
    # Check for errors
    error = stderr.read().decode('utf-8')
    if error:
        raise Exception(f"Error writing file: {error}")
    
    # Replace the original file with the temporary file
    move_command = f"sudo mv {temp_file_path} {remote_file_path}"
    stdin, stdout, stderr = ssh_client.exec_command(move_command)
    
    # Check for errors
    error = stderr.read().decode('utf-8')
    if error:
        raise Exception(f"Error moving file: {error}")
    
    print(f"File {remote_file_path} has been updated successfully.")

def generate_timestamp_filename():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    filename = f"temp_{timestamp}"
    return filename


def run_command_over_ssh_multiple(yaml_filename: str):
    
    console.rule("[bold red]"+"Connecting to remote server")
    with console.status("[bold yellow]Reading configuration file...") as status:
        console.log(f"[yellow]{yaml_filename}[/yellow]")
        config = read_config_file(yaml_filename)
#        with open('./' + yaml_filename, 'r', encoding="utf-8") as file:
#            config = yaml.safe_load(file)

    hostname = config['connection']['hostname']
    username = config['connection']['username']
    password = config['connection']['password']
    port = config['connection']['port'] 
            
    console.log(f"[yellow]Remote server: {hostname}[/yellow]")

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())   

    ssh_client.connect(hostname=hostname, username=username,password=password, port=port, timeout=10)
    connection = ssh_client.invoke_shell()

    transport = ssh_client.get_transport()
    transport.set_keepalive(60)

    echo_on = True
    sleeptime = 1

    for command in config['run']:
        console.rule("[bold red]"+command['name'])
        with console.status("[bold yellow]Executing command...") as status:
            for line in command['command']:
                console.log(f"[yellow]{line}[/yellow]")
                try:
                    connection.send(line + "\n")
                    output = bytearray()
                    MAX_BUFFER = 65535
                    not_done = True
                    max_loops = 10
                    i = 0
                    while (not_done) and (i <= max_loops):
                        time.sleep(1)
                        i += 1
                        # Keep reading data as long as available (up to max_loops)
                        if connection.recv_ready():
                            output += connection.recv(MAX_BUFFER)
                        else:
                            not_done = False
                    if echo_on:
                        print(output.decode('utf8').encode('ascii', errors='ignore').decode("utf-8"))
                except Exception as error:
                    print("An exception occurred:", error)

    console.log(f'[bold][red]Done!')
                
    connection.close()   
    ssh_client.close()



ssh_client = ""
import time
import datetime
@app.command()
def run_command(yaml_filename: str):
    global ssh_client
    
    console.rule("[bold red]"+"Connecting to remote server")
    with console.status("[bold yellow]Reading configuration file...") as status:
        console.log(f"[yellow]{yaml_filename}[/yellow]")
        config = read_config_file(yaml_filename)
#        with open('./' + yaml_filename, 'r', encoding="utf-8") as file:
#            config = yaml.safe_load(file)


    hostname = config['connection']['hostname']
    username = config['connection']['username']
    password = config['connection']['password']
    file_type = config['connection']['file_type']
    port = config['connection']['port'] 
            
    console.log(f"[yellow]Remote server: {hostname}[/yellow]")

#    ssh_client = paramiko.SSHClient()
#    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())   

#    ssh_client.connect(hostname=hostname, username=username,password=password, port=port, timeout=10)
    
#    connection = ssh_client.invoke_shell()

#    transport = ssh_client.get_transport()
#    transport.set_keepalive(60)

    # Connect to SSH
    ssh_client = connect_ssh(hostname, port, username, password)
    


    echo_on = True

    if file_type == 'multiple':
        run_command_over_ssh_multiple(yaml_filename)
    else:
        for command in config['run']:
            console.rule("[bold red]"+command['name'])
            with console.status("[bold yellow]Executing command...") as status:
                if command['type'] == 'shell':
                    for line in command['command']:
                        console.log(f"[yellow]{line}[/yellow]")
                        try:
                            output = run_command_over_ssh(hostname, username, password, line)
                            if echo_on:
                                print(output[0])
                                # print(output.decode('utf8').encode('ascii', errors='ignore').decode("utf-8"))
                        except Exception as error:
                            print("An exception occurred:", error)
                            
                            
                elif command['type'] == 'function':
                    line_number = 0
                    function_name = ""
                    function_parameters = []
                    for line in command['command']:
                        if line_number == 0:
                            function_name = line
                        else:
                            function_parameters.append(line)
                        line_number = line_number + 1
                            
                    console.log(f"[yellow]{function_name}[/yellow]")
                    
                    print("function_name:", function_name)
                    print("function_parameters:", function_parameters)
                    
                    globals()[function_name](*function_parameters)
                
                
                

    console.log(f'[bold][red]Done!')
                

    ssh_client.close()

if __name__ == "__main__":
    app()
