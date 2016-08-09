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


if __name__ == "__main__":

    thePSCU = PSCUAccess()
    print "key arm: ", thePSCU.getArm()
    print "key isarmed: ", thePSCU.getIsarmed()
    print "key enableall: ", thePSCU.getEnableall()
    #print "\nkey fan: ", thePSCU.getFan()
    
    # Toggle arm on
    thePSCU.setArm(False)
    time.sleep(0.2)
    # Need to manually poll BB for (updated) key values
    thePSCU.updateDict()
    print "key arm: ", thePSCU.getArm()
    print "key isarmed: ", thePSCU.getIsarmed()


    # Developments..

    # Quads
    dQuads = thePSCU.dict
    quads = dQuads['quad']['quads']
    channels = dQuads['quad']['quads']['0']['channels']
    for quad in range(len( quads)):
        print "QUAD NUMBER {}".format(quad)
        for channel in range(len( channels)):
            quads[str(quad)]['channels'][str(channel)]
            chCurrent     = quads[str(quad)]['channels'][str(channel)]['current']
            chEnable      = quads[str(quad)]['channels'][str(channel)]['enable']
            chFeedback    = quads[str(quad)]['channels'][str(channel)]['feedback']
            chFuseVoltage = quads[str(quad)]['channels'][str(channel)]['fusevoltage']
            chVoltage     = quads[str(quad)]['channels'][str(channel)]['voltage']
            print "Ch{}:  ".format(channel),
            print "{0:.f}A  ".format(chCurrent),
            print "Ena? {}  Fdbk? {}  Fuse: {}  ".format(chEnable,chFeedback, chFuseVoltage),
            print "Volt: {0:.3}V".format(chVoltage)
        print "-----------"

    
    # Humidity
##    dHumidity = thePSCU.getHumidity()
##    dHumidity['sensors'].keys() # => [u'1', u'0']
##    dHumidity['sensors']['0']   # => {u'disabled': 0, u'setpoint': 62.77198584890892, u'humidity': 46.02235371466141, u'trace': True, u'tripped': False}



    
