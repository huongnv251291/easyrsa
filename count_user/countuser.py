#!/usr/bin/env python3
import json
import re
from threading import Thread
from time import sleep
import os

import psutil
import requests


class CountUser:
    last_user = 0
    max_current_connection = 0
    vpn_type = 1
    cpu = 0
    ram = 0

    def read_config(self):
        file = open("/etc/openvpn/server.conf", "r")
        for lines in file:
            if re.match("duplicate-cn", lines):
                self.vpn_type = 0
            if lines.startswith("max-clients"):
                self.max_current_connection = lines.split()[1]

    def push_new_vpn_to_dash_broad(self, b, isserverrunning):
        self.read_config()
        r = requests.get("https://ipinfo.io/json")
        data_from_ip_info = json.loads(r.text)
        id_vps = str(data_from_ip_info["ip"]).replace(".", "")
        result_data = {
            'id': id_vps,
            'host_name': "vpn" + str(id_vps),
            'ip': str(data_from_ip_info["ip"]),
            'current_connection': b,
            'max_connection': self.max_current_connection,
            'city': str(data_from_ip_info["city"]),
            'region': str(data_from_ip_info["region"]),
            'country': str(data_from_ip_info["country"]),
            'vpn_type': self.vpn_type,
            'cpu': self.cpu,
            'ram': self.ram,
            'status_vpn': isserverrunning
        }
        print(result_data)
        requests.post("http://50.116.8.251/api/creatVpn", data=result_data)

    def print_time(self):
        fd = open("/var/log/openvpn/status.log", "r")
        b = 0
        for lines in fd:
            if re.match("ROUTING TABLE", lines):
                b = b - 3
                if b != self.last_user:
                    self.last_user = b
                self.update_new_infor(b, 1)
                break
            else:
                b = b + 1

    def get_cpu(self):
        self.cpu = psutil.cpu_percent(4.5)
        self.ram = int(psutil.virtual_memory().used * 100 / psutil.virtual_memory().total)

    def run(self):
        # self.print_time()
        while True:
            thread = Thread(target=self.get_cpu())
            thread.start()
            sleep(5)
            # file = Path("/var/log/openvpn/status.log")
            # if file.is_file():
            try:
                self.print_time()
                # status = os.system('systemctl is-active openvpn@server')
                # if status == 0:
                #     self.print_time()
                # else:
                #     self.update_new_infor(0, 0)
            except:
                continue
        # else:
        #     break

    def update_new_infor(self, b, isserverrunning):
        r = requests.get("https://api.ipify.org")
        name = r.text.replace(".", "")
        pload = {
            'id': name,
            'current_connection': b,
            'cpu': self.cpu,
            'ram': self.ram,
            'status_vpn': isserverrunning
        }
        path = "http://50.116.8.251/api/updateNumberConnect"
        data = requests.post(path, data=pload)
        data_from_ip_info = json.loads(data.text)
        error = data_from_ip_info["code"]
        if error == 201:
            self.push_new_vpn_to_dash_broad(b, isserverrunning)
        else:
            print(data_from_ip_info)


CountUser().run()
