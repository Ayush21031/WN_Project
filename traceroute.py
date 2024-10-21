import subprocess
import platform
import re
import sys

def run_traceroute(command):
    """
    Runs the traceroute/tracert command and returns the output.
    """
    try:
        # Execute the command and capture the output
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(command)}")
        print(e.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Command not found: {command[0]}")
        sys.exit(1)

def count_hops_unix(output):
    """
    Counts the number of hops from traceroute output on Unix-like systems.
    """
    hop_count = 0
    for line in output.splitlines():
        # Traceroute lines typically start with the hop number
        if re.match(r'^\s*\d+', line):
            hop_count += 1
    return hop_count

def count_hops_windows(output):
    """
    Counts the number of hops from tracert output on Windows systems.
    """
    hop_count = 0
    for line in output.splitlines():
        # Tracert lines typically start with the hop number followed by spaces
        if re.match(r'^\s*\d+', line):
            hop_count += 1
    return hop_count

def read_ping_data(file_path):
    """
    Reads the pingData3.txt file and extracts the domain, IPv4, and IPv6 addresses.
    """
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            domain = parts[0].strip()
            ipv4_address = parts[1].strip()
            ipv6_address = parts[5].strip()
            data.append((domain, ipv4_address, ipv6_address))
    return data

def write_hops_data(file_path, hops_data):
    """
    Writes the hops data (domain, IPv4 hops, IPv6 hops) to a file.
    """
    with open(file_path, 'w') as file:
        for domain, hops_ipv4, hops_ipv6 in hops_data:
            file.write(f"{domain}, IPv4 hops: {hops_ipv4}, IPv6 hops: {hops_ipv6}\n")

def main():
    # File paths
    ping_data_file = 'pingData3.txt'
    output_hops_file = 'hopsData.txt'

    # Read data from pingData3.txt
    ping_data = read_ping_data(ping_data_file)

    os_type = platform.system()

    hops_data = []

    for domain, ipv4_address, ipv6_address in ping_data:
        # Run traceroute for IPv4
        print(f"Running traceroute for IPv4 to {ipv4_address} ({domain})...")
        if os_type == "Windows":
            traceroute_cmd_ipv4 = ["tracert", "-4", ipv4_address]
        else:
            traceroute_cmd_ipv4 = ["traceroute", "-4", ipv4_address]
        
        output_ipv4 = run_traceroute(traceroute_cmd_ipv4)
        if os_type == "Windows":
            hops_ipv4 = count_hops_windows(output_ipv4)
        else:
            hops_ipv4 = count_hops_unix(output_ipv4)

        # Run traceroute for IPv6
        print(f"Running traceroute for IPv6 to {ipv6_address} ({domain})...")
        if os_type == "Windows":
            traceroute_cmd_ipv6 = ["tracert", "-6", ipv6_address]
        else:
            traceroute_cmd_ipv6 = ["traceroute", "-6", ipv6_address]

        output_ipv6 = run_traceroute(traceroute_cmd_ipv6)
        if os_type == "Windows":
            hops_ipv6 = count_hops_windows(output_ipv6)
        else:
            hops_ipv6 = count_hops_unix(output_ipv6)

        # Append the hops data for this domain
        hops_data.append((domain, hops_ipv4, hops_ipv6))

    # Write the results to hopsData.txt
    write_hops_data(output_hops_file, hops_data)
    print(f"Traceroute hops data saved to {output_hops_file}")

if __name__ == "__main__":
    main()
