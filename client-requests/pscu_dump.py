'''
Created on Aug 23, 2016

@author: tcn45
'''
import requests, json
import pprint 
import sys

pscu_host='beagle03.aeg.lan'
if len(sys.argv) > 1:
    pscu_host=sys.argv[1]

url = 'http://{:s}:8888/api/0.1/lpdpower/'.format(pscu_host)

pp = pprint.PrettyPrinter()

response = requests.get(url)
pscu_status = response.json()
pp.pprint(pscu_status)
