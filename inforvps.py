#!/usr/bin/env python
from tqdm import tqdm
from time import sleep
import psutil

print("gives a single float value :")
print(psutil.cpu_percent())
print("gives an object with many fields :")
print(psutil.virtual_memory())
print("you can have the percentage of used  :")
var = psutil.virtual_memory().percent
print(var)
print("you can calculate percentage of available memory  :")
print(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total)
print(psutil.net_io_counters(pernic=False))
