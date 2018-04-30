# Nexus 9K NX-SDK app for ECMP Monitoring and Streaming Telemetry integration
##### Author: Nicolas Delecroix
##### Email: ndelecro@cisco.com

## Description:

This repository contains a NX-SDK application that monitors the load of an ECMP bundle.

Upon startup, it automatically detects an ECMP bundle. The load threshold can be configured via a custom CLI. When the load of a link member exceeds the threshold, the app displays a syslog and creates a streaming telemetry event.

The app requires NX-OS version 7.0(3)I7(3) minimum.

A demo of the app can be found at https://youtu.be/IHSZ4hUmkvg.

## Usage:
Either generate the RPM yourself from ecmp_monitoring.py (steps at https://github.com/CiscoDevNet/NX-SDK) or use the pre-built RPM. Copy it to the switch and install it:
```
switch# install add bootflash:ecmp_monitoring-1.0-1.5.0.x86_64.rpm
[####################] 100%
Install operation 15 completed successfully at Mon Apr 30 15:51:07 2018

switch# 2018 Apr 30 15:51:07 switch %PATCH-INSTALLER-3-PATCH_INSTALLER_GENERIC_LOG_MSG: Install operation 15 completed successfully at Mon Apr 30 15:51:07 2018

switch# install activate ecmp_monitoring-1.0-1.5.0.x86_64
[####################] 100%
Install operation 19 completed successfully at Mon Apr 30 15:51:36 2018

2018 Apr 30 15:51:36 switch %PATCH-INSTALLER-3-PATCH_INSTALLER_GENERIC_LOG_MSG: Install operation 19 completed successfully at Mon Apr 30 15:51:36 2018

switch#
```

Enable NX-SDK and start the app:
```
switch# conf t
Enter configuration commands, one per line. End with CNTL/Z.
switch(config)# feature nxsdk
switch(config)# nxsdk service-name ecmp_monitoring
```

Verify that the app is running:
```
switch(config)# sh nxsdk internal service

NXSDK Started/Temp unavailabe/Max services : 1/0/32
NXSDK Default App Path         : /isan/bin/nxsdk
NXSDK Supported Versions       : 1.0 1.5

Service-name              Base App        Started(PID)      Version    RPM Package
------------------------- --------------- ----------------- ---------- ------------
------------
ecmp_monitoring           nxsdk_app1      VSH(4901)         1.5        ecmp_monitor
ing-1.0-1.5.0.x86_64
switch(config)#
```

If you want to use streaming telemetry, enable it via "feature telemetry", and configure it:
```
feature telemetry

telemetry
  destination-group 1
    ip address <my_telemetry_server_ip> port <my_telemetry_server_port> protocol HTTP encoding JSON
  sensor-group 1
    data-source NX-API
    path "show ecmp_monitoring.py tm-use-only" depth 0 query-condition show-output-format=json
  subscription 1
    dst-grp 1
    snsr-grp 1 sample-interval 10000
```

You can use the HTTP streaming telemetry collector provided on https://github.com/ndelecro/Nexus-9K-Programmability/tree/master/Streaming_Telemetry/HTTP_Transport. Start it on your telemetry server:
```
server# python http_receiver.py -vv -l 0
Starting httpd on port 5000...
verbose           = True
more verbose      = True
verbose print len = 0 (0 is unlimited)
```

Verify that the connection to the collector is successful:
```
switch# sh telemetry transport

Session Id      IP Address      Port       Encoding   Transport  Status
--------------------------------------------------------------------------------
0               10.60.0.96      5000       JSON       HTTP       Transmitting
switch#
```

Verify that you have at least one ECMP bundle. By default the app will look for bundles in the BGP AS 65000.
```
switch# sh ip route 192.168.2.0
IP Route Table for VRF "default"
'*' denotes best ucast next-hop
'**' denotes best mcast next-hop
'[x/y]' denotes [preference/metric]
'%<string>' in via output denotes VRF <string>

192.168.2.0/24, ubest/mbest: 2/0
    *via 10.0.1.1, [20/0], 1w5d, bgp-65000, external, tag 65001
    *via 10.0.1.5, [20/0], 1w5d, bgp-65000, external, tag 65001
switch#
```

Configure the bandwidth threshold using the custom CLI. In this example, 7.5GB:
```
switch# conf
Enter configuration commands, one per line. End with CNTL/Z.
switch(config)# ecmp_monitoring ?
  bw-threshold  Bandwidth threshold for monitoring

switch(config)# ecmp_monitoring bw-threshold ?
  <0-2147483647>  Bandwidth threshold value in Mbps

switch(config)# ecmp_monitoring bw-threshold 7500
```

When the actual bandwidth on a ECMP link member exceeds the threshold, a syslog will be displayed:
```
2018 Apr 30 15:57:17 switch %NXSDK-4-WARNING_MSG:  nxsdk_app1 [6718]  [ecmp_monitoring] High egress bandwidth: int=Eth1/49, bw=8000372920
```

A telemetry event will also be received by the collector:
```
server# python http_receiver.py -vv -l 0
Starting httpd on port 5000...
verbose           = True
more verbose      = True
verbose print len = 0 (0 is unlimited)

10.60.0.41 - - [30/Apr/2018 10:52:53] "POST /network/show%20ecmp_monitoring%20tm-use-only HTTP/1.0" 200 -
10.60.0.41 - - [30/Apr/2018 10:52:53] "POST /network/show%20ecmp_monitoring%20tm-use-only HTTP/1.0" 200 -
>>> URL            : /network/show%20ecmp_monitoring%20tm-use-only
>>> TM-HTTP-VER    : 1.0.0
>>> TM-HTTP-CNT    : 1
>>> Content-Type   : application/json
>>> Content-Length : 392
    Path => show ecmp_monitoring tm-use-only
            node_id_str   : switch
            collection_id : 231
            data_source   : NX-API
            data          : {
    "interface": "Ethernet1/49",
    "eth_outrate1_bits": "7999764864"
}
```

Check the app debug logs:
```
switch(config)# feature bash-shell
switch(config)# run bash
bash-4.2$ sudo su
bash-4.2# tail -f /tmp/ecmp_monitoring.log
2018-04-30 16:12:48 -- Starting event loop, CTRL-C to interrupt
2018-04-30 16:12:48 -- postL3RouteCb
2018-04-30 16:12:48 -- 192.168.2.0/24
2018-04-30 16:12:48 -- 192.168.2.0/24 is a ECMP route
2018-04-30 16:12:48 -- ----> while nextHop
2018-04-30 16:12:48 -- ----> 10.0.1.1,
2018-04-30 16:12:48 -- ----> p2pIntfName: Ethernet1/49
2018-04-30 16:12:48 -- ----> while nextHop
2018-04-30 16:12:48 -- ----> 10.0.1.5,
2018-04-30 16:12:48 -- ----> p2pIntfName: Ethernet1/50
2018-04-30 16:12:48 -- end postL3RouteCb
2018-04-30 16:12:51 -- tm-use
2018-04-30 16:12:51 -- get_telemetry_json()
2018-04-30 16:12:51 -- show interface Ethernet1/49
2018-04-30 16:12:52 -- show interface Ethernet1/50
2018-04-30 16:12:52 -- "{}"
2018-04-30 16:13:01 -- tm-use
2018-04-30 16:13:01 -- get_telemetry_json()
2018-04-30 16:13:01 -- show interface Ethernet1/49
2018-04-30 16:13:02 -- show interface Ethernet1/50
2018-04-30 16:13:02 -- "{}"
2018-04-30 16:13:02 -- set_bw_threshold_cmd
2018-04-30 16:13:02 -- 7500000000
2018-04-30 16:13:05 -- [ecmp_monitoring] High egress bandwidth: int=Ethernet1/49, bw=7999951696
2018-04-30 16:13:11 -- [ecmp_monitoring] High egress bandwidth: int=Ethernet1/49, bw=7999963328
2018-04-30 16:13:12 -- tm-use
2018-04-30 16:13:12 -- get_telemetry_json()
2018-04-30 16:13:12 -- show interface Ethernet1/49
2018-04-30 16:13:12 -- {"interface": "Ethernet1/49", "eth_outrate1_bits": "7999963328"}
```

If you want to modify the code without rebuilding nor reinstalling the RPM, stop the app, use the bash shell to copy the new source to /isan/bin/nxsdk/ecmp_monitoring, and start the app as shown earlier.

Stop the app:
```
switch(config)# no nxsdk service-name ecmp_monitoring
```

Remove the RPM:
```
switch# install deactivate ecmp_monitoring-1.0-1.5.0.x86_64
[####################] 100%
Install operation 24 completed successfully at Mon Apr 30 16:15:11 2018

switch# 2018 Apr 30 16:15:11 switch %PATCH-INSTALLER-3-PATCH_INSTALLER_GENERIC_LOG_MSG: Install operation 24 completed successfully at Mon Apr 30 16:15:11 2018

switch# install remove ecmp_monitoring-1.0-1.5.0.x86_64.rpm
Proceed with removing ecmp_monitoring-1.0-1.5.0.x86_64.rpm? (y/n)?  [n] y
[####################] 100%
Install operation 25 completed successfully at Mon Apr 30 16:15:27 2018

2018 Apr 30 16:15:27 switch %PATCH-INSTALLER-3-PATCH_INSTALLER_GENERIC_LOG_MSG: Install operation 25 completed successfully at Mon Apr 30 16:15:27 2018
switch#
```

## References:
https://github.com/CiscoDevNet/NX-SDK

http://www.cisco.com/c/en/us/td/docs/switches/datacenter/nexus9000/sw/7-x/programmability/guide/b_Cisco_Nexus_9000_Series_NX-OS_Programmability_Guide_7x/b_Cisco_Nexus_9000_Series_NX-OS_Programmability_Guide_7x_chapter_011010.html
