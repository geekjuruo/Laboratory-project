#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Charles Guo'
# 用握手信息来进行分流

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


if __name__=="__main__":
    f = open('../../../pcaptest_20190516/0.pcap', 'rb')
    pcap = dpkt.pcap.Reader(f)
    flows={}    #存放流对象的字典，key为元组 (源端口,目的地址,目的端口)，value为当前三元组下的所有流
    index = 0   #包index,从1开始记录
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
        if transData.flags & dpkt.tcp.TH_SYN:   #遇到syn包
            if triple not in flows:  # 如果不存在当前三元组的流，则新建新流列表
                flows[triple] = [Flow()] # 创建新的流
                flows[triple][-1].addPacket(index) # 将这个包添加到刚刚创建的流中去
            else:   #若存在当前三元组的流，则
                if flows[triple][-1].status==notEnd:    #若流列表结尾的流没有闭合，
                    flows[triple][-1].addPacket(index)   #则把当前包添加到这个流
                else:                               #若流列表结尾的流闭合
                    flows[triple].append(Flow())    #则新建新流
        elif transData.flags & dpkt.tcp.TH_FIN: #遇到fin包
            if triple in flows:
                if flows[triple][-1].status==notEnd:    #若流列表结尾的流没有闭合，
                    flows[triple][-1].addPacket(index)   #则使该流闭合
                    flows[triple][-1].status=end
                else:                               #若流列表结尾的流闭合
                    pass                            #则忽略该包
        else:           #遇到一般的包
            if triple in flows:
                if flows[triple][-1].status==notEnd:    #若流列表结尾的流没有闭合，
                    flows[triple][-1].addPacket(index)   #则将当前包加入该流中


    TotalNum = 0
    print("Total {} triples.".format(flows.__len__()))
    print("Total {} valid packets.".format(Flow.validPacket))
    for key,flowGroup in flows.items():
        TotalNum += 1
        for flow in flowGroup:
            if TotalNum >= 10:
                break
            if(len(flowGroup[0].packetList) <= 100):
                print("packet list", flowGroup[0].packetList)
    f.close()
