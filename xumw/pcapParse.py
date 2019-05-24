import dpkt
import socket
import scapy
from scapy.all import *
from scapy.utils import PcapReader
f = open('./pcaptest_20190516/0.pcap', 'rb')
pcap = dpkt.pcap.Reader(f)


def inet_to_str(inet):
    try:
        return socket.inet_ntop(socket.AF_INET,inet)
    except:
        return socket.inet_ntop(socket.AF_INET6,inet)

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


print("NO")
