#!/bin/bash

systemctl stop openvpn@server.service
sleep 1
systemctl start openvpn@server.service
echo "reset done"