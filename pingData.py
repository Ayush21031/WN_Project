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
		self.timeout = 5
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
			ipAddr_ipv6 = re.findall(r"Address:\s+([0-9a-fA-F:]+)", out_ipv6)
			# ipAddr_ipv6 = re.findall(r"Address: \s+([0-9a-fA-F:]+)", out_ipv6)
			# check if the IP address is found
			if len(ipAddr_ipv4) == 0 or len(ipAddr_ipv6) == 0:
				return []
			print("nslookup done")
			return [ipAddr_ipv4[0], ipAddr_ipv6[-1]]
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
				minRTT = re.findall(r'rtt min/avg/max/mdev = ([0-9.]+)+/([0-9.]+)+/([0-9.]+)+/([0-9.]+|nan) ms', out)
			else:
				ping = subprocess.run(["ping6", "-c", "5", ip_addr], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				out = ping.stdout.decode('utf-8')
				minRTT = re.findall(r'rtt min/avg/max/mdev = ([0-9.]+)+/([0-9.]+)+/([0-9.]+)+/([0-9.]+|nan)', out)
		except Exception as e:
			print(f"Error: {e}")
			return []
		if minRTT == []:
			return []
		result = [i for i in minRTT[0][:-1]]
		print(result)
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
		with open('pingData3.txt', 'w') as f:
			for d in data:
				try:
					# f.write(f"{d[0]}, {d[1]}, {d[2]}, {d[3]}, {d[4]}, {d[5]}, {d[6]} \n")
					f.write(f"{d[0]}, {d[1]}, {d[2]}, {d[3]}, {d[4]} \n")
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
			data = self.getPingStats(websiteAddr)
			if len(data) == 0:
				continue
			geolocation = self.getGeolocation(data[3])
			data.append(geolocation)
			statsForAllSites.append(data)
		self.saveData(statsForAllSites)
	
	def mainTest(self):
		f = open("ipdata.txt","a")
		statsForAllSites = []
		websiteAddrs = self.getWebsiteNames()
		for websiteAddr in websiteAddrs:
			print("getting data for ", websiteAddr)
			data = self.getIPv4_IPv6(websiteAddr)
			print(data)
			f.write(f"{websiteAddr},{data[0]},{data[1]}\n")
			if len(data) !=2:
				print("data not found")
				continue
			ipv4_ping_stats = self.getPingStats(data[0], False)
			ipv6_ping_stats = self.getPingStats(data[1], True)
			print(f"IPv4: {data[0]}: {ipv4_ping_stats}")
			print(f"IPv6: {data[1]}: {ipv6_ping_stats}")
			if len(ipv4_ping_stats) == 0 or len(ipv6_ping_stats) == 0:
				print("ping stats not found")
				continue
			# geolocation_ipv4 = self.getGeolocation(data[0])
			# geolocation_ipv6 = self.getGeolocation(data[1])
			complete_data = []
			complete_data.append(websiteAddr)
			complete_data.append(data[0])
			complete_data.append(str(ipv4_ping_stats))
			# complete_data.append(geolocation_ipv4)
			complete_data.append(data[1])
			complete_data.append(str(ipv6_ping_stats))
			# complete_data.append(geolocation_ipv6)
			statsForAllSites.append(complete_data)
			print(f"IPv4: {data[0]}: {ipv4_ping_stats}")
			print(f"IPv6: {data[1]}: {ipv6_ping_stats}")
		self.saveData(statsForAllSites)
		f.close()



	
if __name__ == '__main__':
	pingData = PingData()
	# pingData.main()
	pingData.mainTest()
