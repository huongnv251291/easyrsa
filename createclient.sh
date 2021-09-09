#!/bin/bash
# shellcheck disable=SC1091,SC2164,SC2034,SC1072,SC1073,SC1009

while getopts "u:p:" opt; do
  case "$opt" in
  u) CLIENT="$OPTARG" ;;
  p) PASS="$OPTARG" ;;
  esac
done
if [ -z "$CLIENT" ]; then
  echo ""
  echo "name client can't empty"
  echo ""
  exit
fi
CLIENTEXISTS=$(tail -n +2 /etc/openvpn/easy-rsa/pki/index.txt | grep -c -E "/CN=$CLIENT\$")
if [[ $CLIENTEXISTS == '1' ]]; then
  echo ""
  echo "The specified client CN was already found in easy-rsa, please choose another name."
  exit
else
  cd /etc/openvpn/easy-rsa/ || return
fi
if [ -z "$PASS" ]; then
  echo "" | ./easyrsa build-client-full "$CLIENT" nopass
else
  (
    echo $PASS
    echo $PASS
  ) | ./easyrsa build-client-full "$CLIENT"
fi
if [ -e "/home/${CLIENT}" ]; then
  # if $1 is a user name
  homeDir="/home/${CLIENT}"
elif [ "${SUDO_USER}" ]; then
  # if not, use SUDO_USER
  if [ "${SUDO_USER}" == "root" ]; then
    # If running sudo as root
    homeDir="/root"
  else
    homeDir="/home/${SUDO_USER}"
  fi
else
  # if not SUDO_USER, use /root
  homeDir="/root"
fi
# Determine if we use tls-auth or tls-crypt
if grep -qs "^tls-crypt" /etc/openvpn/server.conf; then
  TLS_SIG="1"
elif grep -qs "^tls-auth" /etc/openvpn/server.conf; then
  TLS_SIG="2"
fi
# Generates the custom client.ovpn
cp /etc/openvpn/client-template.txt "$homeDir/$CLIENT.ovpn"
{
  echo "<ca>"
  cat "/etc/openvpn/easy-rsa/pki/ca.crt"
  echo "</ca>"

  echo "<cert>"
  awk '/BEGIN/,/END/' "/etc/openvpn/easy-rsa/pki/issued/$CLIENT.crt"
  echo "</cert>"

  echo "<key>"
  cat "/etc/openvpn/easy-rsa/pki/private/$CLIENT.key"
  echo "</key>"

  case $TLS_SIG in
  1)
    echo "<tls-crypt>"
    cat /etc/openvpn/tls-crypt.key
    echo "</tls-crypt>"
    ;;
  2)
    echo "key-direction 1"
    echo "<tls-auth>"
    cat /etc/openvpn/tls-auth.key
    echo "</tls-auth>"
    ;;
  esac
} >>"$homeDir/$CLIENT.ovpn"
echo "$homeDir/$CLIENT.ovpn"
exit 0
