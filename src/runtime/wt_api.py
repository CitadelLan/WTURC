# Access to http://localhost:8111 APIs

import requests

# Get information from /state
def get_wt_state():
    rsp = requests.get("localhost:8111/state")
    if rsp.status_code == 200:
        data = rsp.json()
        return data
    else:
        print("Get /state error: " + str(rsp.status_code))
        return None

# Get information from /hudmsg
def get_wt_hudmsg():
    rsp = requests.get("http://localhost:8111/hudmsg?lastEvt=0&lastDmg=0")
    if rsp.status_code == 200:
        data = rsp.json()
        return data
    else:
        print("Get /hudmsg error: " + str(rsp.status_code))
        return None

def get_wt_map_info():
    rsp = requests.get("http://localhost:8111/map_info.json")
    if rsp.status_code == 200:
        data = rsp.json()
        return data
    else:
        print("Get /mapinfo error: " + str(rsp.status_code))
        return None

def get_wt_indicators():
    rsp = requests.get("http://localhost:8111/indicators")
    if rsp.status_code == 200:
        data = rsp.json()
        return data
    else:
        print("Get /indicator error: " + str(rsp.status_code))
        return None