#!/usr/bin/env python3
import subprocess
import telnetlib
import base64
import random

from Crypto.Cipher import AES
from Crypto import Random
from flask import Flask, abort, jsonify
from flask import request

app = Flask(__name__)

block_size = AES.block_size

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


@app.route('/', methods=['GET'])
def index():
    return "Hello World!"


@app.route('/v1.0/tasks/createprofile', methods=['POST'])
def createprofile():
    if not request.json or not 'profilename' in request.json:
        abort(400)
    enter = "\n"
    name_profile = request.json['profilename']
    print(name_profile)
    command = name_profile
    print(command)
    result = subprocess.run(['/etc/openvpn/createclient.sh', '-u', command], stdout=subprocess.PIPE)
    var = result.stdout
    print("outvalue:" + enter)
    lines = var.split(enter.encode("ascii"))
    size = len(lines)
    rawpath = str(lines[size - 2])
    path = rawpath.split("\'")[1]
    print("path:" + path)
    source = open(path, "r").read()
    print("data:" + source)
    encrypt_data = encryptToBase64(keyEncrypt, ivEncrypt, source)
    encrypt_data = encrypt_data.replace("\n", "")
    print(encrypt_data)
    profile = {
        'code': 0,
        'message': "OK",
        'data': {
            'id': name_profile,
            'configData': encrypt_data}
    }
    print(profile)
    return jsonify(profile)


@app.route('/v1.0/tasks/killprofile', methods=['POST'])
def killprofile():
    if not request.json or not 'profilename' in request.json:
        abort(400)
    enter = "\n"
    name_profile = request.json['profilename']
    print(name_profile)
    host = "127.0.0.1"
    port = "6666"
    telnet = telnetlib.Telnet(host, port, 5)
    command = "kill " + name_profile + enter
    print(command)
    telnet.write(command.encode("ascii"))
    outputs = telnet.expect(["killed\r".encode("ascii"), "not found\r".encode("ascii")], 1)
    output = outputs[len(outputs) - 1]
    list_value = output.split(enter.encode("ascii"))
    strreturn = str(list_value[len(list_value) - 1])
    print(strreturn)
    telnet.close()
    jsondata = {
        'code': 200,
        'msg': strreturn
    }
    return jsonify(jsondata)


@app.route('/v1.0/tasks/removeprofile', methods=['POST'])
def removeprofile():
    if not request.json or not 'profilename' in request.json:
        abort(400)
    enter = "\n"
    name_profile = request.json['profilename']
    result = subprocess.run(['/etc/openvpn/removeclient.sh', '-u', name_profile], stdout=subprocess.PIPE)
    var = result.stdout
    print("outvalue:" + enter)
    lines = var.split(enter.encode("ascii"))
    size = len(lines)
    rawpath = str(lines[size - 2])
    msg = rawpath.split("\'")[1]
    jsondata = {
        'code': 200,
        'msg': msg
    }
    return jsonify(jsondata)


@app.route('/v1.0/tasks/controlvpn', methods=['POST'])
def resetvpn():
    if not request.json or not 'action' in request.json:
        abort(400)
    action = request.json['action']
    var = actionvpn(action)
    print("outvalue:" + var)
    jsondata = {
        'code': 200,
        'msg': "reset vpn done"
    }
    return jsonify(jsondata)


def actionvpn(action):
    return {
        0: subprocess.run(['/etc/openvpn/resetvpn.sh'], stdout=subprocess.PIPE).stdout,
        1: subprocess.run(['/etc/openvpn/turnoffvpn.sh'], stdout=subprocess.PIPE).stdout,
        2: subprocess.run(['/etc/openvpn/turnonvpn.sh'], stdout=subprocess.PIPE).stdout
    }.get(action, "nothing")


if __name__ == '__main__':
    app.run(host='0.0.0.0')
