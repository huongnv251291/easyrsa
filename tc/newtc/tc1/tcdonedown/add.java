#!/bin/bash
TC=$(which tc)

interface="$dev"
interface_speed="100mbit"
client_ip="$trusted_ip"
client_ip_vpn="$ifconfig_pool_remote_ip"
download_limit="512kbit"
upload_limit="512kbit"
handle=$(echo "$client_ip_vpn" | cut -d. -f4)
echo "interface : $interface"
echo "interface_speed : $interface_speed"
echo "client_ip : $client_ip"
echo "client_ip_vpn : $client_ip_vpn"
echo "download_limit : $download_limit"
echo "upload_limit : $upload_limit"
function start_tc {
  echo "start_tc : star"
  tc qdisc show dev $interface | grep -q "qdisc pfifo_fast 0"
  [ "$?" -gt "0" ] && tc qdisc del dev $interface root
  sleep 1

  $TC qdisc add dev $interface root handle 1: htb default 30
  $TC class add dev $interface parent 1: classid 1:1 htb rate $interface_speed burst 15k
  $TC class add dev $interface parent 1:1 classid 1:10 htb rate $download_limit burst 15k
  $TC class add dev $interface parent 1:1 classid 1:20 htb rate $upload_limit burst 15k
  $TC qdisc add dev $interface parent 1:10 handle 10: sfq perturb 10
  $TC qdisc add dev $interface parent 1:20 handle 20: sfq perturb 10
  echo "start_tc : end"
}

function stop_tc {
  echo "stop_tc : start"
  tc qdisc show dev $interface | grep -q "qdisc pfifo_fast 0"
  [ "$?" -gt "0" ] && tc qdisc del dev $interface root
  echo "stop_tc : end"
}

function filter_add {
  echo "filter_add : start"
  echo "handle : ${handle}"
  echo "sudo tc filter add dev $interface protocol ip handle ::${handle} parent 1: prio 1 u32 match ip ${1} ${2}/32 flowid 1:${3}"
  sudo tc filter add dev $interface protocol ip handle ::${handle} parent 1: prio 1 u32 match ip ${1} ${2}/32 flowid 1:${3}
  echo "filter_add : end"
}

function filter_del {
  echo "filter_del : start"
  echo "handle : ${handle}"
  echo "tc filter del dev $interface protocol ip handle 800::${handle} parent 1: prio 1 u32"
  sudo tc filter del dev $interface protocol ip handle 800::${handle} parent 1: prio 1 u32
  echo "filter_del : end"
}

function ip_add {
  echo "ip_add : start"
  #  echo "filter_add dst $client_ip_vpn 10"
  #  filter_add "dst" $client_ip_vpn "10"
  echo "sudo tc filter add dev $interface protocol ip handle ::${handle} parent 1: prio 1 u32 match ip dst $client_ip_vpn/32 flowid 1:10"
  sudo tc filter add dev $interface protocol ip handle ::2 parent 1: prio 1 u32 match ip dst $client_ip_vpn/32 flowid 1:10
  echo "sudo tc filter add dev $interface protocol ip handle ::${handle} parent 1: prio 1 u32 match ip src $client_ip_vpn/32 flowid 1:20"
  sudo tc filter add dev $interface protocol ip handle ::2 parent 1: prio 1 u32 match ip src $client_ip_vpn/32 flowid 1:10
  #  echo "filter_add src $client_ip_vpn 20"
  #  filter_add "src" $client_ip_vpn "10"
  echo "ip_add : end"
}

function ip_del {
  echo "ip_del : start"
  filter_del
  filter_del
  echo "ip_del : end"
}
echo "script_type : $script_type"
if [ "$script_type" == "up" ]; then
  start_tc
elif [ "$script_type" == "down" ]; then
  stop_tc
elif [ "$script_type" == "client-connect" ]; then
  ip_add
elif [ "$script_type" == "client-disconnect" ]; then
  ip_del
fi
