#!/bin/bash
apt update
yes | apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
yes | apt-get install python3-pip python3-dev nginx
yes | apt install python3-venv
pip install psutil
chmod 777 -Rv /var/log/openvpn/status.log
cd /etc/openvpn || return
wget https://raw.githubusercontent.com/huongnv251291/easyrsa/main/count_user/countuser.py -O /etc/openvpn/countuser.py
chmod 777 -Rv /etc/openvpn/countuser.py
touch /etc/openvpn/countuser.sh
chmod +x /etc/openvpn/countuser.sh
echo "#!/bin/bash
python3 -i  /etc/openvpn/countuser.py" >>/etc/openvpn/countuser.sh
cat >/etc/systemd/system/countuser.service <<EOF
[Unit]
Description=CountUser Service

[Service]
ExecStart=/etc/openvpn/countuser.sh

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable countuser
systemctl start countuser
cd
mkdir -p /root/vpnapiproject
cd /root/vpnapiproject/ || return
python3 -m venv vpnapiprojectenv
set -e
source /root/vpnapiproject/vpnapiprojectenv/bin/activate
pip install wheel
pip install gunicorn flask
pip install pycrypto
echo "create file api"
cd /root/vpnapiproject/ || return
wget https://raw.githubusercontent.com/huongnv251291/easyrsa/main/api/api.py -O /root/vpnapiproject/api.py
chmod 777 /root/vpnapiproject/api.py
ufw allow 5000
echo "create file wsgi"
touch /root/vpnapiproject/wsgi.py
echo "from api import app

if __name__ == \"__main__\":
    app.run()" >>/root/vpnapiproject/wsgi.py
deactivate
echo "create file vpnservice"
cat >/etc/systemd/system/vpnservice.service <<EOF
[Unit]
Description=Gunicorn instance to server vpnservice
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/root/vpnapiproject
Environment="PATH=/root/vpnapiproject/vpnapiprojectenv/bin"
ExecStart=/root/vpnapiproject/vpnapiprojectenv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 wsgi:app

[Install]
WantedBy=multi-user.target
EOF
echo "run vpnservice"
systemctl daemon-reload
systemctl start vpnservice
systemctl enable vpnservice
systemctl status vpnservice
exit
