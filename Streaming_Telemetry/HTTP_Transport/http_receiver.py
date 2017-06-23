#! /usr/bin/python

import os, string
from   BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import random
from   pprint import pprint
import requests
import json
import cgi
import urlparse
import argparse
import urllib

g_verbose   = False
g_verbose_2 = False
g_print_len = 80

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        f = open("index.html", "r")
        self.wfile.write(f.read())

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Respond 200 OK
        self._set_headers()
        self.send_response(200)
        self.end_headers()

        # Process headers
        (action, url, ver) = self.requestline.split();
        tm_http_ver  = self.headers.getheader('TM-HTTP-Version')
        tm_http_cnt  = self.headers.getheader('TM-HTTP-Content-Count')
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        data_len     = int(self.headers['Content-Length'])
        print ">>> URL            :",  url
        print ">>> TM-HTTP-VER    :",  tm_http_ver
        print ">>> TM-HTTP-CNT    :",  tm_http_cnt
        print ">>> Content-Type   :",  ctype
        print ">>> Content-Length :",  data_len

        if (g_verbose):
            dn_list = [];
            dn_data = {};

            if ctype == 'multipart/form-data':
                form = cgi.FieldStorage(
                        fp      = self.rfile,
                        headers = self.headers,
                        environ = {'REQUEST_METHOD':'POST',
                                   'CONTENT_TYPE':self.headers['Content-Type'],})
                dn_list = form.keys()
                if (g_verbose_2):
                    for dn in dn_list:
                        dn_data[dn] = form.getvalue(dn)
            else:
                (root, nw, dn_raw) = url.split('/')
                dn = urllib.unquote(dn_raw)
                dn_list.append(dn)
                if (g_verbose_2):
                    data = self.rfile.read(int(self.headers['Content-Length']))
                    dn_data[dn] = data

            # output
            for dn in dn_list:
                print "    Path => %s" % (dn)
                if (g_verbose_2):
                    json_data = json.loads(dn_data[dn])
                    if (not json_data):
                        continue
                    print "            node_id_str   : %s" % (json_data['node_id_str'])
                    print "            collection_id : %s" % (json_data['collection_id'])
                    print "            data_source   : %s" % (json_data['data_source'])
                    if (g_print_len == 0):
                        print "            data          : %s" % (json_data['data'])
                    else:
                        trail = ""
                        if (data_len > g_print_len):
                            trail = "..."
                        print "            data          : %-.*s ..." % (g_print_len, json_data['data'])
        else:
            # Still need to consume the data
            self.rfile.read(int(self.headers['Content-Length']))

        print ""

def run(server_class=HTTPServer, handler_class=S, port=9000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd on port %d...' % (port)
    if (g_verbose == True):
        print 'verbose           = True'
    if (g_verbose_2 == True):
        print 'more verbose      = True'
        print 'verbose print len = %d (0 is unlimited)' % (g_print_len)

    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    parser = argparse.ArgumentParser()
    parser.add_argument('-v',  dest='verbose', action='store_true', default=False, help="verbose")
    parser.add_argument('-vv', dest='more_verbose', action='store_true', default=False, help="more verbose")
    parser.add_argument('-p', '--port', dest='port', action='store', default=5000, help="server listening port")
    parser.add_argument('-l', '--data_len', dest='data_len', action='store', default=80, help="print data length")
    args = parser.parse_args()

    g_port      = args.port
    g_verbose   = args.verbose
    g_verbose_2 = args.more_verbose
    g_print_len = int(args.data_len)
    if (g_verbose_2):
        g_verbose = True

    run(port=int(g_port))
