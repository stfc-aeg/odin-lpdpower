''' ckd27546 - read out each temperature and humidity sensor's value, actual and in volts, ditto for its' setpoint '''

import requests, json, httplib
import time, sys, datetime

pscu_host='beagle03.aeg.lan'
if len(sys.argv) > 1:
    pscu_host=sys.argv[1]

url = 'http://{:s}:8888/api/0.1/lpdpower/'.format(pscu_host)
try:
    response = requests.get(url)
    if response.status_code != requests.codes.OK:
        print("Error: {}.".format(httplib.responses[response.status_code]))
        sys.exit(-1)
except Exception as e:
    print("Exception: {}".format(e))
    sys.exit(-1)
pscu_status = response.json()

temp_sensors = len(pscu_status['temperature']['sensors'])
humid_sensors = len(pscu_status['humidity']['sensors'])
temp_data = pscu_status['temperature']['sensors']
humid_data = pscu_status['humidity']['sensors']

print("Continuous reading out: (Use Ctrl-C to close script)")
time.sleep(1)

try:
    while True:
        # Request PSCU sensors data and place into local var for temp, humidity
        try:
            response = requests.get(url)
            if response.status_code != requests.codes.OK:
                print("Failure: {}".format(httplib.responses[response.status_code]))
                sys.exit(-1)
        except Exception as e:
            print("Exception: {}".format(e))
            sys.exit(-1)
        pscu_status = response.json()
        temp_data = pscu_status['temperature']['sensors']
        humid_data = pscu_status['humidity']['sensors']
        # Print each "pair" of temp, humidity per line (but avoid humidity once beyond 2nd humidity sensor
        for index in range(temp_sensors):
            print("Temperature{0:>2}: {1:>4.1f} C ({2:>6.5} V) Setpoint: {3:2.6f} C ({4:2.6f} V)".format(
                 index, temp_data[str(index)]['temperature'], temp_data[str(index)]['temperature_volts'], 
                 temp_data[str(index)]['setpoint'], temp_data[str(index)]['setpoint_volts']
                 )),
            if index < 2:
                print("   Humidity{0:>2}: {1:2.1f} % ({2:1.5f} V)) Setpoint: {3:2.6f} C ({4:2.6f} V)".format(
                     index, humid_data[str(index)]['humidity'], humid_data[str(index)]['humidity_volts'], 
                     humid_data[str(index)]['setpoint'], humid_data[str(index)]['setpoint_volts']
                     ))
            else:
                print("")
        # Construct and print current daytime
        ts = time.time()
        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print("{}{}".format(timeStamp, "\n"))
        time.sleep(1)
except KeyboardInterrupt:
    print("\n")
print("\nAll Done")

