import requests, json
import pprint, sys

pscu_host = "beagle03.aeg.lan"
if len(sys.argv) > 1:
    pscu_host = sys.argv[1]
url = 'http://{:s}:8888/api/0.1/lpdpower/'.format(pscu_host)

pp = pprint.PrettyPrinter()

garbage_put = 'rubbish_1234'
headers = {"Content-Type" : 'application/json'}

response = requests.put(url, data=garbage_put, headers=headers)
print(response.status_code, response.json())

get_bad_path = url + 'missing'
response = requests.get(get_bad_path)
print(response.status_code, response.json())
