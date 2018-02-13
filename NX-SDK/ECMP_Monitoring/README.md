# Nexus 9K ECMP Monitoring and Streaming Telemetry integration with NX-SDK
##### Author: Nicolas Delecroix
##### Email: ndelecro@cisco.com

## Description:

This repository contains a NX-SDK application that monitors the load of an ECMP bundle.

Upon startup, it automatically detects an ECMP bundle. The load threshold can be configured via a custom CLI. When the load of a link member exceeds the threshold, the app displays a syslog and creates a streaming telemetry event.

## Usage:
Copy ecmp_monitoring.py to the switch.

Enable NX-SDK and Bash Shell in NX-OS, and configure Streaming Telemetry:
```
feature nxsdk
feature bash-shell
feature telemetry

telemetry
  destination-group 1
    ip address 10.60.0.96 port 5000 protocol HTTP encoding JSON
  sensor-group 1
    data-source NX-API
    path "show ecmp_monitoring tm-use-only" depth 0 query-condition show-output-format=json
  subscription 1
    dst-grp 1
    snsr-grp 1 sample-interval 10000
```

Install the app:
```
switch# run bash
bash-4.2$ sudo su
bash-4.2# nohup /isan/bin/python /bootflash/ecmp_monitoring &
``` 

Return to NX-OS and verify that the app is running:
```
bash-4.2# exit
bash-4.2$ exit
switch# show nxsdk internal service

NXSDK Started/Temp unavailabe/Max services : 1/0/32
NXSDK Default App Path         : /isan/bin/nxsdk
NXSDK Supported Versions       : 1.0 1.5

Service-name              Base App        Started(PID)      Version    RPM Package
------------------------- --------------- ----------------- ---------- ------------------------
/bootflash/ecmp_monitoring nxsdk_app1      BASH(24430)                  -
switch#
```

Configure the bandwidth threshold using the custom CLI:
```
switch# conf
Enter configuration commands, one per line. End with CNTL/Z.
switch(config)# ecmp_monitoring ?
  bw-threshold  Bandwidth threshold for monitoring

switch(config)# ecmp_monitoring bw-threshold ?
  <0-2147483647>  Bandwidth threshold value in Mbps

switch(config)# ecmp_monitoring bw-threshold 7500
switch(config)#
```




## References:
https://github.com/CiscoDevNet/NX-SDK

http://www.cisco.com/c/en/us/td/docs/switches/datacenter/nexus9000/sw/7-x/programmability/guide/b_Cisco_Nexus_9000_Series_NX-OS_Programmability_Guide_7x/b_Cisco_Nexus_9000_Series_NX-OS_Programmability_Guide_7x_chapter_011010.html
