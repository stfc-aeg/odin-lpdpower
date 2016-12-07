#!~/develop/projects/odin/venv/bin/python

import requests, sys

pscu_host='beagle03.aeg.lan'
if len(sys.argv) > 1:
    pscu_host=sys.argv[1]

url = 'http://{:s}:8888/api/0.1/lpdpower/'.format(pscu_host)

try:
    theLot = requests.get(url)
    if theLot.status_code != requests.codes.OK:
        print "Error {} Couldn't get() data".format(theLot.status_code)
        sys.exit(-1)

except Exception as e:
    print("Exception: {}".format(e))
    sys.exit(-1)
for index in range(11):
    print("Temp{}: {:.1f}C".format(index, theLot.json()['temperature']['sensors'][str(index)]['temperature']))

print("All Done")
