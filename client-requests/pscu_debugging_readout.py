''' ckd27546 - read out each temperature and humidity sensor's value, actual and in volts, ditto for its' setpoint;
               Now also includes fan, pump, position values; Added timestamp to differentiate between each iteration '''

import requests, json
import time, datetime
import sys

pscu_host='beagle03.aeg.lan'
if len(sys.argv) > 1:
    pscu_host=sys.argv[1]

url = 'http://{:s}:8888/api/0.1/lpdpower/'.format(pscu_host)
try:
    response = requests.get(url)
    if response.status_code != requests.codes.OK:
        print("Error: {}.".format(requests.status_codes._codes[response.status_code][0]))
        sys.exit(-1)
except Exception as e:
    print("Exception: {}".format(e))
    sys.exit(-1)
pscu_status = response.json()

temp_sensors = len(pscu_status['temperature']['sensors'])
humid_sensors = len(pscu_status['humidity']['sensors'])

print("Continuous reading out: (Use Ctrl-C to close script)")
time.sleep(1)

try:
    while True:
        # Request PSCU sensors data and place into local var for temp, humidity
        try:
            response = requests.get(url)
            if response.status_code != requests.codes.OK:
                print("Failure: {}".format(requests.status_codes._codes[response.status_code][0]))
                sys.exit(-1)
        except Exception as e:
            print("Exception: {}".format(e))
            sys.exit(-1)
        pscu_status = response.json()
        temp_data   = pscu_status['temperature']['sensors']
        humid_data  = pscu_status['humidity']['sensors']
        fan_data    = pscu_status['fan']
        pump_data   = pscu_status['pump']
        posn_data   = pscu_status['position']
        # Print each "pair" of temp, humidity per line (but avoid humidity once beyond 2nd humidity sensor
        for index in range(temp_sensors):
            print("Temperature {0:>2}: {1:6.1f} C  ({2:6.4f} V) Setpoint: {3:6.1f} C  ({4:6.4f} V)".format(
                index, temp_data[str(index)]['temperature'], temp_data[str(index)]['temperature_volts'], 
                       temp_data[str(index)]['setpoint'], temp_data[str(index)]['setpoint_volts']
                )),
            if index < 2:
                print("   Humidity{0:>2}: {1:6.1f} % ({2:6.4f} V)) Setpoint: {3:2.1f} C ({4:6.4f} V)".format(
                    index, humid_data[str(index)]['humidity'], humid_data[str(index)]['humidity_volts'], 
                           humid_data[str(index)]['setpoint'], humid_data[str(index)]['setpoint_volts']
                ))
            else:
                print("")

        # Adding fan, pump & position
        print("Fan speed     : {0:>6.1f} Hz ({1:6.4f} V) Setpoint: {2:6.1f} Hz ({3:6.4f} V)".format(
            fan_data['currentspeed'], fan_data['currentspeed_volts'],
            fan_data['setpoint'], fan_data['setpoint_volts']
        ))
        print("Pump flow     : {0:>6.1f} L  ({1:6.4f} V) Setpoint: {2:6.1f} L  ({3:6.4f} V)".format(
            pump_data['flow'], pump_data['flow_volts'],
            pump_data['setpoint'], pump_data['setpoint_volts']
        ))
        print("Position      : {0:>6.1f} mm ({1:6.4f} V)".format(
             pscu_status['position'], pscu_status['position_volts']))

        # Construct and print current daytime
        ts = time.time()
        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print("{}{}".format(timeStamp, "\n"))
        time.sleep(1)

except KeyboardInterrupt:
    print("\n")
print("\nAll Done")
