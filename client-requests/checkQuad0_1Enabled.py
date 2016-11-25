import requests, pprint
import sys

pscu_host = "beagle03.aeg.lan"
if len(sys.argv) > 1:
    pscu_host = sys.argv[1]
url = 'http://{:s}:8888/api/0.1/lpdpower/'.format(pscu_host)
response = requests.get(url)
#response.json().keys()
#[u'fan', u'enableInterval', u'temperature', u'trace', u'overall', u'pump', u'humidity', u'allEnabled', u'displayError', u'position', u'quad', u'armed', u'latched']
pp = pprint.PrettyPrinter(indent=2)
#pp.pprint("Quad 0 Supplies:")
#pp.pprint(response.json()['quad']['quads']['0'] )

#pp.pprint("Quad 1 Supplies:")
#pp.pprint(response.json()['quad']['quads']['1'] )

quadKeys = response.json()['quad']['quads']
for quad in range( len(quadKeys) ):         # Loop over Quads..
    for channel in range( len(quadKeys['0']['channels']) ):         # Loop over Quad's channels
        print("Quad{}, Channel{} is enabled? {}".format(quad, channel, quadKeys[str(quad)]['channels'][str(channel)]['enabled'] ))
    print("---------------")
