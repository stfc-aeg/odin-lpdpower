#!~/develop/projects/odin/venv/bin/python
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
except KeyboardInterrupt:
    print("\n")
print("\nAll Done")
