#!/bin/bash
apt update
yes | apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
#yes | apt-get install python3-pip python3-dev nginx
yes | apt install python3-venv
mkdir -p /root/openvpn
mkdir -p /root/openvpn/vpnapiproject
cd /root/openvpn/vpnapiproject/ || return
python3 -m venv vpnapiprojectenv
source vpnapiprojectenv/bin/activate
pip install wheel
pip install gunicorn flask
pip install pycrypto
echo "create file api"
touch /root/openvpn/vpnapiproject/api.py
echo "#!/usr/bin/env python3
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
keyEncrypt = '757cbb5c17489f3a040d646fd7267cc2'
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

    cipher = AES.new(key.encode(\"utf-8\"), AES.MODE_CBC, iv.encode(\"utf-8\"))
    return cipher.encrypt(plain.encode(\"utf-8\"))


def encryptToBase64(key, iv, source):
    return base64.encodebytes(encrypt(key, iv, source)).decode(\"utf-8\")


def encryptToHexString(key, iv, source):
    return encrypt(key, iv, source).hex()


def encryptToBase64Url(key, iv, source):
    return base64.urlsafe_b64encode(encrypt(key, iv, source)).decode(\"utf-8\")


def decrypt(key, iv, source):
    cipher = AES.new(key.encode(\"utf-8\"), AES.MODE_CBC, iv.encode(\"utf-8\"))
    return unpad(cipher.decrypt(source))


def decryptFromHexString(key, iv, source):
    source_bytes = bytes.fromhex(source)
    return decrypt(key, iv, source_bytes).decode('utf-8')


def decryptFromBase64(key, iv, source):
    source_bytes = base64.b64decode(source)
    return decrypt(key, iv, source_bytes).decode('utf-8')


@app.route('/',methods=['GET'])
def index():
    return \"Hello World!\"


@app.route('/v1.0/tasks/createprofile', methods=['POST'])
def createprofile():
    if not request.json or not 'profilename' in request.json:
        abort(400)
    enter = \"\n\"
    nameProfile = request.json['profilename']
    print(nameProfile)
    command = nameProfile
    print(command)
    result = subprocess.run(['/etc/openvpn/removeclient.sh', '-u', command], stdout=subprocess.PIPE)
    var = result.stdout
    print(\"outvalue:\" + enter)
    lines = var.split(enter.encode(\"ascii\"))
    size = len(lines)
    rawpath = str(lines[size - 2])
    path = rawpath.split(\"\'\")[1]
    source = open(path, \"r\").read()
    encryptData = encryptToBase64(keyEncrypt, ivEncrypt, source)
    stringreturn = str(encryptData)
    print(stringreturn)
    profile = {
        'code': 0,
        'message': \"OK\",
        'data': {
            'id': nameProfile,
            'configData': stringreturn
        }
    }
    print(profile)
    return jsonify(profile)


@app.route('/v1.0/tasks/killprofile', methods=['POST'])
def killprofile():
    if not request.json or not 'profilename' in request.json:
        abort(400)
    enter = \"\n\"
    nameProfile = request.json['profilename']
    print(nameProfile)
    HOST = \"127.0.0.1\"
    PORT = \"6666\"
    telnet = telnetlib.Telnet(HOST, PORT, 5)
    command = \"kill \" + nameProfile + enter
    print(command)
    telnet.write(command.encode(\"ascii\"))
    outputs = telnet.expect([\"killed\r\".encode(\"ascii\"), \"not found\r\".encode(\"ascii\")], 1)
    output = outputs[len(outputs) - 1]
    listValue = output.split(enter.encode(\"ascii\"))
    strreturn = str(listValue[len(listValue) - 1])
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
    enter = \"\n\"
    nameProfile = request.json['profilename']
    result = subprocess.run(['/etc/openvpn/removeclient.sh', '-u', nameProfile], stdout=subprocess.PIPE)
    var = result.stdout
    print(\"outvalue:\" + enter)
    lines = var.split(enter.encode(\"ascii\"))
    size = len(lines)
    rawpath = str(lines[size - 2])
    msg = rawpath.split(\"\'\")[1]
    jsondata = {
        'code': 200,
        'msg': msg
    }
    return jsonify(jsondata)


if __name__ == '__main__':
    app.run(host='0.0.0.0')" >>/root/openvpn/vpnapiproject/api.py
ufw allow 5000
echo "create file wsgi"
touch /root/openvpn/vpnapiproject/wsgi.py
echo "from api import app

if __name__ == \"__main__\":
    app.run()" >>/root/openvpn/vpnapiproject/wsgi.py
deactivate
echo "create file vpnservice"
cat >/etc/systemd/system/vpnservice.service <<EOF
[Unit]
Description=Gunicorn instance to server vpnservice
After=network.target

[Service]
User=sammy
Group=www-data
WorkingDirectory=/root/openvpn/vpnapiproject
Environment="PATH=/root/openvpn/vpnapiproject/vpnapiprojectenv/bin"
ExecStart=/root/openvpn/vpnapiproject/vpnapiprojectenv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 wsgi:app

[Install]
WantedBy=multi-user.target
EOF
echo "run vpnservice"
systemctl daemon-reload
systemctl start vpnservice
systemctl enable vpnservice
#systemctl status vpnservice
#echo "/etc/nginx/sites-available/vpnapiproject"
#touch /etc/nginx/sites-available/vpnapiproject
#PUBLICIP=$(curl -s https://api.ipify.org)
#echo "server {
#    listen 80;
#    server_name $PUBLICIP;
#
#    location / {
#        include proxy_params;
#        proxy_pass http://unix:/root/openvpn/vpnapiproject/vpnapiproject.sock;
#    }
#}"
#ln -s /etc/nginx/sites-available/vpnapiproject /etc/nginx/sites-enabled
#echo "edit nginx config"
#rm /etc/nginx/nginx.conf
#touch /etc/nginx/nginx.conf
#echo "user root;
#worker_processes auto;
#pid /run/nginx.pid;
#include /etc/nginx/modules-enabled/*.conf;
#
#events {
#	worker_connections 768;
#	# multi_accept on;
#}
#
#http {
#
#	##
#	# Basic Settings
#	##
#
#	sendfile on;
#	tcp_nopush on;
#	tcp_nodelay on;
#	keepalive_timeout 65;
#	types_hash_max_size 2048;
#	# server_tokens off;
#
#	# server_names_hash_bucket_size 64;
#	# server_name_in_redirect off;
#
#	include /etc/nginx/mime.types;
#	default_type application/octet-stream;
#
#	##
#	# SSL Settings
#	##
#
#	ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3; # Dropping SSLv3, ref: POODLE
#	ssl_prefer_server_ciphers on;
#
#	##
#	# Logging Settings
#	##
#
#	access_log /var/log/nginx/access.log;
#	error_log /var/log/nginx/error.log;
#
#	##
#	# Gzip Settings
#	##
#
#	gzip on;
#
#	# gzip_vary on;
#	# gzip_proxied any;
#	# gzip_comp_level 6;
#	# gzip_buffers 16 8k;
#	# gzip_http_version 1.1;
#	# gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
#
#	##
#	# Virtual Host Configs
#	##
#
#	include /etc/nginx/conf.d/*.conf;
#	include /etc/nginx/sites-enabled/*;
#}
#
#
##mail {
##	# See sample authentication script at:
##	# http://wiki.nginx.org/ImapAuthenticateWithApachePhpScript
##
##	# auth_http localhost/auth.php;
##	# pop3_capabilities \"TOP\" \"USER\";
##	# imap_capabilities \"IMAP4rev1\" \"UIDPLUS\";
##
##	server {
##		listen     localhost:110;
##		protocol   pop3;
##		proxy      on;
##	}
##
##	server {
##		listen     localhost:143;
##		protocol   imap;
##		proxy      on;
##	}
##}" >>/etc/nginx/nginx.conf
#nginx -t
#ufw allow 'Nginx Full'
##cd /root/openvpn/vpnapiproject/ || return
##source vpnapiprojectenv/bin/activate
##pip install pycrypto
##deactivate
##systemctl restart vpnservice
#rm /root/nginx/sites-enabled/default
#systemctl restart nginx
systemctl status vpnservice
exit
