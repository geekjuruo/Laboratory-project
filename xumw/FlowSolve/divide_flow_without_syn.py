#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dpkt
import socket

import numpy as np
import pandas as pd

from flow import *

def inet_to_str(inet):
    try:
        return socket.inet_ntop(socket.AF_INET,inet)
    except:
        return socket.inet_ntop(socket.AF_INET6,inet)


validPacketNum = 0

# 每条流的：
# 1、包总数
# 2、连接的持续时间（仅对有起止报文的连接）
# 3、包的平均长度 或 负载平均长度
# 4、包之间平均间隔时间

if __name__=="__main__":
    flows={}    #存放流对象的字典，key为元组 (源端口,目的地址,目的端口)，value为当前三元组下的所有包
    index = 0
    for i in range(0, 1):
        print("start read " + str(i) + " pcap")
        pcap_path = '../../../pcaptest_20190516/' + str(i) + '.pcap'
        f = open(pcap_path, 'rb')
        pcap = dpkt.pcap.Reader(f)
        for ts, buf in pcap:
            index += 1
            ethData = dpkt.ethernet.Ethernet(buf)  # 物理层
            ipData = ethData.data  # 网络层
            if not isinstance(ipData.data, dpkt.tcp.TCP): #流分析只需要TCP，UDP中不存在流的概念
                continue
            transData = ipData.data  # 传输层
            appData = transData.data  # 应用层

            ip_dst = inet_to_str(ipData.dst)
            port_src=transData.sport
            port_dst=transData.dport
            triple=(port_src, ip_dst, port_dst)
            if triple not in flows:
                flows[triple] = {}         # 流集合为一个字典结构，每一条流本身是一个字典结构
                flows[triple][index] = []  # 每条流的每个包是一个列表结构，用以存放该包的特征
                flows[triple][index].append(ts) # 特征 包时间戳
                flows[triple][index].append(port_dst) # 特征 端口号
                flows[triple][index].append(len(buf)) # 包长度
                flows[triple][index].append(len(appData)) # 有效负载长度

                validPacketNum += 1
            else:
                flows[triple][index] = []
                flows[triple][index].append(ts) # 特征 包时间戳
                flows[triple][index].append(port_dst) # 特征 端口号
                flows[triple][index].append(len(buf)) # 特征 包长度
                flows[triple][index].append(len(appData)) # 特征 有效负载长度
                validPacketNum += 1
        print(index)
        print("finish read " + str(i) + " pcap")

    # df = pd.DataFrame(flows)
    # df.to_csv('flows.csv')

    TotalNum = 0
    print("Total {} triples.".format(flows.__len__()))
    print("Total {} valid packets.".format(validPacketNum))
    for key, flowGroup in flows.items():
        TotalNum += 1
        if TotalNum >= 10:
            break
        if len(flowGroup) != 1:
            print("packet list", flowGroup)

    print(validPacketNum)
    
    f.close()