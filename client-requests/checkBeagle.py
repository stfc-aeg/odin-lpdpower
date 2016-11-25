import requests, sys

pscu_host = "beagle03.aeg.lan"
if len(sys.argv) > 1:
    pscu_host = sys.argv[1]
url = 'http://{:s}:8888/api/0.1/lpdpower/'.format(pscu_host)
try:
    response = requests.get(url)
    print("BBB's top-level keys:\n ", list(response.json().keys()))
except requests.exceptions.ConnectionError as e:
    print("Error: ", e)

