#! /usr/bin/python

import requests, json, sys

def post_payload(switch_IP, switch_user, switch_password, payload):
    myheaders = {'content-type':'application/json-rpc'}
    url = "http://%s/ins" % (switch_IP)
    requests.post(url, data = json.dumps(payload), headers = myheaders,
                  auth = (switch_user, switch_password)).json()

def post_clis(switch_IP, switch_user, switch_password, clis):
    payload = []
    myheaders={'content-type':'application/json-rpc'}
    url = "http://%s/ins" % (switch_IP)

    for cli in clis:
        print cli
        dict_entry = {"jsonrpc": "2.0","method": "cli","params": {"cmd": cli,"version": 1},"id": 1}
        payload.append(dict_entry)

    requests.post(url, data = json.dumps(payload), headers = myheaders,
                  auth = (switch_user, switch_password)).json()
    print

