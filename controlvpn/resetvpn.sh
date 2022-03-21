#!/bin/bash
PATH="$PATH:/usr/bin:/bin"
systemctl stop openvpn@server
sleep 1
systemctl start openvpn@server
echo "reset done"
