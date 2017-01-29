# Nexus 9K PTP Monitoring
##### Author: Nicolas Delecroix
##### Email: ndelecro@cisco.com

## Description:

This repository contains a Python script to monitor the PTP accuracy of a Nexus 9K.

ptp_monitoring.py periodically checks the PTP accuracy and logs any value that exceeds a threshold.

The threshold can be modified by editing the constant MAX_CORRECTION_VAL (nanoseconds) in the script.
The maximum number of PTP corrections to check can be modified by editing MAX_ENTRIES_TO_CHECK.
The delay between checks can be modified by editing DELAY_BETWEEN_CHECK (seconds).

### Usage:

Add the management IPs / hostnames of the switches to the file switches_ip.

$ ./ptp_monitoring.py switches_ip_file

Example:
$ ./ptp_monitoring.py switches_ip_file
***** Switch 93180-1 *****
show ptp corrections
PTP correction too high: switch=93180-1, correction=184, time=Sun Jan 29 10:58:27 2017 863202
PTP correction too high: switch=93180-1, correction=186, time=Sun Jan 29 10:58:25 2017 864105

