#!~/develop/projects/odin/venv/bin/python

import requests

theLot = requests.get('http://beagle03.aeg.lan:8888/api/0.1/lpdpower/')

temp0 = theLot.json()['temperature']['sensors']['0']['temperature']

for index in range(9):
    print "Temp{}: {:.1f}C".format(index, theLot.json()['temperature']['sensors'][str(index)]['temperature'])
