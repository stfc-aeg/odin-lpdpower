import sys, requests, json, pprint, time

def toggleQuadEnable(base_url, quad, channel):
    
    path = 'quad/quads/{}/channels/{}'.format(quad, channel)
    url = base_url + path    
    headers  = {'Content-Type' : 'application/json'}

    pp = pprint.PrettyPrinter()
    
    # Get the appropriate quad channel status
    response = requests.get(url)
    chan_status   = response.json()[str(channel)]
    print "Quad {} channel {} status before toggling enable: {}".format(quad, channel, chan_status['enabled'])
    #pp.pprint(chan_status)
    chan_enable = chan_status['enabled']
    
    # Toggle the enable state
    payload = {"enabled": not chan_enable}
    rep = requests.put(url, data=json.dumps(payload), headers=headers)
  
    if rep.status_code != 200:
        print "error:  {} Couldn't change quad {} channel {}".format(rep.status_code, quad, channel)
    else:
        print "Success (Code:{}) changed quad {} channel {} to: {}".format(rep.status_code, quad, channel, payload['enabled'])
  
    time.sleep(0.5)
    # Get the status again
    response = requests.get(url)
    chan_status = response.json()[str(channel)]

    print "Quad {} channel {} status after toggling enable: {}".format(quad, channel, chan_status['enabled'])
    #pp.pprint(chan_status)

if __name__ == "__main__":
    
    quad = 0
    channel = 0

    if len(sys.argv) != 4:
        print "Format: python test.py <address> <Quad> <Channel>"
        print "Example Usage: python toggleQuadEnable.py beagle03.aeg.lan 0 3"
    else:

        quad = int(sys.argv[2])
        channel = int(sys.argv[3])
        if quad > 3:
            print "Quad must be integer value between 0-3"
            sys.exit(-1)
        if channel > 3:
            print "Channel must be integer value between 0-3"
            sys.exit(-1)

        pscu_host = "beagle03.aeg.lan"
        if len(sys.argv) > 1:
            pscu_host = sys.argv[1]
        
        base_url = 'http://{:s}:8888/api/0.1/lpdpower/'.format(pscu_host)

        toggleQuadEnable(base_url, quad, channel)
