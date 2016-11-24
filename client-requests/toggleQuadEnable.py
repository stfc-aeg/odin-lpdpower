import sys, requests, json, pprint, time

def toggleQuadEnable(quad, channel):
    
    base_url = 'http://beagle04.aeg.lan:8888/api/0.1/lpdpower/'
    
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
    
    if len(sys.argv) > 1:
        quad = int(sys.argv[1])
        
    if len(sys.argv) > 2:
        channel = int(sys.argv[2])
        
    toggleQuadEnable(quad, channel)
