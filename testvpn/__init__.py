import json
import multiprocessing
import os
from os.path import exists


def ping(i):
    response = os.popen(f"ping {i['IP']}").read()
    print(response)
    if "Received = 4" in response:
        print(f"UP {i['IP']} Ping Successful")
        return i
    else:
        print(f"DOWN {i['IP']} Ping Unsuccessful")
        return "None"


if __name__ == "__main__":
    listData = []
    my_file_handle = open('C://Users//TOH_Android//Downloads//serverbackup.json')
    data = json.load(my_file_handle)
    num_threads = 2 * multiprocessing.cpu_count()
    with multiprocessing.Pool(num_threads) as pool:
        result = pool.map(ping, [i for i in data])
    for value in result:
        print(value)
        if not str(value).__eq__('None'):
            listData.append(value)
    print("server live :" + str(len(listData)))
    file_exists = exists('E://server_other_live.json')
    print(file_exists)
    if file_exists:
        os.remove('E://server_other_live.json')
    with open('E://server_other_live.json', "w") as outfile:
        outfile.write(json.dumps(listData))
