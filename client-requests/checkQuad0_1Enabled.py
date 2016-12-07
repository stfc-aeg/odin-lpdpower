''' Check if each quad's channel is enabled (or not) '''
import requests
import sys

pscu_host = "beagle03.aeg.lan"
if len(sys.argv) > 1:
    pscu_host = sys.argv[1]
url = 'http://{:s}:8888/api/0.1/lpdpower/'.format(pscu_host)
try:
    response = requests.get(url)
    if response.status_code != requests.codes.OK:
        print("Error: {}".format(requests.status_codes._codes[response.status_code][0]))
        sys.exit(-1)
    
    quadKeys = response.json()['quad']['quads']
    for quad in range( len(quadKeys) ):         # Loop over Quads..
        for channel in range( len(quadKeys['0']['channels']) ):         # Loop over Quad's channels
            print("Quad{}, Channel{} is enabled? {}".format(quad, channel, quadKeys[str(quad)]['channels'][str(channel)]['enabled'] ))
        print("---------------")
except Exception as e:
    print("Exception: {}".format(e))
