import requests

GEOLOCATION_API_URL = "http://ip-api.com/json/"
ip_address = "203.115.96.82"
response = requests.get(GEOLOCATION_API_URL + ip_address, timeout=5)
data = response.json()
if data['status'] == 'success':
    print(data.get('country', ''))
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
			