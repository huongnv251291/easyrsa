import base64
import json
import multiprocessing
import os
import time
from os.path import exists

import requests

if __name__ == "__main__":
    listFile = ['E://server_gate_live.json', 'E://server_other_live.json']
    listData = []
    allData = None
    for file in listFile:
        my_file_handle = open(file)
        data = json.load(my_file_handle)
        print(len(data))
        listData = listData + data
    print(len(listData))
    result_data = {
        'data': listData,
        }
    print(result_data)
