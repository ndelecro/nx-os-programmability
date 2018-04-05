# Use a Nexus 3K/9K as a PXE server
##### Author: Nicolas Delecroix
##### Email: ndelecro@cisco.com

## Description:
A Nexus 3K/9K can be used as a PXE server to bootstrap switches connected to it. We leverage the Guest Shell to run a DCHP, TFTP and HTTP servers. Here's the configuration steps.
A demo recording can be found on https://www.youtube.com/watch?v=f1F97TXlluU.

## Prerequisite
```
switch# guestshell resize rootfs 350
```

## DHCP server
The switch needs to be configured for DHCP-relay for DHCP/BOOTP discovery packets to be punted to the CPU. 
NX-OS configuration example:
```
feature dhcp
ip dhcp relay
interface Ethernet1/1
  description connects to the server
  no switchport
  speed 1000
  ip address 192.168.0.1/24
  ip dhcp relay address 192.168.0.1
```

Install the DHCP server in the guest shell:
```
switch# guestshell
[guestshell@guestshell ~]$ sudo su
[root@guestshell guestshell]# chvrf management yum install dhcp.x86_64
...
Installed:
  dhcp.x86_64 12:4.2.5-42.el7.centos

Dependency Installed:
  bind-libs-lite.x86_64 32:9.9.4-29.el7_2.1    bind-license.noarch 32:9.9.4-29.el7_2.1
  dhcp-common.x86_64 12:4.2.5-42.el7.centos    dhcp-libs.x86_64 12:4.2.5-42.el7.centos

Complete!
[root@guestshell guestshell]#
```

DHCP configuration:
```
[root@guestshell ~]# cat /etc/dhcp/dhcpd.conf
# specify domain name
option domain-name "server.world";

# specify name server's hostname or IP address
option domain-name-servers dlp.server.world;

# default lease time
default-lease-time 600;

# max lease time
max-lease-time 7200;

# this DHCP server to be declared valid
authoritative;

# specify network address and subnet mask
subnet 192.168.0.0 netmask 255.255.255.0 {
    # specify the range of lease IP address
    range dynamic-bootp 192.168.0.200 192.168.0.254;
    # specify broadcast address
    option broadcast-address 192.168.0.255;
    # specify default gateway
    option routers 192.168.0.1;
    # PXE server IP: ourselves
    next-server 192.168.0.1;
    filename "pxelinux.0";
}
[root@guestshell ~]# 
```

Start the DHCP server:
```
[root@guestshell guestshell]# systemctl start dhcpd
[root@guestshell guestshell]# systemctl enable dhcpd
ln -s '/usr/lib/systemd/system/dhcpd.service' '/etc/systemd/system/multi-user.target.wants/dhcpd.service'
```

## TFTP server
Install the TFTP server in the guest shell:
```
[root@guestshell ~]# chvrf management yum install tftp.x86_64 tftp-server.x86_64

Create the directory /tftpboot.

TFTP configuration:
[root@guestshell xinetd.d]# cat /etc/xinetd.d/tftp
# default: off
# description: The tftp server serves files using the trivial file transfer \
#    protocol.  The tftp protocol is often used to boot diskless \
#    workstations, download configuration files to network-aware printers, \
#    and to start the installation process for some operating systems.
service tftp
{
    socket_type    = dgram
    protocol        = udp
    wait            = yes
    user            = root
    server        = /usr/sbin/in.tftpd
    server_args    = -s /tftpboot
    disable        = no
    per_source    = 11
    cps            = 100 2
    flags            = IPv4
}
[root@guestshell xinetd.d]#
```

The following step is needed to disable the NX-OS TFTP server. NOTE: for now this needs to be done after each reboot.
From the NX-OS CLI:
```
switch# system no hap-reset

Go to the native shell with "run bash" from the NX-OS CLI.  Become root and kill tftpd 3 times in 10 seconds so our system manager detects this and does not restart the process anymore.
bash-4.2# kill -9 `pidof in.tftpd`
bash-4.2# kill -9 `pidof in.tftpd`
bash-4.2# kill -9 `pidof in.tftpd`
```

Back to the guest shell, restart xinetd and tftp:
```
[root@guestshell guestshell]# systemctl restart xinetd
[root@guestshell guestshell]# systemctl restart tftp
[root@guestshell guestshell]# systemctl enable tftp
```

Verification:
```
[root@guestshell tmp]# systemctl status tftp
● tftp.service - Tftp Server
   Loaded: loaded (/usr/lib/systemd/system/tftp.service; enabled; vendor preset: disabled)
   Active: active (running) since Tue 2016-01-12 20:05:17 UTC; 1s ago
     Docs: man:in.tftpd
 Main PID: 141 (in.tftpd)
   CGroup: /system.slice/tftp.service
           └─141 /usr/sbin/in.tftpd -s /tftpboot
[root@guestshell tmp]#
```

