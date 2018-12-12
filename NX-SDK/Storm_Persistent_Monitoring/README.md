Configure Storm Control on any required interfaces:
```
switch# conf
Enter configuration commands, one per line. End with CNTL/Z.
switch(config)# int e1/41
switch(config-if)# storm-control multicast level 1
switch(config-if)# storm-control broadcast level 1
switch(config-if)# storm-control unicast level 1
```

Copy storm.py to the bootflash.

Make sure Bash Shell and NX-SDK are enabled, then go to Bash and start the app:
```
switch# conf
Enter configuration commands, one per line. End with CNTL/Z.
switch(config)# feature bash-shell
switch(config)# feature nxsdk
switch(config)# end
switch# run bash sudo su
bash-4.2# cp /bootflash/storm.py /isan/bin
bash-4.2# nohup /isan/bin/python /isan/bin/storm.py &
bash-4.2# exit
exit
switch#
```

The app is starting:
```
2018 Dec 10 16:38:46 switch nxsdk: [storm.py] Started service

switch# sh nxsdk internal service

NXSDK Started/Temp unavailabe/Max services : 1/0/32
NXSDK Default App Path         : /isan/bin/nxsdk
NXSDK Supported Versions       : 1.0 1.5

Service-name              Base App        Started(PID)      Version    RPM Package
------------------------- --------------- ----------------- ---------- ------------
------------
/isan/bin/storm.py        nxsdk_app1      BASH(21279)                  -
switch#
```

If storm traffic is persisting after the period of time configured in the app (by default, 10 seconds), the interface(s) will be shut down:
```
switch# 2018 Dec 10 16:49:08 switch %NXSDK-4-WARNING_MSG:   [21279]  [storm.py] Traffic storm persisting on Ethernet1/41 after 10 minute(s): suppression discard count current=160587834500, previous=156941358000.  Shutting down interface
2018 Dec 10 16:49:09 switch %ETHPORT-5-IF_DOWN_CFG_CHANGE: Interface Ethernet1/41 is down(Config change)
2018 Dec 10 16:49:09 switch %ETHPORT-5-IF_DOWN_ADMIN_DOWN: Interface Ethernet1/41 is down (Administratively down)
```

The interface(s) that the app has shut down are automatically brought back up after a longer period of time (by default, 1 minute):
```
switch(config)# 2018 Dec 12 08:16:21 switch %NXSDK-4-WARNING_MSG:   [12628]  [storm.py] Interface Ethernet1/41 has been shut for more than 60 seconds, unshutting
2018 Dec 12 08:16:22 switch %ETHPORT-5-IF_ADMIN_UP: Interface Ethernet1/41 is admin up .
```

The shut and unshut timers can be configured as follows:
```
switch(config)# storm.py ?
  shut-interval    Interval in seconds after which the interfaces on which storm traffic persists
                   are shut down
  unshut-interval  Interval in seconds after which the interfaces that got shut down by the app are
                   brought back up
```
