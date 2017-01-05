'''
Dump PSCU data tree (but in a formatted display)

@author: ckd27546
'''
import requests, json
import pprint, httplib 
import sys

pscu_host='beagle03.aeg.lan'
if len(sys.argv) > 1:
    pscu_host=sys.argv[1]

url = 'http://{:s}:8888/api/0.1/lpdpower/'.format(pscu_host)

pp = pprint.PrettyPrinter()

try:
    response = requests.get(url)
    if response.status_code != requests.codes.OK:
        print("Error: {}; Couldn't get() data".format(httplib.responses[response.status_code]))
        sys.exit(-1)
    pscu_status = response.json()
    pp.pprint(pscu_status)
except Exception as e:
    print("Exception: {}".format(e))
