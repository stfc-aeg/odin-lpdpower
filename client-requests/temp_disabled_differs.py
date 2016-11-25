#!~/develop/projects/odin/venv/bin/python

''' Demonstrate how temperature sensor data type is either int/bool for dictionary key 'disabled' '''
from __future__ import print_function
from pscu_client import PSCUClient
import sys

pscu_host = "beagle03.aeg.lan"
if len(sys.argv) > 1:
    pscu_host = sys.argv[1]

thePSCU = PSCUClient(address=pscu_host, port=8888)

# Access temperature sensor info
temps = thePSCU.dict['temperature']['sensors']
channels = len(temps)
for channel in range(channels):
    chInfo        = temps[str(channel)]
    print("Ch{0:<2}:  ".format(channel), end=' ')
    print("Enable? {}  (Type: {})".format(chInfo['disabled'], type(chInfo['disabled'])))

print("But it doesn't matter if int/bool, if we invert disabled to display as enabled:")

for channel in range(channels):
    chInfo        = temps[str(channel)]
    print("Ch{0:<2}:  ".format(channel), end=' ')
    bValue = (True if chInfo['disabled'] == 0 else False)
    print("Enable? {}  (Type: {})".format(bValue, type(chInfo['disabled'])))
