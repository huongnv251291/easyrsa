#!/bin/bash

udp1194=21 #tun0
main=eth0
echo tc qdisc del dev $main root >>tcrules
echo tc qdisc del dev tun0 root >>tcrules
echo tc qdisc add dev $main root handle 1: htb >>tcrules
echo tc qdisc add dev tun0 root handle 1: htb >>tcrules
for i in {1..254}
do
##udp1194
echo iptables -I FORWARD -s 10.$udp1194.$id.$i -j MARK --set-mark 1$i >> mark
echo iptables -I FORWARD -d 10.$udp1194.$id.$i -j MARK --set-mark 1$i >> mark
echo tc class add dev eth0 parent 1:1 classid 1:1$i htb rate 1mbit ceil 1mbit >> tcrules
echo tc qdisc add dev eth0 parent 1:1$i sfq perturb 10 >> tcrules
echo tc filter add dev eth0 protocol ip parent 1: prio 1 handle 1$i fw flowid 1:1$i >> tcrules
echo tc class add dev tun0 parent 1:1 classid 1:1$i htb rate 1mbit ceil 1mbit >> tcrules
echo tc qdisc add dev tun0 parent 1:1$i sfq perturb 10 >> tcrules
echo tc filter add dev tun0 protocol ip parent 1: prio 1 handle 1$i fw flowid 1:1$i >> tcrules
done