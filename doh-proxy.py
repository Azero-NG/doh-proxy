#!/usr/bin/env python
import requests
import json
import time
from dnslib.server import DNSServer
from dnslib.server import BaseResolver
from dnslib.server import DNSLogger
from dnslib.server import RR
from dnslib import QTYPE

GOOGLE_DNS_URL = "https://dns.google.com/resolve?"
dnssess = requests.session()
socks5proxies = {'http': 'socks5h://@127.0.0.1:1190', 'https': 'socks5h://@127.0.0.1:1190'}
dnssess.proxies = socks5proxies
waitime = 1
while True:
    try:
        myip = requests.get('https://api.ipify.org?format=text',proxies = socks5proxies)
        while myip.status_code!=200:
            myip = requests.get('https://api.ipify.org?format=text',proxies = socks5proxies)
        print("myip:",myip.text)
        myip = myip.text+'/32'
        break
    except:
        print("error")
        time.sleep(waitime*2)
class HTTPSResolver(BaseResolver):
    def resolve(self, request, handler):
        hostname = str(request.q.qname)
        ltype = request.q.qtype
        print(hostname)
        headers = {"Host": "dns.google.com"}
        try:

            lookup_resp = dnssess.get('%sname=%s&type=%s&edns_client_subnet=%s' % (GOOGLE_DNS_URL,
                hostname,
                ltype,
                myip))
            answer = json.loads(lookup_resp.text)['Answer']
            reply = request.reply()
            for record in answer:
                rtype = QTYPE[record['type']]
                zone = "%s %s %s %s" % (str(record['name']),
                                        record['TTL'],
                                        rtype,
                                        str(record['data']))
                print(str(record['data']))
                reply.add_answer(*RR.fromZone(zone))
            return reply
        except:
            reply = request.reply()
            return reply
            pass
resolver = HTTPSResolver()
logger = DNSLogger()

server = DNSServer(resolver,
                           port=60058,
                           address='localhost',
                           logger=logger)
server.start_thread()
while 1:
    time.sleep(300)
