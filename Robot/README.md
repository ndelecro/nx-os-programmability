### Prerequisite
```
$ pip install robotframework
```

### Usage example
```
root@3576a229c5c9:~/Robot/Cisco# cat validate_nxos.txt
*** Settings ***
Library
    CiscoNxosLibrary

Suite Setup  Add Switches

*** Test Cases ***
Check version
  Change To Switch    n9kv-3
  ${version}=  Run Cmds  show ver
  Log   ${version}
  Should Be Equal   ${version['result']['body']['kickstart_ver_str']}   9.2(1)

Check version wrong
  Change To Switch    9372-1
  ${version}=  Run Cmds  show ver
  Log   ${version}
  Should Be Equal   ${version['result']['body']['kickstart_ver_str']}   9.2(1)

*** Keywords ***
Add Switches
  Add Switch    host=9372-1    user=admin    pwd=cisco
  Add Switch    host=n9kv-3    user=admin    pwd=cisco
  Add Switch    host=n9kv-4    user=admin    pwd=cisco
root@3576a229c5c9:~/Robot/Cisco#
root@3576a229c5c9:~/Robot/Cisco#
root@3576a229c5c9:~/Robot/Cisco# pybot --pythonpath=CiscoLibrary validate_nxos.txt
==============================================================================
Validate Nxos
==============================================================================
Check version                                                         | PASS |
------------------------------------------------------------------------------
Check version wrong                                                   | FAIL |
7.0(3)I7(5) != 9.2(1)
------------------------------------------------------------------------------
Validate Nxos                                                         | FAIL |
2 critical tests, 1 passed, 1 failed
2 tests total, 1 passed, 1 failed
==============================================================================
Output:  /root/Robot/Cisco/output.xml
Log:     /root/Robot/Cisco/log.html
Report:  /root/Robot/Cisco/report.html
root@3576a229c5c9:~/Robot/Cisco#
```
