#!/bin/bash

statedir=/tmp/

function bwlimit-enable() {
  echo "bwlimit-enable start"
  ip=$1
  user=$2
  echo "ip : $ip"
  echo "user : $user"
  # Disable if already enabled.
  bwlimit-disable $ip

  # Find unique classid.
  if [ -f $statedir/$ip.classid ]; then
    # Reuse this IP's classid
    classid=$(cat $statedir/$ip.classid)
  else
    if [ -f $statedir/last_classid ]; then
      classid=$(cat $statedir/last_classid)
      classid=$((classid + 1))
    else
      classid=1
    fi
    echo $classid >$statedir/last_classid
  fi
  echo "classid : $classid"
  # Find this user's bandwidth limit
  # downrate: from VPN server to the client
  # uprate: from client to the VPN server

  downrate=5mbit
  uprate=5mbit
  # Limit traffic from VPN server to client
  echo "tc class add dev $dev parent 1: classid 1:$classid htb rate $downrate"
  sudo tc class add dev $dev parent 1: classid 1:$classid htb rate $downrate
  echo "tc filter add dev $dev protocol all parent 1:0 prio 1 u32 match ip dst $ip/32 flowid 1:$classid"
  sudo tc filter add dev $dev protocol all parent 1:0 prio 1 u32 match ip dst $ip/32 flowid 1:$classid

  # Limit traffic from client to VPN server
  echo "tc filter add dev $dev parent ffff: protocol all prio 1 u32 match ip src $ip/32 police rate $uprate burst 80k drop flowid :$classid"
  sudo tc filter add dev $dev parent ffff: protocol all prio 1 u32 match ip src $ip/32 police rate $uprate burst 80k drop flowid :$classid

  # Store classid and dev for further use.
  echo $classid >$statedir/$ip.classid
  echo $dev >$statedir/$ip.dev
  echo "bwlimit-enable done"
}

function bwlimit-disable() {
  echo "bwlimit-disable start"
  ip=$1
  echo "IP : $ip"
  if [ ! -f $statedir/$ip.classid ]; then
    return
  fi
  if [ ! -f $statedir/$ip.dev ]; then
    return
  fi

  classid=$(cat $statedir/$ip.classid)
  echo "classid : $classid"
  dev=$(cat $statedir/$ip.dev)
  echo "dev : $dev"
  echo "tc filter del dev $dev protocol all parent 1:0 prio 1 u32 match ip dst $ip/32"
  tc filter del dev $dev protocol all parent 1:0 prio 1 u32 match ip dst $ip/32
  echo "tc class del dev $dev classid 1:$classid"
  tc class del dev $dev classid 1:$classid
  echo "tc filter del dev $dev parent ffff: protocol all prio 1 u32 match ip src $ip/32"
  tc filter del dev $dev parent ffff: protocol all prio 1 u32 match ip src $ip/32

  # Remove .dev but keep .classid so it can be reused.
  rm $statedir/$ip.dev
  echo "bwlimit-disable done"
}

# Make sure queueing discipline is enabled.
echo "start : $1  -   $2   -   $3"
tc qdisc add dev $dev root handle 1: htb 2>/dev/null || /bin/true
tc qdisc add dev $dev handle ffff: ingress 2>/dev/null || /bin/true
echo "clear dev done"
case "$1" in
add | update)
  bwlimit-enable $2 $3
  ;;
delete)
  bwlimit-disable $2
  ;;
*)
  echo "$0: unknown operation [$1]" >&2
  exit 1
  ;;
esac

exit 0
