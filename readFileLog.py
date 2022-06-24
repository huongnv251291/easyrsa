import json
import multiprocessing
import os
import time
from os.path import exists
import re

import requests

if __name__ == "__main__":
    my_file_handle = open('F://log//vpn.log', 'r')
    listIp = []
    listLine = []
    listIsp = []
    file_exists = exists('F://log//ipError.log')
    if file_exists:
        os.remove('F://log//ipError.log')
    file_exists = exists('F://log//lineError.log')
    if file_exists:
        os.remove('F://log//lineError.log')
    file_exists = exists('F://log//ispError.log')
    if file_exists:
        os.remove('F://log//ispError.log')
    line = 0
    steamIp = open('F://log//ipError.log', 'w', buffering=1, encoding="utf-8")
    steamIp.write('ip,country,regionName,city,org,as,isp')
    for value in my_file_handle:
        if value.endswith('TLS Error: TLS handshake failed\n'):
            print(value)
            listLine.append(value)
            ipPort = value.split(' ')[6].split(':')
            if len(ipPort) < 2:
                ipPort = value.split(' ')[7].split(':')
            ip = ipPort[0].replace('vpn151236221109free/', '')
            if listIp.count(ip) <= 0:
                listIp.append(ip)
                steamIp.write(value)
                steamIp.flush()
    #
    #     if line == 0:
    #
    #     line = line + 1
    #     fp.write('\n'.join(str(item) for item in listIp))
    # with open('F://log//lineError.log', 'w') as fp:
    #     fp.write('\n'.join(str(item) for item in listLine))
