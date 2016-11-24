''' by ckd27546 - read out each temperature and humidity sensor's value, actual and in volts, ditto for its' setpoint;
                    Now also includes fan, pump, position values '''

import requests, json
import time

url = 'http://beagle03.aeg.lan:8888/api/0.1/lpdpower/'

response = requests.get(url)
pscu_status = response.json()

temp_sensors = len(pscu_status['temperature']['sensors'])
humid_sensors = len(pscu_status['humidity']['sensors'])

print("Continuous reading out: (Use Ctrl-C to close script)")
time.sleep(1)

try:
    while True:
        # Request PSCU sensors data and place into local var for temp, humidity
        response = requests.get(url)
        pscu_status = response.json()
        temp_data = pscu_status['temperature']['sensors']
        humid_data = pscu_status['humidity']['sensors']
        fan_data = pscu_status['fan']
        pump_data = pscu_status['pump']
        posn_data = pscu_status['position']
        # Print each "pair" of temp, humidity per line (but avoid humidity once beyond 2nd humidity sensor
        for index in range(temp_sensors):
            print "Temperature{0:>2}: {1:2.1f} C ({2:2.5} V) Setpoint: {3:2.6f} C ({4:2.6f} V)".format(index, temp_data[str(index)]['temperature'], temp_data[str(index)]['temperature_volts'], 
                                                                                               temp_data[str(index)]['setpoint'], temp_data[str(index)]['setpoint_volts']),
            if index < 2:
                print "   Humidity{0:>2}: {1:2.1f} % ({2:1.5f} V)) Setpoint: {3:2.6f} C ({4:2.6f} V)".format(index, humid_data[str(index)]['humidity'], humid_data[str(index)]['humidity_volts'], 
                                                                                                     humid_data[str(index)]['setpoint'], humid_data[str(index)]['setpoint_volts'])
            else:
                print ""
        # Adding fan, pump & position
        print "fan's currentspeed: {0:>2.1f} Hz ({1:2.1} V) Setpoint: {2:2.6f} Hz ({3:2.6f} V)".format(fan_data['currentspeed'], fan_data['currentspeed_volts'],
                                                                                                      fan_data['setpoint'], fan_data['setpoint_volts'])
        print "pump's currentspeed: {0:>2.1f} L/min ({1:2.1} V) Setpoint: {2:2.6f} L/min ({3:2.6f} V)".format(pump_data['flow'], pump_data['flow_volts'],
                                                                                                       pump_data['setpoint'], pump_data['setpoint_volts'])
        print "Position: {0:>2.4f} mm ({1:2.1} V)".format(posn_data['flow'], posn_data['flow_volts'])
        # Placeholder in case there is a setpoint_volts key too:
        #print "Position: {0:>2.4f} mm ({1:2.1} V) Setpoint: {2:2.6f} mm".format(posn_data['flow'], posn_data['flow_volts'])
        print "Pause 1 sec.."
        time.sleep(1)
except KeyboardInterrupt:
    print("\n")
print("\nAll Done")

