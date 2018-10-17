import requests, json, sys

class CiscoNxosLibrary(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self.switch_list = []
        self.current_switch = {}

    def add_switch(self, host, user, pwd):
        self.switch_list.append(dict(host=host, user=user, pwd=pwd))

    def change_to_switch(self, host):
        for item in self.switch_list:
            if item["host"] == host:
                self.current_switch = item

    def run_cmds(self, commands):
        resp = self.post_clis(self.current_switch["host"],
                              self.current_switch["user"],
                              self.current_switch["pwd"],
                              ["show version"])
        return resp

    def post_payload(self, switch_IP, switch_user, switch_password, payload):
        myheaders = {'content-type':'application/json-rpc'}
        url = "http://%s/ins" % (switch_IP)
        requests.post(url, data = json.dumps(payload), headers = myheaders,
                      auth = (switch_user, switch_password)).json()

    def post_clis(self, switch_IP, switch_user, switch_password, clis):
        payload = []
        myheaders={'content-type':'application/json-rpc'}
        url = "http://%s/ins" % (switch_IP)

        for cli in clis:
            dict_entry = {"jsonrpc": "2.0","method": "cli","params": {"cmd": cli,"version": 1},"id": 1}
            payload.append(dict_entry)

        return requests.post(url, data = json.dumps(payload), headers = myheaders,
                             auth = (switch_user, switch_password)).json()
