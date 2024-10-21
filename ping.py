# import pandas as pd
# import subprocess
# import platform
# import re
# import csv
# import requests
# import time
# from datetime import datetime

# # Constants
# INPUT_CSV = 'website_ip_addresses.csv'
# PING_RTT_CSV = 'ping_rtt.csv'
# GEOLOCATION_CSV = 'geolocation_data.csv'
# PING_COUNT = 10
# GEOLOCATION_API_URL = 'http://ip-api.com/json/'  # Using ip-api.com for geolocation

# def ping_host(ip_address, count=PING_COUNT):
#     """
#     Pings the given IP address and returns a list of RTTs in milliseconds.
#     """
#     # Determine the parameter based on OS
#     param = '-n' if platform.system().lower() == 'windows' else '-c'
#     # For IPv6, use appropriate parameter if needed
#     # Build the ping command
#     command = ['ping', param, str(count), ip_address]
    
#     try:
#         output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
#         # Extract RTTs using regex
#         # This regex works for both Windows and Unix ping outputs
#         rtts = re.findall(r'time[=<]([\d\.]+) ?ms', output)
#         # Convert RTTs to float
#         rtts = [float(rtt) for rtt in rtts]
#         return rtts
#     except subprocess.CalledProcessError as e:
#         print(f"Failed to ping {ip_address}. Error: {e}")
#         return []

# def get_geolocation(ip_address):
#     """
#     Fetches geolocation data for the given IP address using ip-api.com.
#     """
#     try:
#         response = requests.get(GEOLOCATION_API_URL + ip_address, timeout=5)
#         data = response.json()
#         if data['status'] == 'success':
#             return {
#                 'country': data.get('country', ''),
#                 'regionName': data.get('regionName', ''),
#                 'city': data.get('city', ''),
#                 'lat': data.get('lat', ''),
#                 'lon': data.get('lon', ''),
#                 'timezone': data.get('timezone', ''),
#                 'isp': data.get('isp', ''),
#                 'org': data.get('org', ''),
#                 'as': data.get('as', '')
#             }
#         else:
#             print(f"Geolocation failed for {ip_address}: {data.get('message', 'No message')}")
#             return {}
#     except Exception as e:
#         print(f"Error fetching geolocation for {ip_address}: {e}")
#         return {}

# def main():
#     # Read the input CSV
#     try:
#         df = pd.read_csv(INPUT_CSV)
#     except FileNotFoundError:
#         print(f"Input file '{INPUT_CSV}' not found.")
#         return

#     # Prepare CSV writers
#     with open(PING_RTT_CSV, mode='w', newline='') as rtt_file, \
#          open(GEOLOCATION_CSV, mode='w', newline='') as geo_file:
        
#         # Define headers for ping RTT CSV
#         rtt_writer = csv.writer(rtt_file)
#         rtt_header = ['Domain', 'Address Type', 'IP Address'] + [f'Ping_{i+1}_RTT(ms)' for i in range(PING_COUNT)]
#         rtt_writer.writerow(rtt_header)
        
#         # Define headers for geolocation CSV
#         geo_writer = csv.writer(geo_file)
#         geo_header = ['Domain', 'Address Type', 'IP Address', 'Country', 'Region', 'City', 
#                       'Latitude', 'Longitude', 'Timezone', 'ISP', 'Organization', 'AS', 'Timestamp']
#         geo_writer.writerow(geo_header)
        
#         # Iterate over each row in the dataset
#         for index, row in df.iterrows():
#             domain = row['Domain']
#             ipv4 = row['IPv4']
#             ipv6 = row['IPv6']
            
#             # List of tuples: (Address Type, IP Address)
#             addresses = []
#             if pd.notna(ipv4) and ipv4.lower() != 'no ipv6':
#                 addresses.append(('IPv4', ipv4))
#             if pd.notna(ipv6) and ipv6.lower() != 'no ipv6':
#                 addresses.append(('IPv6', ipv6))
            
#             for addr_type, ip in addresses:
#                 print(f"Pinging {domain} ({addr_type}: {ip})")
                
#                 # Ping the IP address
#                 rtts = ping_host(ip)
                
