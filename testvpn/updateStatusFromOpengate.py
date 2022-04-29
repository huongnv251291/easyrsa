import base64
import json
import multiprocessing
import os
import time
from os.path import exists

import requests
from Crypto.Cipher import AES

block_size = AES.block_size
enter = "\n"
unpad = lambda s: s[:-ord(s[len(s) - 1:])]
keyEncrypt = '757CBB5C17489F3A040D646FD7267CC2'
ivEncrypt = '1234567890ABCDEF'


def pad(text):
    bs = AES.block_size  # 16
    length = len(text)
    bytes_length = len(bytes(text, encoding='utf-8'))
    padding_size = length if (bytes_length == length) else bytes_length
    padding = bs - padding_size % bs
    padding_text = chr(padding) * padding
    return text + padding_text


def encrypt(key, iv, source):
    plain = pad(source)

    cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
    return cipher.encrypt(plain.encode("utf-8"))


def encryptToBase64(key, iv, source):
    return base64.encodebytes(encrypt(key, iv, source)).decode("utf-8")


def encryptToHexString(key, iv, source):
    return encrypt(key, iv, source).hex()


def encryptToBase64Url(key, iv, source):
    return base64.urlsafe_b64encode(encrypt(key, iv, source)).decode("utf-8")


def decrypt(key, iv, source):
    cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
    return unpad(cipher.decrypt(source))


def decryptFromHexString(key, iv, source):
    source_bytes = bytes.fromhex(source)
    return decrypt(key, iv, source_bytes).decode('utf-8')


def decryptFromBase64(key, iv, source):
    source_bytes = base64.b64decode(source)
    return decrypt(key, iv, source_bytes).decode('utf-8')


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
        originData = str(base64.b64decode(i['config']))
        encrypt_data = encryptToBase64(keyEncrypt, ivEncrypt, originData)
        encrypt_data = encrypt_data.replace("\n", "")
        i['config'] = encrypt_data
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
                {'id': str(datas[1].replace('.', '', )),
                 'host_name': 'vpn' + str(datas[1].replace('.', '', )),
                 'ip': datas[1],
                 'current_connection': datas[9],
                 'max_connection': 0,
                 'city': str(datas[5]),
                 'country': str(datas[6]),
                 'vpn_type': 0,
                 'cpu': 0,
                 'ram': 0,
                 'lastTimeSync': int(time.time() * 1000),
                 'online': 1,
                 'source': 1,
                 'config': str(datas[14])})
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
