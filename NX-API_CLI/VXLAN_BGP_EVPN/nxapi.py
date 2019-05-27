#! /usr/bin/python

import requests, json, sys, getpass

switch_password = ""

def get_switch_password():
    global switch_password
    switch_password = getpass.getpass()

def post_payload(switch_IP, switch_user, payload):
    myheaders = {'content-type':'application/json-rpc'}
    url = "https://%s/ins" % (switch_IP)
    requests.post(url, data = json.dumps(payload), headers = myheaders,
                  auth = (switch_user, switch_password), verify = False).json()

def post_clis(switch_IP, switch_user, clis, rollback = False):
    global switch_password
    payload = []
    myheaders={'content-type':'application/json-rpc'}
    url = "https://%s/ins" % (switch_IP)

    nxapi_id = 1
    for cli in clis:
        dict_entry = {
            "jsonrpc": "2.0",
            "method": "cli",
            "params": {
                "cmd": cli,
                "version": 1
            },
            "id": nxapi_id
        }
        if rollback:
            dict_entry["rollback"] = "rollback-on-error"
        payload.append(dict_entry)
        nxapi_id += 1

    print(json.dumps(payload, indent=4))
    response = requests.post(url, data = json.dumps(payload), headers = myheaders,
                             auth = (switch_user, switch_password),
                             verify = False).json()
    print(json.dumps(response, indent=4))
    print
    return response

