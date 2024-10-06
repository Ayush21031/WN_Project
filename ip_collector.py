import socket
import csv

# Function to get IPv4 and IPv6 addresses
def get_ip_addresses(domain):
    ipv4 = "No IPv4"
    ipv6 = "No IPv6"

    # Get IPv4 address using socket
    try:
        ipv4_info = socket.getaddrinfo(domain, None, socket.AF_INET)  # IPv4
        ipv4 = ipv4_info[0][4][0]
    except socket.gaierror:
        ipv4 = "No IPv4"

    # Get IPv6 address using socket
    try:
        ipv6_info = socket.getaddrinfo(domain, None, socket.AF_INET6)  # IPv6
        ipv6 = ipv6_info[0][4][0]
    except socket.gaierror:
        ipv6 = "No IPv6"

    return ipv4, ipv6

# Read the domain list from the input CSV
input_csv = 'website.csv'   # Replace with the actual path to the input CSV file
output_csv = 'website_ip_addresses.csv'

with open(input_csv, mode='r') as infile, open(output_csv, mode='w', newline='') as outfile:
    reader = csv.reader(infile)
    fieldnames = ['Domain', 'IPv4', 'IPv6']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)

    # Write the header row
    writer.writeheader()

    # Loop through each domain and fetch IP addresses
    for row in reader:
        domain = row[0]  # Since the CSV now contains only one column (domain names)
        
        # Get the IP addresses using socket.getaddrinfo
        ipv4, ipv6 = get_ip_addresses(domain)
        
        # Write to the output CSV file
        writer.writerow({'Domain': domain, 'IPv4': ipv4, 'IPv6': ipv6})

print(f"IP addresses for all domains have been stored in {output_csv}")
