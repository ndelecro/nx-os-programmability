FROM phusion/baseimage:0.10.1
MAINTAINER Nicolas Delecroix <ndelecro@cisco.com>

# Use baseimage-docker's init system.
CMD ["/sbin/my_init"]

# Dependencies
RUN	apt-get -y update && \
	apt-get -y install python-pip gdebi-core python3-dev python-dev libtool-bin wget emacs iputils-ping subversion

# Ansible
RUN	pip install ansible==2.6.1 && \
	mkdir /root/Ansible && \
	svn checkout "https://github.com/ndelecro/Nexus-9K-Programmability/trunk/Ansible/2.5" /root/Ansible && \
	mkdir /etc/ansible && \
	svn checkout "https://github.com/ndelecro/Nexus-9K-Programmability/trunk/Ansible/Config" /etc/ansible

# NX-API CLI
RUN     pip install requests && \
	mkdir /root/NX-API_CLI && \
	svn checkout "https://github.com/ndelecro/Nexus-9K-Programmability/trunk/NX-API_CLI" /root/NX-API_CLI

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
