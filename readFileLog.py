import json
import multiprocessing
import os
import time
from os.path import exists
import re

import requests

if __name__ == "__main__":
    my_file_handle = open('E://huong//logTest//vpn.log', 'r')
    listIp = []
    listLine = []
    listIsp = []
    file_exists = exists('E://huong//logTest//ipError.log')
    if file_exists:
        os.remove('E://huong//logTest//ipError.log')
    file_exists = exists('E://huong//logTest//lineError.log')
    if file_exists:
        os.remove('E://huong//logTest//lineError.log')
    file_exists = exists('E://huong//logTest//ispError.log')
    if file_exists:
        os.remove('E://huong//logTest//ispError.log')
    line = 0

        steamIp = open('E://huong//logTest//ipError.log', 'w', buffering=1, encoding="utf-8")
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
                r = requests.get(f"http://ip-api.com/json/{ip}")
                data_from_ip_info = json.loads(r.text)
                if 'status' in data_from_ip_info:
                    if data_from_ip_info['status'] == 'success':
                        if 'country' in data_from_ip_info:
                            ip = ip + str(', ' + data_from_ip_info['country'])
                        if 'regionName' in data_from_ip_info:
                            ip = ip + str(', ' + data_from_ip_info['regionName'])
                        if 'city' in data_from_ip_info:
                            ip = ip + str(', ' + data_from_ip_info['city'])
                        if 'org' in data_from_ip_info:
                            ip = ip + str(', ' + data_from_ip_info['org'])
                        if 'as' in data_from_ip_info:
                            ip = ip + str(', ' + data_from_ip_info['as'])
                        if 'isp' in data_from_ip_info:
                            ip = ip + str(', ' + data_from_ip_info['isp'])
                ip = ip + ', END'
                textWrite = str('\n' + ip).encode('utf-8').decode('utf-8')
                print(textWrite)
                steamIp.write(textWrite)
                steamIp.flush()
                time.sleep(2)
    #
    #     if line == 0:
    #
    #     line = line + 1
    #     fp.write('\n'.join(str(item) for item in listIp))
    # with open('E://huong//logTest//lineError.log', 'w') as fp:
    #     fp.write('\n'.join(str(item) for item in listLine))
