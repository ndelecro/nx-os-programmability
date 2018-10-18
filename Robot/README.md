### Prerequisite
```
$ pip install robotframework
```

### Usage example: validation
```
root@3576a229c5c9:~/Robot/Cisco# cat validate_nxos.txt
*** Settings ***
Library	          CiscoNxosLibrary

Suite Setup  Add Switches

*** Test Cases ***
Check version
  Change To Switch    n9kv-3
  ${version}=  Run Cmd  show ver
  Log   ${version}
  Should Be Equal   ${version['result']['body']['kickstart_ver_str']}   9.2(1)

Check version wrong
  Change To Switch    9372-1
  ${version}=  Run Cmd  show ver
  Should Be Equal   ${version['result']['body']['kickstart_ver_str']}   9.2(1)

Check model type
  Change To Switch    n9kv-4
  ${mod}=  Run Cmd  show mod
  Should Be Equal   ${mod['result']['body']['TABLE_modinfo']['ROW_modinfo']['model']}   N9K-9000v

Ping
  Change To Switch    9372-1
  ${ping_output}=    Run Cmd   ping 10.0.9.0
  ${match}      ${packet_loss}=      Should Match Regexp     ${ping_output['result']['msg']}  (\\d+\\.\\d+)% packet loss
  Should Be Equal As Numbers   ${packet_loss}       0       msg="Packets lost percent not zero!!!"

Ping wrong
  Change To Switch    9372-1
  ${ping_output}=    Run Cmd   ping 10.0.9.42
  ${match}      ${packet_loss}=      Should Match Regexp     ${ping_output['result']['msg']}  (\\d+\\.\\d+)% packet loss
  # Log to console  ${match}
  Should Be Equal As Numbers   ${packet_loss}       0       msg="Packets lost percent not zero!!!"

*** Keywords ***
Add Switches
  Add Switch    host=9372-1    user=admin    pwd=cisco
  Add Switch    host=n9kv-3    user=admin    pwd=cisco
  Add Switch    host=n9kv-4    user=admin    pwd=cisco
root@3576a229c5c9:~/Robot/Cisco# pybot --pythonpath=CiscoLibrary validate_nxos.txt
==============================================================================
Validate Nxos
==============================================================================
Check version                                                         | PASS |
------------------------------------------------------------------------------
Check version wrong                                                   | FAIL |
7.0(3)I7(5) != 9.2(1)
------------------------------------------------------------------------------
Check model type                                                      | PASS |
------------------------------------------------------------------------------
Ping                                                                  | PASS |
------------------------------------------------------------------------------
Ping wrong                                                            | FAIL |
"Packets lost percent not zero!!!": 100.0 != 0.0
------------------------------------------------------------------------------
Validate Nxos                                                         | FAIL |
5 critical tests, 3 passed, 2 failed
5 tests total, 3 passed, 2 failed
==============================================================================
Output:  /root/Robot/Cisco/output.xml
Log:     /root/Robot/Cisco/log.html
Report:  /root/Robot/Cisco/report.html
root@3576a229c5c9:~/Robot/Cisco#
```

### Usage example: configuration
```
root@3576a229c5c9:~/Robot/Cisco# cat configure_nxos.txt
*** Settings ***
Library	          CiscoNxosLibrary

Suite Setup  Add Switches

*** Test Cases ***
Add a VLAN
  Change To All Switches
  @{cmds}=    Create List    vlan 42    name vlan-42
  Configure   ${cmds}

Ping before interface configuration
  Change To Switch    9372-1
  ${ping_output}=    Run Cmd   ping 10.0.9.0
  ${match}      ${packet_loss}=      Should Match Regexp     ${ping_output['result']['msg']}  (\\d+\\.\\d+)% packet loss
  Should Be Equal As Numbers   ${packet_loss}       0       msg="Packets lost percent not zero!!!"

Configure IP on interface
  @{cmds}=    Create List    int e1/49  ip address 10.0.9.1/31
  Configure   ${cmds}
  sleep       5

Ping after interface configuration
  ${ping_output}=    Run Cmd   ping 10.0.9.0
  ${match}      ${packet_loss}=      Should Match Regexp     ${ping_output['result']['msg']}  (\\d+\\.\\d+)% packet loss
  # Log to console  ${match}
  Should Be Equal As Numbers   ${packet_loss}       0       msg="Packets lost percent not zero!!!"

*** Keywords ***
Add Switches
  Add Switch    host=9372-1    user=admin    pwd=cisco
  Add Switch    host=n9kv-3    user=admin    pwd=cisco
  Add Switch    host=n9kv-4    user=admin    pwd=cisco
root@3576a229c5c9:~/Robot/Cisco#
root@3576a229c5c9:~/Robot/Cisco# pybot --pythonpath=CiscoLibrary configure_nxos.txt
==============================================================================
Configure Nxos
==============================================================================
Add a VLAN                                                            | PASS |
------------------------------------------------------------------------------
Ping before interface configuration                                   | FAIL |
"Packets lost percent not zero!!!": 100.0 != 0.0
------------------------------------------------------------------------------
Configure IP on interface                                             | PASS |
------------------------------------------------------------------------------
Ping after interface configuration                                    | PASS |
------------------------------------------------------------------------------
Configure Nxos                                                        | FAIL |
4 critical tests, 3 passed, 1 failed
4 tests total, 3 passed, 1 failed
==============================================================================
Output:  /root/Robot/Cisco/output.xml
Log:     /root/Robot/Cisco/log.html
Report:  /root/Robot/Cisco/report.html
root@3576a229c5c9:~/Robot/Cisco#
```
