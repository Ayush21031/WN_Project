import os
import re
import subprocess
import requests

class PingData:
	'''
	Class to extract the IP address and RTT of the websites
	'''
	def __init__(self):
		self.WEBSITE_SOURCE_FILE = "website.csv"
		self.timeout = 2
		self.GEOLOCATION_API_URL = "http://ip-api.com/json/"

	def getIP(self, websiteAddr):
		'''
		Extracts the IP address of the website using the ping command
		'''
		try:
			ping = subprocess.run(["ping", "-c", "1", websiteAddr], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=self.timeout)
			out = ping.stdout.decode('utf-8')
			# out, error = ping.communicate()
			# now format the output to get the IP address, min RTT, max RTT, avg RTT
			# out = out.decode('utf-8')
			# Extract the IP address from the output
			ipAddr = re.findall(r'[0-9]+(?:\.[0-9]+){3}', out)
			print(f"IP address of {websiteAddr} is {ipAddr[0]}")
			minRTT = re.findall(r'round-trip min/avg/max/stddev = ([0-9.]+)+/([0-9.]+)+/([0-9.]+)+/([0-9.]+|nan) ms', out)
		except Exception as e:
			print(f"Error: {e}")
			return []
		
		result = [i for i in minRTT[0][:-1]]
		result.append(ipAddr[0])
		return result

	def getWebsiteNames(self):
		'''
		Reads the websites from the file and returns a list of websites
		'''
		websites = []
		with open(self.WEBSITE_SOURCE_FILE, 'r') as f:
			for line in f:
				websites.append(line.strip())
		return websites
	
	def saveData(self, data):
		'''
		Saves the data to a file
		'''
		with open('pingData.txt', 'w') as f:
			for d in data:
				try:
					f.write(f"{d[3]},{d[0]},{d[1]},{d[2]},{d[4]}\n")
				except Exception as e:
					print(d)

	def getGeolocation(self,ip_address):
		'''
		Fetches geolocation data for the given IP address using ip-api.com.
		'''
		try:
			response = requests.get(self.GEOLOCATION_API_URL + ip_address, timeout=5)
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

	def main(self):
		statsForAllSites = []
		websiteAddrs = self.getWebsiteNames()
		for websiteAddr in websiteAddrs:
			data = self.getIP(websiteAddr)
			if len(data) == 0:
				continue
			geolocation = self.getGeolocation(data[3])
			data.append(geolocation)
			statsForAllSites.append(data)
		self.saveData(statsForAllSites)
	
if __name__ == '__main__':
	pingData = PingData()
	pingData.main()