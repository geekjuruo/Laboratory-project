# -*- encoding:utf-8
import dpkt
import socket
import scapy
from scapy.all import *
from scapy.utils import PcapReader
import numpy as np 
import pandas as pd
import random
import csv
import math
from scipy.sparse import csr_matrix, hstack
from sklearn import svm
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection  import train_test_split
from sklearn.naive_bayes import BernoulliNB


f = open('../../../pcaptest_20190516/0.pcap', 'rb')
pcap = dpkt.pcap.Reader(f)


def inet_to_str(inet):
    try:
        return socket.inet_ntop(socket.AF_INET,inet)
    except:
        return socket.inet_ntop(socket.AF_INET6,inet)

port_list = []
num = 0
for ts,buf in pcap:
    num += 1
    print(num)
    ethData = dpkt.ethernet.Ethernet(buf) # 物理层
    ipData = ethData.data # 网络层
    transData = ipData.data # 传输层
    appData = transData.data # 应用层
    
    ip_src = inet_to_str(ipData.src)
    ip_dst = inet_to_str(ipData.dst)
    print( "ip_src", ip_src)
    print("ip_dsr",ip_dst)
    print("src_port", transData.sport)
    print("dst_port", transData.dport)
    port_list.append(transData.dport) # 通过dst port分析

print("--------------------------------------")
print("pcap dst port type num:", len(port_list))

port_official_csv = pd.read_csv("./service-names-port-numbers.csv")

port_official_useful = {}
for i in range(0, len(port_official_csv)):
    if (port_official_csv['Service Name'][i] is not np.nan) and  (port_official_csv['Port Number'][i] is not np.nan):
        port_official_useful[port_official_csv['Port Number'][i]] = port_official_csv['Service Name'][i]

print("--------------------------------------")
print("official useful port number:",len(port_official_useful))

app_list = []
for i in range(0, len(port_list)):
	x = str(port_list[i])
	if (x in port_official_useful.keys()):
		app_list.append(port_official_useful[x]) 
	else:
		app_list.append('unknown')

print("--------------------------------------")
print("label set num:",len(app_list))

for i in range(0, len(app_list)):
	print(port_list[i], app_list[i])

portTrain, portTest, appTrain, appTest = train_test_split(port_list, app_list, test_size = 0.2, random_state = 42)

print(len(portTrain))
print(len(portTest))
print(len(appTrain))
print(len(appTest))