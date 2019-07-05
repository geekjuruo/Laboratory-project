import numpy as np
import pandas as pd
import csv
import dpkt
import socket

# 进行流特征统计分析

def inet_to_str(inet):
    try:
        return socket.inet_ntop(socket.AF_INET,inet)
    except:
        return socket.inet_ntop(socket.AF_INET6,inet)

pd.set_option('precision', 20) #设置精度
pd.set_option('display.float_format', lambda x: '%.20f' % x) #为了直观的显示数字，不采用科学计数法



if __name__=="__main__":
    flows={}    #存放流对象的字典，key为元组 (源端口,目的地址,目的端口)，value为当前三元组下的所有包
    flows_feature = []      # 存放流对象特征的列表，列表套列表，里面的每一个列表代表每一个流的特征
    flows_label = []        # 存放流对象应用类型标签的列表
    index = 0

    flows_label = pd.read_csv('./flows_label.csv')
    flows_feature = pd.read_csv('./flows_feature.csv')

    tcp_num = 0
    udp_num = 0

    unknown_label_num = 0
    known_label_num = 0
    flows_label_list = []
    for item in flows_label['label']:
        if item not in flows_label_list:
            flows_label_list.append(item)
        if item == 'unknown':
            unknown_label_num += 1
        else:
            known_label_num += 1
    print("label kinds ", len(flows_label_list))
    print("unknown label num ", unknown_label_num)
    print("known label num ", known_label_num)

    packet_total_num = pd.DataFrame(flows_feature['PacketTotalNum'])
    print(packet_total_num.describe())

    duration_time = pd.DataFrame(flows_feature['DurationTime'])
    print(duration_time.describe())

    packet_len_mean = pd.DataFrame(flows_feature['PacketLenMean'])
    print(packet_len_mean.describe())

    payload_len_mean = pd.DataFrame(flows_feature['PayloadLenMean'])
    print(payload_len_mean.describe())

    time_gap_mean = pd.DataFrame(flows_feature['TimeGapMean'])
    print(time_gap_mean.describe())

    for i in range(0, 155):
        print("start read " + str(i) + " pcap")
        pcap_path = '/data/liyinghui/' + str(i) + '.pcap'
        f = open(pcap_path, 'rb')
        pcap = dpkt.pcap.Reader(f)
        for ts, buf in pcap:
            index += 1
            ethData = dpkt.ethernet.Ethernet(buf)  # 物理层
            ipData = ethData.data  # 网络层
            if not isinstance(ipData, bytes):
                if not isinstance(ipData.data, dpkt.tcp.TCP) and not isinstance(ipData.data, dpkt.udp.UDP): #流分析只需要TCP，UDP中不存在流的概念
                    continue
                if isinstance(ipData.data, dpkt.tcp.TCP):
                    tcp_num += 1
                if isinstance(ipData.data, dpkt.udp.UDP):
                    udp_num += 1
                transData = ipData.data  # 传输层
                appData = transData.data  # 应用层

        f.close()
        print(index)
        print("finish read " + str(i) + " pcap")

    print("tcp num ", tcp_num)
    print("udp num ", udp_num)


