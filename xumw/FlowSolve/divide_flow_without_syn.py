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
    flows_feature = []      # 存放流对象特征的列表，列表套列表，里面的每一个列表代表每一个流的特征
    flows_label = []        # 存放流对象应用类型标签的列表
    index = 0
    for i in range(0, 30):
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
        f.close()
        print(index)
        print("finish read " + str(i) + " pcap")

    # df = pd.DataFrame(flows)
    # df.to_csv('flows.csv')
    flow_index = 0
    for key, flowGroup in flows.items():
        print(key)
        print(flowGroup)
        feature = []#每个流的特征列表
        
        feature.append(len(flowGroup)) # 特征 包总数
        
        keys = list(flowGroup.keys())
        duration = flowGroup[keys[len(keys)-1]][0] - flowGroup[keys[0]][0]
        feature.append(duration) # 特征 连接的持续时间 若只有一个包 则为0
        
        packetLenMean = 0 # 特征 包的平均长度
        payloadLenMean = 0 # 特征 有效负载平均长度
        for index, item in flowGroup.items():
            packetLenMean += item[2]
            payloadLenMean += item[3]
        packetLenMean = packetLenMean / len(keys)
        payloadLenMean = payloadLenMean / len(keys)
        feature.append(packetLenMean)
        feature.append(payloadLenMean)

        timeGapMean = 0 # 特征 包之间平均间隔 若只有一个包 则为0
        if (len(keys) != 1):
            for index in range(0, len(keys) - 1):
                timeGapMean += flowGroup[keys[index + 1]][0] - flowGroup[keys[index]][0]
            timeGapMean = timeGapMean / (len(keys) - 1)
        feature.append(timeGapMean)

        flows_feature.append(feature)
    

    print(flows_feature)
    featureName=['PacketTotalNum','DurationTime','PacketLenMean', 'PayloadLenMean', 'TimeGapMean']
    df=pd.DataFrame(columns=featureName,data=flows_feature)
    df.to_csv('flows_feature.csv')