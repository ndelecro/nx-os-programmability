import requests, json, sys

class CiscoNxosLibrary(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self.switch_list = []
        self.current_switch = {}
        self.all_switches = False

    def add_switch(self, host, user, pwd):
        self.switch_list.append(dict(host=host, user=user, pwd=pwd))

    def change_to_switch(self, host):
        self.all_switches = False
        for item in self.switch_list:
            if item["host"] == host:
                self.current_switch = item

    # only relevant for configuration
    def change_to_all_switches(self):
        self.all_switches = True

    def run_cmd(self, command):
        if (self.all_switches):
            return "error: all switches option configured"
        resp = self.post_clis(self.current_switch["host"],
                              self.current_switch["user"],
                              self.current_switch["pwd"],
                              [str(command)])
        return resp

    def configure(self, commands):
        if (self.all_switches):
            config_list = self.switch_list
        else:
            # make a list with only the current switch
            config_list = [self.current_switch]
        for switch in config_list:
            resp = self.post_clis(switch["host"],
                                  switch["user"],
                                  switch["pwd"],
                                  commands)
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
