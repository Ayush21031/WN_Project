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

def main():
    # Fixed IPv4 and IPv6 addresses
    ipv4_address = "8.8.8.8"  # Google Public DNS IPv4
    ipv6_address = "2001:4860:4860::8888"  # Google Public DNS IPv6

    os_type = platform.system()

    if os_type == "Windows":
        # Windows uses 'tracert'
        traceroute_cmd_ipv4 = ["tracert", "-4", ipv4_address]
        traceroute_cmd_ipv6 = ["tracert", "-6", ipv6_address]
    else:
        # Unix-like systems use 'traceroute'
        traceroute_cmd_ipv4 = ["traceroute", "-4", ipv4_address]
        traceroute_cmd_ipv6 = ["traceroute", "-6", ipv6_address]

    print(f"Running traceroute for IPv4 to {ipv4_address}...")
    output_ipv4 = run_traceroute(traceroute_cmd_ipv4)
    if os_type == "Windows":
        hops_ipv4 = count_hops_windows(output_ipv4)
    else:
        hops_ipv4 = count_hops_unix(output_ipv4)
    print(f"IPv4: Number of hops = {hops_ipv4}")

    print(f"\nRunning traceroute for IPv6 to {ipv6_address}...")
    output_ipv6 = run_traceroute(traceroute_cmd_ipv6)
    if os_type == "Windows":
        hops_ipv6 = count_hops_windows(output_ipv6)
    else:
        hops_ipv6 = count_hops_unix(output_ipv6)
    print(f"IPv6: Number of hops = {hops_ipv6}")

if __name__ == "__main__":
    main()