## PXE
Install the syslinux package and copy the PXE files to /tftpboot:
```
[root@guestshell ~]# chvrf management yum install syslinux
[root@guestshell ~]# cd /usr/share/syslinux/
[root@guestshell syslinux]# cp pxelinux.0 menu.c32 memdisk mboot.c32 chain.c32 /tftpboot
```

PXE configuration:
```
[root@guestshell pxelinux.cfg]# vi default
default menu.c32
prompt 0
timeout 300
ONTIMEOUT 1

menu title ########## INSBU PXE Boot Menu ##########

label 1
menu label ^1) Install CentOS 7
menu default
kernel centos7/vmlinuz
append initrd=centos7/initrd.img method=http://192.168.0.1/centos7 devfs=nomount

label 2
menu label ^2) Boot from local drive
localboot 0
[root@guestshell pxelinux.cfg]#
```

## Kernel
In the guest shell, copy the kernel and initial RAM disk (vmlinuz and initrd.img) to /tftpboot/centos7.

## HTTP server
Install the EPEL repository that will provide us lighttpd:
```
[root@guestshell ~]# chvrf management yum search epel
```

Install lighttpd:
```
[root@guestshell ~]# chvrf management yum install lighttpd.x86_64
```

Lighttpd configuration:
```
[root@guestshell lighttpd]# cat /etc/lighttpd/lighttpd.conf
server.document-root = "/var/www/"

server.port = 80

mimetype.assign = (
  ".html" => "text/html",
  ".txt" => "text/plain",
  ".jpg" => "image/jpeg",
  ".png" => "image/png"
)
[root@guestshell lighttpd]#

[root@guestshell ~]# service lighttpd start
Redirecting to /bin/systemctl start  lighttpd.service
[root@guestshell lighttpd]# systemctl enable lighttpd
Created symlink from /etc/systemd/system/multi-user.target.wants/lighttpd.service to /usr/lib/systemd/system/lighttpd.service.
[root@guestshell lighttpd]#
```
Verification:
```
[root@guestshell centos7]# systemctl status lighttpd
● lighttpd.service - Lightning Fast Webserver With Light System Requirements
   Loaded: loaded (/usr/lib/systemd/system/lighttpd.service; enabled; vendor preset: disabled)
   Active: active (running) since Wed 2016-01-13 21:09:41 UTC; 2 days ago
 Main PID: 7129 (lighttpd)
   CGroup: /system.slice/lighttpd.service
           └─7129 /usr/sbin/lighttpd -D -f /etc/lighttpd/lighttpd.conf
```

## Mount the Linux distribution ISO 
If using a USB key, those steps are needed to make it accessible from the guest shell.
switch# run bash
```
bash-4.2$ sudo su
bash-4.2# mount --make-shared /usbslot1
bash-4.2# mkdir /var/run/netns/usbslot1
bash-4.2# mount --bind /usbslot1 /var/run/netns/usbslot1
```

Now mount the ISO:
```
bash-4.2# cd /usbslot1
bash-4.2# mount -o loop CentOS-7.0-1406-x86_64-Minimal.iso mnt/centos7/
mount: warning: mnt/centos7/ seems to be mounted read-only.
bash-4.2# cd mnt/centos7/
bash-4.2# ls -l
total 90
-rw-r--r-- 1  500 debug    14 Jul  4  2014 CentOS_BuildTag
drwxr-xr-x 3  500 debug  2048 Jul  4  2014 EFI
-rw-r--r-- 1  500 debug   214 Jul 17  2014 EULA
-rw-r--r-- 1  500 debug 18009 Jul  4  2014 GPL
drwxr-xr-x 3  500 debug  2048 Jul  4  2014 images
drwxr-xr-x 2  500 debug  2048 Jul  4  2014 isolinux
drwxr-xr-x 2  500 debug  2048 Jul  4  2014 LiveOS
drwxr-xr-x 2  500 debug 53248 Jul 17  2014 Packages
drwxr-xr-x 2 root root   4096 Jul 17  2014 repodata
-rw-r--r-- 1  500 debug  1690 Jul  4  2014 RPM-GPG-KEY-CentOS-7
-rw-r--r-- 1  500 debug  1690 Jul  4  2014 RPM-GPG-KEY-CentOS-Testing-7
-r--r--r-- 1 root root   2883 Jul 17  2014 TRANS.TBL
bash-4.2# 
```

Back to guest shell, symlink the USB key centos mount to /var/www/centos7:
```
[root@guestshell guestshell]# cd /var/www
[root@guestshell www]# l
total 4
drwxr-xr-x 2 root root 1024 Jan 13 20:21 dsl
-rw-r--r-- 1 root root    3 Jan 13 19:21 index.html
[root@guestshell www]# ln -s /var/run/netns/usbslot1/mnt/centos7/ centos7
```

The Nexus switch configuration is now complete for a PXE boot of servers.
