# Nexus 9K Interface Load Monitoring
##### Author: Nicolas Delecroix
##### Email: ndelecro@cisco.com

## Description:

This repository contains a Python script to monitor the load of a Nexus 9K interface.

The delay between checks can be modified by editing DELAY_BETWEEN_CHECK (seconds).

### Usage:

```
./intf_load_monitoring.py switch_name interface max_load(bits/sec)
```

Example:
```
$ ./intf_load_monitoring.py 93180-1 e1/41 30000
show interface e1/41
2017-03-31 17:31:19 - Interface load too high: switch=93180-1, load=1442247080
show interface e1/41
2017-03-31 17:31:24 - Interface load too high: switch=93180-1, load=961541864
```

