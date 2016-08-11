#!~/develop/projects/odin/venv/bin/python

''' Display all device information in as similar a fashion as the webpage, as possible '''

from pscu_access import PSCUAccess
thePSCU = PSCUAccess()

if __name__ == "__main__":

    thePSCU = PSCUAccess()

    print "________________________________________________________________"
    print "Replicating \"Overall Health\", i.e. left-hand side of the webpage"

    print "Overall Health: ", thePSCU.getKey(thePSCU.url, 'overall')
    print "Trace Status: {}, Latched: {}".format(thePSCU.getKey(thePSCU.url+'trace/overall', 'overall'),
                                                thePSCU.getKey(thePSCU.url+'trace/latched', 'latched'))
    print "key enableall: ", thePSCU.getEnableall()
    print "key isarmed: ", thePSCU.getIsarmed()

    print "________________________________________________________________"
    

    # Developments..

    # Quads - Displays all key/value pairs, that needs wrapping in proper function call(s)
    dQuads = thePSCU.dict
    quads = dQuads['quad']['quads']
    channels = dQuads['quad']['quads']['0']['channels']
    print "Quads:"
    for quad in range(len( quads)):
        print "------"
        print "Quad {}".format(quad)
        for channel in range(len( channels)):
            quads[str(quad)]['channels'][str(channel)]
            chCurrent     = quads[str(quad)]['channels'][str(channel)]['current']
            chEnable      = quads[str(quad)]['channels'][str(channel)]['enable']
            chFeedback    = quads[str(quad)]['channels'][str(channel)]['feedback']
            chFuseVoltage = quads[str(quad)]['channels'][str(channel)]['fusevoltage']
            chVoltage     = quads[str(quad)]['channels'][str(channel)]['voltage']
            print "Channel{}:  ".format(channel),
            print "{0:.3f}A  ".format(chCurrent),
            print "Ena? {}  Fdbk? {}  Fuse: {}  ".format(chEnable,chFeedback, chFuseVoltage),
            print "Volt: {0:.3}V".format(chVoltage)
    print "________________________________________________________________"


    # Temperature:
    
    dTemperature = thePSCU.dict['temperature']
    channels = len(dTemperature['sensors'])
    print "Temperature:"
    print "Status: {}  Latched: {}  ".format(dTemperature['overall'], dTemperature['latched'])
    for channel in range(channels):
        chInfo        = dTemperature['sensors'][str(channel)]
        print "Temp{0:>2}:  ".format(channel),
        print "{0:>6.1f}C  Setpoint {1:>6.1f}C  ".format(chInfo['temperature'], chInfo['setpoint']),
        print "Trace? {}  Enable? {:<1}  Tripped: {} ".format(chInfo['trace'], chInfo['disabled'],
                                                           chInfo['tripped'])
    print "________________________________________________________________"

    # Humidity
    
    dHumidity = thePSCU.getHumidity()
    #Above is equivalent to:
    #thePSCU.getKey('http://beagle03.aeg.lan:8888/api/0.1/lpdpower/humidity', 'humidity')
    
    #dHumidity['sensors'].keys() # => [u'1', u'0']
    #dHumidity['sensors']['0']   # => {u'disabled': 0, u'setpoint': 62.77198584890892, u'humidity': 46.02235371466141, u'trace': True, u'tripped': False}
    print "Humidity:"
    print "Status: {}  Latched: {}  ".format(dHumidity['overall'], dHumidity['latched'])
    channels = len(dHumidity['sensors'])
    for channel in range(channels):
        chInfo        = dHumidity['sensors'][str(channel)]
        print "Humidity{0:>2}:  ".format(channel),
        print "{0:>6.1f}%  Setpoint {1:>6.1f}%  ".format(chInfo['humidity'], chInfo['setpoint']),
        print "Trace? {}  Enable? {:<1}  Tripped: {} ".format(chInfo['trace'], chInfo['disabled'],
                                                           chInfo['tripped'])
    print "________________________________________________________________"

    # Pump
    print "Pump info:"

    chPump = thePSCU.getKey(thePSCU.url, 'pump')
    print "Pump1 Status: {}  Latched: {}  ".format(chPump['overall'], chPump['latched'])
    print "{0:>2.1f}l/min  Setpoint {1:>2.1f}l/min  ".format(chPump['flow'], chPump['setpoint']),
    print "Tripped: {} ".format(chPump['tripped'])
    
    print "________________________________________________________________"
    

    
    # Fan
    print "Fan info:"

    chFan = thePSCU.getFan()
    print "Fan1 Status: {}  Latched: {}  ".format(chFan['overall'], chFan['latched'])
    print "{0:>2.1f}Hz  Setpoint {1:>2.1f}Hz  ".format(chFan['currentspeed'], chFan['setpoint']),
    print "Potentiometer: {0:>2.1f}%  ".format(chFan['potentiometer']),
    print "Tripped: {}      (target: {})".format(chFan['tripped'], chFan['target'])
    
    print "________________________________________________________________"


    
