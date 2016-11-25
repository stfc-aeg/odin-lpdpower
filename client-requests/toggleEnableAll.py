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
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Requesting global enable state failed with status_code {} : {}".format(
            response.status_code, response.json()))
        return
    
    
    enabled = response.json()[enable_path]
    print("Current {} state is {}".format(enable_path, enabled))
    payload = {enable_path: not enabled}

    response = requests.put(base_url, data=json.dumps(payload), headers=headers)
    
    if response.status_code != 200:
        print("Setting global enable state to {} failed with status_code {} : {}".format(
            not enabled, response.status_code, response.json()))
        return
    
    print("{}'s state is now {}".format(enable_path, response.json()[enable_path]))
    
if __name__ == '__main__':
    toggleEnableAll()
