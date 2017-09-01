#! /usr/bin/python

import os
import json

cli = "sh ver | json"
f = os.popen("dohost \"sh ver | json\"")
ver = f.read()

ver_dict = json.loads(ver)

print
print type(ver_dict)

print ver_dict["kern_uptm_secs"]

#print json.dumps(ver_dict, indent=4)

f = os.popen("dohost \"sh int status | json\"")
s = f.read()
int_status = json.loads(s)
print json.dumps(int_status, indent=4)
for int in int_status["TABLE_interface"]["ROW_interface"]:
    print "%s\t" % (int["interface"]),
    if "name" in int:
    print "%s\t" % (int["name"]),
else:
      print "--\t",
    print int["state"]
