''' Test accessing and displaying of top-level keys are working '''
import requests, sys

pscu_host = "beagle03.aeg.lan"
if len(sys.argv) > 1:
    pscu_host = sys.argv[1]
url = 'http://{:s}:8888/api/0.1/lpdpower/'.format(pscu_host)
try:
    response = requests.get(url)
    if response.status_code != requests.codes.OK:
        print("Error: {}".format(requests.status_codes._codes[response.status_code][0]))
        sys.exit(-1)
    print("BBB's top-level keys: {}\n ".format(list(response.json().keys())))
except requests.exceptions.ConnectionError as e:
    print("Exception: {}".format(e))

