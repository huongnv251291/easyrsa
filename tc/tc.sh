#!/bin/bash
TC=$(which tc)

interface="$dev"
interface_speed="100mbit"
client_ip="$trusted_ip"
client_ip_vpn="$ifconfig_pool_remote_ip"
download_limit="512kbit"
upload_limit="10mbit"
handle=`echo "$client_ip_vpn" | cut -d. -f4`

function start_tc {
  tc qdisc show dev $interface | grep -q "qdisc pfifo_fast 0"
  [ "$?" -gt "0" ] && tc qdisc del dev $interface root; sleep 1

  $TC qdisc add dev $interface root handle 1: htb default 30
  $TC class add dev $interface parent 1: classid 1:1 htb rate $interface_speed burst 15k
  $TC class add dev $interface parent 1:1 classid 1:10 htb rate $download_limit burst 15k
  $TC class add dev $interface parent 1:1 classid 1:20 htb rate $upload_limit burst 15k
  $TC qdisc add dev $interface parent 1:10 handle 10: sfq perturb 10
  $TC qdisc add dev $interface parent 1:20 handle 20: sfq perturb 10
}

function stop_tc {
  tc qdisc show dev $interface | grep -q "qdisc pfifo_fast 0"
  [ "$?" -gt "0" ] && tc qdisc del dev $interface root
}

function filter_add {
  $TC filter add dev $interface protocol ip handle ::${handle} parent 1: prio 1 u32 match ip ${1} ${2}/32 flowid 1:${3}
}

function filter_del {
  $TC filter del dev $interface protocol ip handle 800::${handle} parent 1: prio 1 u32
}

function ip_add {
  filter_add "dst" $client_ip_vpn "10"
  filter_add "src" $client_ip_vpn "20"
}

function ip_del {
  filter_del
  filter_del
}

if [ "$script_type" == "up" ]; then
        start_tc
elif [ "$script_type" == "down" ]; then
