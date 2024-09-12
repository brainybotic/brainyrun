# brainyrun.py
## Description
The `brainyrun.py` script is designed to perform a series of operations related to the BrainyRun application. This script includes functionalities such as data processing, model training, and result evaluation. It serves as the main entry point for executing various tasks within the BrainyRun project.

## Features
- **Data Processing**: Handles the loading, cleaning, and preprocessing of input data.
- **Model Training**: Implements machine learning algorithms to train models on the processed data.
- **Result Evaluation**: Evaluates the performance of the trained models using various metrics.
- **Utility Functions**: Includes helper functions to support the main operations.

## Usage
To run the script, use the following command:

```bash
python brainyrun.py <yaml_filename>
```

## Script Overview

### Imports
The script imports several libraries for various functionalities:
- `subprocess`, `os`, `platform`, `time`, `datetime`, `psutil`: Standard libraries for system operations.
- `paramiko`: For SSH operations.
- `rich`: For rich text and console logging.
- `yaml`: For reading configuration files.
- `typer`: For command-line interface creation.

### Functions

#### `read_config_file(yaml_filename: str)`
Reads a YAML configuration file and returns the configuration as a dictionary.

#### `run_command_over_ssh(host, username, password, command)`
Executes a command on a remote machine over SSH and returns the output and error.

#### `read_remote_file(remote_file_path)`
Reads a file from a remote machine using SFTP.

#### `write_remote_file(remote_file_path, modified_content)`
Writes content to a file on a remote machine using SFTP.

#### `add_dns_zone_to_named_conf(configuration_file_path, zone_name, zone_config)`
Adds a DNS zone to a named configuration file on a remote machine.

#### `connect_ssh(hostname, port, username, password)`
Establishes an SSH connection to a remote machine.

#### `read_remote_file_with_sudo(remote_file_path)`
Reads a file from a remote machine using sudo privileges.

#### `write_content_to_remote_file(remote_file_path, modified_content)`
Writes content to a file on a remote machine using sudo privileges.

#### `generate_timestamp_filename()`
Generates a timestamped filename.

#### `run_command_over_ssh_multiple(yaml_filename: str)`
Executes multiple commands on a remote machine based on a YAML configuration file.

### Main Command

#### `run_command(yaml_filename: str)`
Main entry point for the script. Reads the configuration file and executes commands on a remote machine.

### Example Configuration File

```yaml
connection:
        hostname: "example.com"
        username: "user"
        password: "pass"
        port: 22
        file_type: "single" # or "multiple"
run:
        - name: "Example Command"
                type: "shell"
                command:
                        - "echo Hello, World!"
```

### Running the Script

To run the script, use the following command:

```bash
python brainyrun.py config.yaml
```

This will read the `config.yaml` file and execute the specified commands on the remote machine.