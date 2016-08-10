import requests, sys, time, json


class PSCUAccess(object):
    def __init__(self):
        #self.quad = quad
        self.url = 'http://beagle03.aeg.lan:8888/api/0.1/lpdpower/'
	self.response = requests.get(self.url)
        self.dict     = self.response.json()
        # Headers don't change
        self.headers = {'Content-Type' : 'application/json'}

    def updateDict(self):
	self.response = requests.get(self.url)
        self.dict     = self.response.json()

    def getArm(self):
        return self.dict['arm']

    def getIsarmed(self):
        return self.dict['isarmed']

    def getEnableall(self):
        return self.dict['enableall']

    def getFan(self):
        return self.dict['fan']

    def getHumidity(self):
        return self.dict['humidity']


    def setArm(self, bToggle):
        payload = {"arm": bToggle}
        rep = requests.put(self.url, data=json.dumps(payload), headers=self.headers)
        if rep.status_code != 200:
            print "Error: %d Couldn't updated key 'arm'!" % rep.status_code
        # Allow (I2C) hardware read updated value before confirming 'arm' updated
        time.sleep(0.1)
        # Check new values of arm, isarmed keys
        r = requests.get(self.url)
        if r.status_code != 200:
            print "Error: %d Couldn't confirm updated key value!" % r.status_code

    def setQuadChannel(self, quad, channel, bEnable):
        payload = {"enable": bEnable}
        path = 'quad/quads/{}/channels/{}/enable'.format(quad, channel)
        # DEBUG:
        rp = requests.get( self.url + path)
        print "DEBUG, before: {} receiving: {}".format(rp.status_code, rp.text)
        rep = requests.put( self.url + path, data=json.dumps(payload), headers=self.headers)

        if rep.status_code != 200:
            print "error:  {} Couldn't change quad{}'s channel {}".format(rep.status_code, quad, channel)
        else:
            print "Success {}  changed quad{}'s channel {}".format(rep.status_code, quad, channel)

        # Check whether change worked.. #;
        rp = requests.get( self.url + path)
        if rp.status_code != 200:
            print "error:  {} Couldn't confirm quad channel set".format(rp.status_code)

    def getKey(self, path, aKey):
        rp = requests.get(path)
##        print "Going to access path: \n\t'{}'".format(path)
        # Check key value
        rp = requests.get(path)
        if rp.status_code != 200:
            print "Error {}: getKey() failed on key '{}'".format(rp.status_code, aKey)
##        else:
##            print "Successfully read key: '{}' and has value: '{}' ".format(aKey, rp.json()[aKey])
        return rp.json()[aKey]


if __name__ == "__main__":

    thePSCU = PSCUAccess()

    print "________________________________________________________________"
    print "Replicating \"Overall Health\", i.e. left-hand side of the webpage"

    print "Overall Health: ", thePSCU.getKey(thePSCU.url, 'overall')
    print "Trace Status: {}, Latched: {}".format(thePSCU.getKey(thePSCU.url+'trace/overall', 'overall'),
                                                thePSCU.getKey(thePSCU.url+'trace/overall', 'overall'))
    print "key enableall: ", thePSCU.getEnableall()
    print "key isarmed: ", thePSCU.getIsarmed()

    print "________________________________________________________________"
    
    # Toggle arm on
##    thePSCU.setArm(False)
##    thePSCU.setArm(True)
##    time.sleep(0.2)
##    # Need to manually poll BB for (updated) key values
##    thePSCU.updateDict()
##    print "key arm: ", thePSCU.getArm()
##    print "key isarmed: ", thePSCU.getIsarmed()

    # Developments..

    # Quads - Displays all key/value pairs, that needs wrapping in proper function call(s)
##    dQuads = thePSCU.dict
##    quads = dQuads['quad']['quads']
##    channels = dQuads['quad']['quads']['0']['channels']
##    for quad in range(len( quads)):
##        print "QUAD NUMBER {}".format(quad)
##        for channel in range(len( channels)):
##            quads[str(quad)]['channels'][str(channel)]
##            chCurrent     = quads[str(quad)]['channels'][str(channel)]['current']
##            chEnable      = quads[str(quad)]['channels'][str(channel)]['enable']
##            chFeedback    = quads[str(quad)]['channels'][str(channel)]['feedback']
##            chFuseVoltage = quads[str(quad)]['channels'][str(channel)]['fusevoltage']
##            chVoltage     = quads[str(quad)]['channels'][str(channel)]['voltage']
##            print "Ch{}:  ".format(channel),
##            print "{0:.3f}A  ".format(chCurrent),
##            print "Ena? {}  Fdbk? {}  Fuse: {}  ".format(chEnable,chFeedback, chFuseVoltage),
##            print "Volt: {0:.3}V".format(chVoltage)
##        print "-----------"

    print "________________________________________________________________"

##    # Enable/Disabled a quad channel:
##    bEnable = False
##    quad = 0
##    channel = 3
##    thePSCU.setQuadChannel(quad, channel, bEnable)

    # Temperature:
    
    temps = thePSCU.dict['temperature']['sensors']
    channels = len(temps)
    for channel in range(channels):
        temps[str(channel)]
        chDisabled    = temps[str(channel)]['disabled']
        chSetpoint    = temps[str(channel)]['setpoint']
        chTemp        = temps[str(channel)]['temperature']
        chTrace       = temps[str(channel)]['trace']
        chTripped     = temps[str(channel)]['tripped']
        print "Ch{}:  ".format(channel),
        print "{0:.1f}C  ".format(chTemp),
        print "Setpoint {0:.3}  ".format(chSetpoint),
        print "Trace? {}  Enable? {}  ".format(chTrace, chDisabled),
        print "Tripped: {} ".format(chTripped)
    print "-----------"

    # Humidity
##    dHumidity = thePSCU.getHumidity()
##    dHumidity['sensors'].keys() # => [u'1', u'0']
##    dHumidity['sensors']['0']   # => {u'disabled': 0, u'setpoint': 62.77198584890892, u'humidity': 46.02235371466141, u'trace': True, u'tripped': False}

    #print "\nkey fan: ", thePSCU.getFan()
