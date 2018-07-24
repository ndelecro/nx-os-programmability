FROM phusion/baseimage:0.10.1
MAINTAINER Nicolas Delecroix <ndelecro@cisco.com>

# Use baseimage-docker's init system.
CMD ["/sbin/my_init"]

# ...put your own build instructions here...
RUN touch nico

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
