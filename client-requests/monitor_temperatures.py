#!~/develop/projects/odin/venv/bin/python
''' Readout 1/second all temperature sensors until the user interrupts '''
from __future__ import print_function#, division, absolute_import

import requests, sys, time

pscu_host = "beagle03.aeg.lan"
if len(sys.argv) > 1:
    pscu_host = sys.argv[1]
url = 'http://{:s}:8888/api/0.1/lpdpower/'.format(pscu_host)
print("Continuously reading all temperatures: (Use Ctrl-C to close script)")
try:
    while True:
        theLot = requests.get(url)
        if theLot.status_code != requests.codes.OK:
            print("Error: {}".format(requests.status_codes._codes[theLot.status_code][0]))
            sys.exit(-1)
        # Read all 11 temperatures, display on the same line
        for index in range(11):
            print("{}: {:.1f}C  ".format(index, theLot.json()['temperature']['sensors'][str(index)]['temperature']), end=' ')
        # Flush stream; add "heartbeat" before reading temps to same line
        sys.stdout.flush()
        time.sleep(0.8)
        print("\r.", end=' ')
        sys.stdout.flush()
        time.sleep(0.2)
        print("\r", end=' ')
except Exception as e:
    print("Exception: {}".format(e))
except KeyboardInterrupt:
    # The user pressed Ctrl-C (to stop the script) 
    print("\n")
