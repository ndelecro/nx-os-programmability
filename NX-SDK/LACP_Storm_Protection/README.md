Copy lacp_storm.py to the bootflash.

Make sure Bash Shell and NX-SDK are enabled, then go to Bash and start the app:
```
switch# conf
Enter configuration commands, one per line. End with CNTL/Z.
switch(config)# feature bash-shell
switch(config)# feature nxsdk
switch(config)# end
switch# run bash sudo su
bash-4.2# cp /bootflash/lacp_storm.py /isan/bin
bash-4.2# nohup /isan/bin/lacp_storm.py /isan/bin/lacp_storm.py &
bash-4.2# exit
exit
switch#
```

The app is starting:
```
2019 Feb  5 13:37:09 switch nxsdk: [lacp_storm.py] Started service
```

If the LACP received PDU delta exceeds a threshold after the period of time configured in the app (by default, 5 seconds), the interface(s) will be shut down:
```
2019 Feb  5 13:38:09 switch %NXSDK-4-WARNING_MSG:   [1518]  [lacp_storm.py] LACP PDU storm on Ethernet1/42 after 5 second(s): count current=7085, previous=7077.  Shutting down interface
```

The check interval can be configured as follows:
```
switch(config)# lacp_storm.py ?
  check-interval  Interval in seconds to check for LACP PDU storm

switch(config)# lacp_storm.py check-interval ?
  <0-2147483647>  Interval in seconds

switch(config)# lacp_storm.py check-interval 10
```
