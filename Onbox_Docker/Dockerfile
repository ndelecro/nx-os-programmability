FROM ubuntu
MAINTAINER Nicolas Delecroix <ndelecro@cisco.com>

RUN     apt-get -y update && \
        apt-get -y install iproute2 iputils-ping emacs subversion

# Packet Generator
RUN     apt-get -y install python3-scapy && \
        mkdir /root/Packet_Generator && \
        svn checkout --trust-server-cert --non-interactive "https://github.com/ndelecro/nx-os-programmability/trunk/Onbox_Docker/Packet_Generator" /root/Packet_Generator

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
