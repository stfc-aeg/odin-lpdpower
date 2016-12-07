''' Toggle key 'allEnabled' to the opposite of its current value '''
from __future__ import print_function
import requests, json, sys

def toggleEnableAll():
    
    pscu_host = "beagle03.aeg.lan"
    if len(sys.argv) > 1:
        pscu_host = sys.argv[1]

    base_url = 'http://{:s}:8888/api/0.1/lpdpower/'.format(pscu_host)
    enable_path = 'allEnabled'
    headers = {'Content-Type': 'application/json'}

    url = base_url + enable_path
    try:
        response = requests.get(url)
    except Exception as e:
        print("Exception: {} on get() call".format(e))
        return

    if response.status_code != requests.codes.OK:
        print("Requesting global enable state failed ({}) {}".format(
            response.status_code, requests.status_codes._codes[response.status_code][0]))
        return

    enabled = response.json()[enable_path]
    print("Current {} state is {}".format(enable_path, enabled))
    payload = {enable_path: not enabled}

    try:
        response = requests.put(base_url, data=json.dumps(payload), headers=headers)
    except Exception as e:
        print("Exception: {} on put() call".format(e))
        return

    if response.status_code != requests.codes.OK:
        print("Setting global enable state to {} failed ({}) {}".format(not enabled,
            response.status_code, requests.status_codes._codes[response.status_code][0]))
        return
    
    print("{}'s state is now {}".format(enable_path, response.json()[enable_path]))
    
if __name__ == '__main__':
    toggleEnableAll()
