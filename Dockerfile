FROM phusion/baseimage:0.10.1
MAINTAINER Nicolas Delecroix <ndelecro@cisco.com>

# Use baseimage-docker's init system.
CMD ["/sbin/my_init"]

# Dependencies
RUN	apt-get -y update && \
	apt-get -y install python-pip gdebi-core python3-dev python-dev libtool-bin wget emacs iputils-ping subversion && \
	pip install scp

# Ansible
RUN     pip install ansible==2.6.1 ncclient && \
	mkdir /root/Ansible && \
	svn checkout "https://github.com/ndelecro/nx-os-programmability/trunk/Ansible/2.5" /root/Ansible && \
	mkdir /etc/ansible && \
	svn checkout "https://github.com/ndelecro/nx-os-programmability/trunk/Ansible/Config" /etc/ansible

# NX-API CLI
RUN     pip install requests && \
	mkdir /root/NX-API_CLI && \
	svn checkout "https://github.com/ndelecro/nx-os-programmability/trunk/NX-API_CLI" /root/NX-API_CLI

# Robot
RUN	pip install robotframework && \
	mkdir /root/Robot && \
	svn checkout "https://github.com/ndelecro/nx-os-programmability/trunk/Robot" /root/Robot

# YDK
RUN	wget https://devhub.cisco.com/artifactory/debian-ydk/0.7.2/libydk_0.7.2-1_amd64.deb -P /tmp && \
	gdebi --n /tmp/libydk_0.7.2-1_amd64.deb

# YDK NX-OS
# RUN	pip install ydk-models-cisco-nx-os==0.7.4 && \
# 	mkdir -p /root/YANG/NX-OS/YDK && \
# 	svn checkout "https://github.com/ndelecro/nx-os-programmability/trunk/YANG/NX-OS/YDK" /root/YANG/NX-OS/YDK && \
# 	wget https://github.com/YangModels/yang/blob/master/vendor/cisco/nx/7.0-3-I7-3/Cisco-NX-OS-device.yang?raw=true -O /root/YANG/NX-OS/YDK/Cisco-NX-OS-device.yang

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
