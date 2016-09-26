import requests
url = 'http://beagle04.aeg.lan:8888/api/0.1/lpdpower/'
try:
    response = requests.get(url)
    print "BBB's top-level keys:\n ", response.json().keys()
except requests.exceptions.ConnectionError as e:
    print "Error: ", e

