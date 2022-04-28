import json
import multiprocessing
import os
import time

import requests
from OpenVpn import OpenVpn
from os.path import exists
import base64


def ping(i):
    ip = i['ip']
    print(ip)
    res = os.popen(f"ping {ip}").read()
    print(res)
    if "Received = 4" in res:
        print(f"UP {ip} Ping Successful")
        r = requests.get(f"https://ipinfo.io/ {ip} /json")
        data_from_ip_info = json.loads(r.text)
        if 'city' in data_from_ip_info:
            i['city'] = str(data_from_ip_info['city'])
        if 'region' in data_from_ip_info:
            i['city'] = str(data_from_ip_info['region'])
        i['config'] = base64.b64decode(i['config'])
        print(i)
        return i
    else:
        print(f"DOWN {ip} Ping Unsuccessful")
        return "None"


if __name__ == "__main__":
    response = requests.get("http://www.vpngate.net/api/iphone/")
    data = str(response.text)
    # print(data)
    listData = []
    lines = data.split('\n')
    startLine = 2
    counter = 0
    for line in lines:
        datas = line.split(",")
        if len(datas) == 15 and counter > startLine:
            listData.append(
                {'id': datas[1].replace('.', '', ),
                 'host_name': datas[0],
                 'ip': datas[1],
                 'current_connection': datas[9],
                 'max_connection': 0,
                 'city': datas[5],
                 'country': datas[6],
                 'vpn_type': 0,
                 'cpu': 0,
                 'ram': 0,
                 'lastTimeSync': int(time.time() * 1000),
                 'online': 1,
                 'source': 0,
                 'config': datas[14]})
        counter = counter + 1
    dataServerLive = []
    print(len(listData))
    num_threads = 2 * multiprocessing.cpu_count()
    with multiprocessing.Pool(num_threads) as pool:
        result = pool.map(ping, [i for i in listData])
    for value in result:
        if not str(value).__eq__('None'):
            dataServerLive.append(value)
    print("server live :" + str(len(dataServerLive)))
    file_exists = exists('E://server_gate_live.json')
    if file_exists:
        os.remove('E://server_gate_live.json')
    with open('E://server_gate_live.json', "w") as outfile:
        outfile.write(json.dumps(dataServerLive))
