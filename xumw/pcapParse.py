import dpkt
import socket
f = open('./0.pcap', 'rb')
pcap = dpkt.pcap.Reader(f)


def inet_to_str(inet):
    try:
        return socket.inet_ntop(socket.AF_INET,inet)
    except:
        return socket.inet_ntop(socket.AF_INET6,inet)

num = 0
for ts,buf in pcap:
    num += 1
    eth = dpkt.ethernet.Ethernet(buf)
    ip_src = inet_to_str(eth.data.src)
    ip_dst = inet_to_str(eth.data.dst)
    print(num, "ip_src", ip_src)
    print("ip_dsr",ip_dst)

