* unix_secs:%tsr

* unix_nsecs:%ter

* sysUpTime:%trr   

* exaddr: %ra （nfdump中处理v6是用数组存放的，不知该如何处理）

* srcaddr: %sa (v6同理)

* dstaddr:%da（v6同理）
* nexthop:%nh（v6同理）
* input: %in
* output:%out
* dPkts:%ipkt
* dOctets:%ibyt
* First:%tsr ??? 
* Last:%ter ???
* srcport: %sp
* dstport: %dp
* prot: %pr
* tos: %tos
* tcp_flags: %flg
* pad: ??? 
* engine_type: %eng
* engine_id: %eng
* src_mask: %smk
* dst_mask: %dmk
* src_as: %sas
* dst_as: %das



Ipv4:nfdump -r nfcapd.201903192105 -o "fmt: %ra" >> test.txt

Ipv6:nfdump -r nfcapd.201903261110 -o "fmt: %sa" -6  >> test.txt

