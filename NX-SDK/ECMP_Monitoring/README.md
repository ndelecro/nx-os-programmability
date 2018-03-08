# Nexus 9K NX-SDK app for ECMP Monitoring and Streaming Telemetry integration
##### Author: Nicolas Delecroix
##### Email: ndelecro@cisco.com

## Description:

This repository contains a NX-SDK application that monitors the load of an ECMP bundle.

Upon startup, it automatically detects an ECMP bundle. The load threshold can be configured via a custom CLI. When the load of a link member exceeds the threshold, the app displays a syslog and creates a streaming telemetry event.

The app requires NX-OS version 7.0(3)I7(3) minimum.

A demo of the app can be found at https://youtu.be/IHSZ4hUmkvg.

## Usage:
Copy ecmp_monitoring.py to the switch.

Enable NX-SDK and Bash Shell in NX-OS:
```
feature nxsdk
feature bash-shell
```

If you want to use streaming telemetry, enable it and configure it:
```
feature telemetry

telemetry
  destination-group 1
    ip address 10.60.0.96 port 5000 protocol HTTP encoding JSON
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

Verify that you have at least one ECMP bundle:
```
switch# show ip route 192.168.1.0
IP Route Table for VRF "default"
'*' denotes best ucast next-hop
'**' denotes best mcast next-hop
'[x/y]' denotes [preference/metric]
'%<string>' in via output denotes VRF <string>

192.168.1.0/24, ubest/mbest: 2/0
    *via 10.42.0.1, [20/0], 1w1d, bgp-65101, external, tag 65102
    *via 10.42.0.3, [20/0], 1w1d, bgp-65101, external, tag 65102
switch#
```

Start the app:
```
switch# run bash nohup /isan/bin/python /bootflash/ecmp_monitoring.py &
```

NX-OS will indicate that the app started, and found an ECMP bundle. 
```
switch# 2018 Feb 13 15:32:53 switch nxsdk: [ecmp_monitoring.py] Started service
switch# 2018 Feb 13 15:32:55 switch nxsdk: [ecmp_monitoring.py] Found an ECMP bundle: 192.168.1.0/24 --> Eth1/19, Eth1/20
```

Let's also verify that the app is running:
```
switch# show nxsdk internal service

NXSDK Started/Temp unavailabe/Max services : 1/0/32
NXSDK Default App Path         : /isan/bin/nxsdk
NXSDK Supported Versions       : 1.0 1.5

Service-name              Base App        Started(PID)      Version    RPM Package
------------------------- --------------- ----------------- ---------- ------------------------
/bootflash/ecmp_monitoring.py nxsdk_app1      BASH(24430)                  -
switch#
```

Configure the bandwidth threshold using the custom CLI:
```
switch# conf
Enter configuration commands, one per line. End with CNTL/Z.
switch(config)# ecmp_monitoring.py ?
  bw-threshold  Bandwidth threshold for monitoring

switch(config)# ecmp_monitoring.py bw-threshold ?
  <0-2147483647>  Bandwidth threshold value in Mbps

switch(config)# ecmp_monitoring.py bw-threshold 7500
```

When the actual bandwidth on a ECMP member exceeds the threshold, a syslog will be displayed:
```
switch# 2018 Feb 13 12:43:38 switch %NXSDK-4-WARNING_MSG:   [28703]  [ecmp_monitoring.py] High egress bandwidth: int=Eth1/20, bw=8000020224
```

A telemetry event will also be received by the collector:
```
server# python http_receiver.py -vv -l 0
Starting httpd on port 5000...
verbose           = True
more verbose      = True
verbose print len = 0 (0 is unlimited)
10.60.0.109 - - [13/Feb/2018 08:43:41] "POST /network/show%20ecmp_monitoring.py%20tm-use-only HTTP/1.0" 200 -
10.60.0.109 - - [13/Feb/2018 08:43:41] "POST /network/show%20ecmp_monitoring.py%20tm-use-only HTTP/1.0" 200 -
>>> URL            : /network/show%20ecmp_monitoring.py%20tm-use-only
>>> TM-HTTP-VER    : 1.0.0
>>> TM-HTTP-CNT    : 1
>>> Content-Type   : application/json
>>> Content-Length : 398
    Path => show ecmp_monitoring.py tm-use-only
            node_id_str   : switch
            collection_id : 145087
            data_source   : NX-API
            data          : {u'interface': u'Ethernet1/20', u'eth_outrate1_bits': u'7999955104'}
```

Stop the app:
```
switch# ecmp_monitoring.py stop-event-loop
```

## References:
https://github.com/CiscoDevNet/NX-SDK

http://www.cisco.com/c/en/us/td/docs/switches/datacenter/nexus9000/sw/7-x/programmability/guide/b_Cisco_Nexus_9000_Series_NX-OS_Programmability_Guide_7x/b_Cisco_Nexus_9000_Series_NX-OS_Programmability_Guide_7x_chapter_011010.html
