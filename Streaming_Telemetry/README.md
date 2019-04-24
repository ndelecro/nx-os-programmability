## NX-OS configuration example
```
telemetry
  destination-group 1
    ip address 10.60.0.96 port 5000 protocol HTTP encoding JSON
  sensor-group 1
    data-source NX-API
    path "show mac address-table" depth 0
  subscription 1
    dst-grp 1
    snsr-grp 1 sample-interval 1000
```

## Python receiver usage example
```
# python http_receiver.py -l 0 -vv
Starting httpd on port 5000...
verbose           = True
more verbose      = True
verbose print len = 0 (0 is unlimited)
10.60.0.108 - - [25/Oct/2018 04:49:16] "POST /network/telemetry_post HTTP/1.0" 200 -
10.60.0.108 - - [25/Oct/2018 04:49:16] "POST /network/telemetry_post HTTP/1.0" 200 -
>>> URL            : /network/telemetry_post
>>> TM-HTTP-VER    : 1.0.0
>>> TM-HTTP-CNT    : 2
>>> Content-Type   : multipart/form-data
>>> Content-Length : 1188
    Path => sys/tm-connection-hello
            node_id_str   : n9kv-4
            collection_id : 0
            data_source   : NONE
            data          : {
    "message": "resync"
}
    Path => show mac address-table
            node_id_str   : n9kv-4
            collection_id : 1
            data_source   : NX-API
            data          : {
    "TABLE_mac_address": {
        "ROW_mac_address": {
            "disp_age": "-",
            "disp_vlan": "-",
            "disp_port": "(R)",
            "disp_mac_addr": "0050.56b9.b903",
            "disp_type": "static",
            "disp_is_ntfy": "F",
            "disp_is_secure": "F"
        }
    }
}
```
