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

if __name__=="__main__":
    f = open('../../../pcaptest_20190516/0.pcap', 'rb')
    pcap = dpkt.pcap.Reader(f)
    flows={}    #存放流对象的字典，key为元组 (源端口,目的地址,目的端口)，value为当前三元组下的所有包
    index = 0
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
            flows[triple] = []
            flows[triple].append(index)
            validPacketNum += 1
        else:
            flows[triple].append(index)
            validPacketNum += 1

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