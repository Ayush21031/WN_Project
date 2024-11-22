import os
import re
import subprocess
import requests
import datetime
import threading
import json

class PingData:
	'''
	Class to extract the IP address and RTT of the websites
	'''
	def __init__(self, isp):
		self.WEBSITE_SOURCE_FILE = "websites/website.csv"
		self.timeout = 5
		self.isp = isp
		self.GEOLOCATION_API_URL = "http://ip-api.com/json/"

	def getIPv4_IPv6(self, websiteAddr):
		'''
		Extracts the IP address of the website using the ping command
		'''
		try:
			nslookup_ipv4 = subprocess.run(["nslookup", "-type=A", websiteAddr], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=self.timeout)
			nslookup_ipv6 = subprocess.run(["nslookup", "-type=AAAA", websiteAddr], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=self.timeout)
			out_ipv4 = nslookup_ipv4.stdout.decode('utf-8')
			out_ipv6 = nslookup_ipv6.stdout.decode('utf-8')
			# Extract the IP address from the output
			ipAddr_ipv4 = re.findall(r'Address: ([0-9]+(?:\.[0-9]+){3})', out_ipv4)
			ipAddr_ipv6 = re.findall(r"AAAA address\s+([0-9a-fA-F:]+)", out_ipv6)
			# check if the IP address is found
			if len(ipAddr_ipv4) == 0 or len(ipAddr_ipv6) == 0:
				return []
			print("nslookup done")
			return [ipAddr_ipv4[0], ipAddr_ipv6[0]]
		except Exception as e:
			print(f"Error: {e}")
			return []

	def getPingStats(self, ip_addr, flag):
		'''
		Extracts the IP address of the website using the ping command
		'''
		try:
			if not flag:
				ping = subprocess.run(["ping", "-c", "5", ip_addr], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				out = ping.stdout.decode('utf-8')
				minRTT = re.findall(r'round-trip min/avg/max/stddev = ([0-9.]+)+/([0-9.]+)+/([0-9.]+)+/([0-9.]+|nan) ms', out)
			else:
				ping = subprocess.run(["ping6", "-c", "5", ip_addr], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				out = ping.stdout.decode('utf-8')
				minRTT = re.findall(r'round-trip min/avg/max/std-dev = ([0-9.]+)+/([0-9.]+)+/([0-9.]+)+/([0-9.]+|nan) ms', out)
		except Exception as e:
			print(f"Error: {e}")
			return []
		if minRTT == []:
			return []
		result = [float(i) for i in minRTT[0][:-1]]
		return [sum(result)/3]

	def getWebsiteNames(self):
		'''
		Reads the websites from the file and returns a list of websites
		'''
		websites = []
		with open(self.WEBSITE_SOURCE_FILE, 'r') as f:
			for line in f:
				websites.append(line.strip())
		return websites
	
	def saveData(self, data, iterationNumber):
		'''
		Saves the data to a file
		'''
		currDateTime = datetime.datetime.now().strftime("%Y-%m-%d|%H")
		dataJson = {}
		for d in data:
			dataJson[d[0]] = {
				'ipv4': {
					'ip': d[1],
					'ping': d[2],
					'geolocation': d[3]
				},
				'ipv6': {
					'ip': d[4],
					'ping': d[5],
					'geolocation': d[6]
				},
				'wget': d[7]
			}
		with open(f'results/{currDateTime}|{self.isp}.txt|{iterationNumber}', 'a') as f:
			# for d in data:
			try:
				json.dump(dataJson, f, indent=4)
				# f.write(f"{d[0]}, {d[1]}, {d[2]}, {d[3]}, {d[4]}, {d[5]}, {d[6]}, {d[7]} \n")
			except Exception as e:
				print(d)

	def getGeolocation(self,ip_address):
		'''
		Fetches geolocation data for the given IP address using ip-api.com.
		'''
		try:
			response = requests.get(self.GEOLOCATION_API_URL + ip_address + "?fields=country,status", timeout=5)
			data = response.json()
			if data['status'] == 'success':
				return data.get('country', '')
				# return {
				# 	'country': data.get('country', ''),
				# 	'regionName': data.get('regionName', ''),
				# 	'city': data.get('city', ''),
				# 	'lat': data.get('lat', ''),
				# 	'lon': data.get('lon', ''),
				# 	'timezone': data.get('timezone', ''),
				# 	'isp': data.get('isp', ''),
				# 	'org': data.get('org', ''),
				# 	'as': data.get('as', '')
				# }
			else:
				print(f"Geolocation failed for {ip_address}: {data.get('message', 'No message')}")
				return {}
		except Exception as e:
			print(f"Error fetching geolocation for {ip_address}: {e}")
			return {}

	def get_wget_stats(self, website_url):
		"""
		Extracts the download time from the wget command output.
		Returns the download time in seconds as a float.
		"""
		try:
			# Run the wget command
			wget = subprocess.run(["wget", "-O", "/dev/null", website_url], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=self.timeout)
			output = wget.stderr  # The relevant timing data is in stdout
			
			# Look for the download time in the format `352K=0.06s`
			match = re.search(r'=\s*([\d.]+)s', output)
			if match:
				download_time = float(match.group(1))
				return download_time
			else:
				print("Download time not found in wget output.")
				return None
		except Exception as e:
			print(f"timed out while fetching wget data for {website_url}")
			return None
	
	def run(self, rangeLower, rangeUpper, iterationNumber):
		statsForAllSites = []
		websiteAddrs = self.getWebsiteNames()
		for websiteAddr in websiteAddrs[rangeLower:rangeUpper]:
			print("getting data for ", websiteAddr)
			data = self.getIPv4_IPv6(websiteAddr)
			if len(data) !=2:
				print("data not found")
				print("Trying again!!")
				data = self.getIPv4_IPv6(websiteAddr)
				if len(data)!=2:
					print("data not found again")
					continue
			ipv4_ping_stats = self.getPingStats(data[0], False)
			ipv6_ping_stats = self.getPingStats(data[1], True)
			if len(ipv4_ping_stats) == 0 or len(ipv6_ping_stats) == 0:
				print("ping stats not found")
				print("Trying again!!")
				ipv4_ping_stats = self.getPingStats(data[0], False)
				ipv6_ping_stats = self.getPingStats(data[1], True)
				if len(ipv4_ping_stats) == 0 or len(ipv6_ping_stats) == 0:
					print("ping stats not found again")
					continue
			geolocation_ipv4 = self.getGeolocation(data[0])
			geolocation_ipv6 = self.getGeolocation(data[1])
			wget_stats = self.get_wget_stats(websiteAddr)
			if wget_stats is None:
				continue
			complete_data = []
			complete_data.append(websiteAddr)
			complete_data.append(data[0])
			complete_data.append(str(ipv4_ping_stats))
			complete_data.append(geolocation_ipv4)
			complete_data.append(data[1])
			complete_data.append(str(ipv6_ping_stats))
			complete_data.append(geolocation_ipv6)
			complete_data.append(wget_stats)
			statsForAllSites.append(complete_data)
			print(f"IPv4: {data[0]}: {ipv4_ping_stats} geolocation: {geolocation_ipv4} wget: {wget_stats}")
			print(f"IPv6: {data[1]}: {ipv6_ping_stats} geolocation: {geolocation_ipv6} wget: {wget_stats}")
		self.saveData(statsForAllSites, iterationNumber)

def main():
	isp = input("Enter the ISP name: ")
	pingData = PingData(isp)
	for iterationNumber in range(1, 3):
		threads = []
		for i in range(0, 159, 10):
			t = threading.Thread(target=pingData.run, args=(i, i+10, iterationNumber))
			threads.append(t)
			t.start()
		for t in threads:
			t.join()
	
if __name__ == '__main__':
	main()
