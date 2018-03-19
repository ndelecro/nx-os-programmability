# Nexus 9K NX-SDK app for FEX Pre-Provisioning
##### Author: Nicolas Delecroix
##### Email: ndelecro@cisco.com

## Description:

<a href=https://www.cisco.com/c/en/us/td/docs/switches/datacenter/nexus5000/sw/system_management/502_n1_1/b_Cisco_n5k_system_mgmt_cg_rel_502_n1_1/Cisco_n5k_system_mgmt_cg_rel_502_n1_1_chapter4.html>FEX Pre-Provisioning</a> is not currently available as a native NX-OS feature on Nexus 9K. In the following example, the FEX is defined in NX-OS, but we cannot pre-configure the FEX HIFs:
```
switch# sh run fex
fex 101
  pinning max-links 1
  description “FEX0101"
 
switch# sh run int e101/1/1
                              ^
Invalid range at '^' marker.
switch#
```

This NX-SDK app provides an alternative way of achieving FEX Pre-Provisioning on Nexus 9K.

The app detects when a FEX comes online, and automatically pushes the FEX HIF configuration to NX-OS. This configuration is stored on a file called fex-FEX_ID-config, where FEX_ID is replaced by the actual FEX ID.

The app requires NX-OS version 7.0(3)I7(3) minimum.

## Usage:
Create the necessary fex-FEX_ID_config files that store your FEX HIF configs. For example:
```
$ cat fex-101-config

interface Ethernet101/1/1
switchport
switchport mode access
switchport access vlan 42
no shut

interface Ethernet101/1/2
switchport
switchport mode access
switchport access vlan 42
no shut
$
```

Copy fex_pre_provisioning.py and the fex-FEX_ID_config files to the switch.

Enable NX-SDK and Bash Shell in NX-OS:
```
feature nxsdk
feature bash-shell
```

Install the app. Here the app and FEX config files are in the directory fex_pre_provisioning in the bootflash.
```
switch# run bash
bash-4.2$ sudo su
bash-4.2# nohup /isan/bin/python /bootflash/fex_pre_provisioning/fex_pre_provisioning.py &
```

Return to NX-OS. It should indicate that the app is running:
```
bash-4.2# exit
bash-4.2$ exit
switch# sh nxsdk internal service
 
NXSDK Started/Temp unavailabe/Max services : 1/0/32
NXSDK Default App Path         : /isan/bin/nxsdk
NXSDK Supported Versions       : 1.0 1.5
 
Service-name              Base App        Started(PID)      Version    RPM Package
------------------------- --------------- ----------------- ---------- ------------------------
/bootflash/fex_pre_provisioning/fex_pre_provisioning.py nxsdk_app1      BASH(Deleting)               -
switch#
```

Let's now connect the FEX. It initially appears as offline and proceeds to boot up:
```
switch# sh fex
  FEX         FEX           FEX                       FEX
Number    Description      State            Model            Serial
------------------------------------------------------------------------
101        FEX0101               Offline     N2K-C2248TP-1GE   SSI16060JSH
switch#
```

The FEX becomes online. The NX-SDK app detects it and auto-configures the FEX HIFs:
```
2018 Mar  2 17:06:01 switch %PLATFORM-5-MOD_STATUS: Fex 101 current-status is MOD_STATUS_ONLINE/OK
2018 Mar  2 17:06:06 switch %NXSDK-5-NOTICE_MSG:   [1587]  Configured FEX 101 with config file fex-101-config
```

The FEX HIFs have been automatically configured, similarly to what the native NX-OS feature would have done:
```
switch# sh run int e101/1/1-2
 
!Command: show running-config interface Ethernet101/1/1-2
!Time: Fri Mar  2 17:06:40 2018
 
version 7.0(3)I7(3)
 
interface Ethernet101/1/1
  switchport access vlan 42
  no shutdown
 
interface Ethernet101/1/2
  switchport access vlan 42
  no shutdown
 
switch#
```

If you need to stop the app:
```
switch# fex_pre_provisioning.py stop-event-loop
```

## References:
https://github.com/CiscoDevNet/NX-SDK

http://www.cisco.com/c/en/us/td/docs/switches/datacenter/nexus9000/sw/7-x/programmability/guide/b_Cisco_Nexus_9000_Series_NX-OS_Programmability_Guide_7x/b_Cisco_Nexus_9000_Series_NX-OS_Programmability_Guide_7x_chapter_011010.html
