#! /usr/bin/python3

import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import send, IP, ICMP

send(IP(dst="192.168.0.2")/ICMP())
