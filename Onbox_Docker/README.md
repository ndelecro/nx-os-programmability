Run at least NX-OS 9.2(1).

NX-OS:
```
switch# conf
Enter configuration commands, one per line. End with CNTL/Z.
switch(config)# feature bash-shell
switch(config)# end
switch# run bash sudo su
```

We're now in the Nexus 9K native Bash shell. Let's enable Docker:
```
bash-4.3# service docker start
bash-4.3# chkconfig --add docker
```

Start the Docker container. If you only need access to the management port, run:
```
bash-4.3# docker run --name=programmability --hostname=programmability -it ndelecro/nexus9k-onbox:latest
```

If you need access to the management port and to the front-panel ports, run:
```
bash-4.3# docker run --name=programmability --hostname=programmability -v /var/run/netns:/var/run/netns:ro,rslave --rm --network host --cap-add SYS_ADMIN -it ndelecro/nexus9k-onbox:latest
```

If you get an error like `docker: Error response from daemon: Get https://registry-1.docker.io/v2/: dial tcp: lookup registry-1.docker.io on [::1]:53: dial udp [::1]:53: connect: cannot assign requested address.`, check your management IP proxy, DNS etc. to make sure you have basic Internet connectivity from the shell. If you're accessing Internet via the management port, make sure that you're in the `management` network namespace:
```
bash-4.3# ip netns list
management (id: 1)
default (id: 0)
bash-4.3# ip netns exec management bash
```

Or prefix the `docker` call by `ip netns exec management`:
```
bash-4.3# ip netns exec management docker run --name=programmability --hostname=programmability -it ndelecro/nexus9k-onbox:latest
```

We're now inside the container:
```
root@programmability:/#
```
