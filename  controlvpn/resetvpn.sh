#!/bin/bash
systemctl stop openvpn@server
sleep 1
systemctl start openvpn@server
echo "reset done"