#                 # If less RTTs are returned than expected, pad with None
#                 if len(rtts) < PING_COUNT:
#                     rtts += [None] * (PING_COUNT - len(rtts))
                
#                 # Write RTT data
#                 rtt_row = [domain, addr_type, ip] + rtts
#                 rtt_writer.writerow(rtt_row)
                
#                 # Fetch geolocation data
#                 geolocation = get_geolocation(ip)
#                 timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                
#                 geo_row = [
#                     domain,
#                     addr_type,
#                     ip,
#                     geolocation.get('country', ''),
#                     geolocation.get('regionName', ''),
#                     geolocation.get('city', ''),
#                     geolocation.get('lat', ''),
#                     geolocation.get('lon', ''),
#                     geolocation.get('timezone', ''),
#                     geolocation.get('isp', ''),
#                     geolocation.get('org', ''),
#                     geolocation.get('as', ''),
#                     timestamp
#                 ]
#                 geo_writer.writerow(geo_row)
                
#                 # To respect API rate limits
#                 time.sleep(1)  # Adjust as necessary

#     print("Ping and geolocation data collection complete.")

# if __name__ == "__main__":
#     main()




import csv
import os
import subprocess
import time
from datetime import datetime
import requests

# Define the API for geolocation (use an appropriate API like ipinfo.io, ipapi.co, or freegeoip.app)
GEOLOCATION_API_URL = "http://ip-api.com/json/"

# Function to ping an IP address and return the RTTs
def ping_ip(ip, count=10):
    try:
        # Check if the IP is IPv4 or IPv6
        if ":" in ip:
            ping_cmd = f"ping6 -c {count} {ip}"  # For IPv6
        else:
            ping_cmd = f"ping -c {count} {ip}"  # For IPv4

        # Execute the ping command
        result = subprocess.run(ping_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode()

        # Extract RTTs from the ping output
        rtt_lines = [line for line in output.split('\n') if 'time=' in line]
        rtts = [float(line.split('time=')[-1].split(' ')[0]) for line in rtt_lines]
        return rtts

    except Exception as e:
        print(f"Error pinging IP {ip}: {e}")
        return []

# Function to get geolocation of an IP address
def get_geolocation(ip):
    try:
        response = requests.get(GEOLOCATION_API_URL + ip)
        data = response.json()
        if data['status'] == 'success':
            return data['country'], data['regionName'], data['city']
        else:
            return None, None, None
    except Exception as e:
        print(f"Error fetching geolocation for IP {ip}: {e}")
        return None, None, None

# Function to write the RTT results to a CSV
def write_to_csv(filename, data):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)

# Main function to process the CSV file and ping each IP address
def main():
    # Open the input CSV
    with open('website_ip_addresses.csv', mode='r') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Skip headers

        # Loop through each website and ping IPv4 and IPv6
        for row in reader:
            domain, ipv4, ipv6 = row

            # Get current timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Ping IPv4
            if ipv4 != 'No IPv4':
                rtts_ipv4 = ping_ip(ipv4)
                country, region, city = get_geolocation(ipv4)
                for rtt in rtts_ipv4:
                    write_to_csv('ipv4_rtt.csv', [domain, ipv4, rtt, timestamp, country, region, city])

            # Ping IPv6
            if ipv6 != 'No IPv6':
                rtts_ipv6 = ping_ip(ipv6)
                country, region, city = get_geolocation(ipv6)
                for rtt in rtts_ipv6:
                    write_to_csv('ipv6_rtt.csv', [domain, ipv6, rtt, timestamp, country, region, city])
            print(f"{row[0]} Done")

if __name__ == "__main__":
    # Create CSV files with headers if they don't exist
    if not os.path.exists('ipv4_rtt.csv'):
        write_to_csv('ipv4_rtt.csv', ['Domain', 'IPv4', 'RTT', 'Timestamp', 'Country', 'Region', 'City'])
    
    if not os.path.exists('ipv6_rtt.csv'):
        write_to_csv('ipv6_rtt.csv', ['Domain', 'IPv6', 'RTT', 'Timestamp', 'Country', 'Region', 'City'])
    
    # Run the main process
    main()
