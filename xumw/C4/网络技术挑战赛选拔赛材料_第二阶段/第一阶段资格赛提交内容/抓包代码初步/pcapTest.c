#include <pcap.h>
#include <time.h>
#include <netinet/in.h>

typedef struct eth_hdr {
    u_char dst_mac[6];
    u_char src_mac[6];
    u_short eth_type;
}eth_hdr;
eth_hdr *ethernet;

typedef struct ip_hdr {
    int version:4;
    int header_len:4;
    u_char tos:8;
    int total_len:16;
    int ident:16;
    int flags:16;
    u_char ttl:8;
    u_char protocol:8;
    int checksum:16;
    u_char sourceIP[4];
    u_char destIP[4];
}ip_hdr;
ip_hdr *ip;

typedef struct tcp_hdr {
    u_short sport;
    u_short dport;
    u_int seq;
    u_int ack;
    u_char head_len;
    u_char flags;
    u_short wind_size;
    u_short check_sum;
    u_short urg_ptr;
}tcp_hdr;
tcp_hdr *tcp;

typedef struct udp_hdr {
    u_short sport;
    u_short dport;
    u_short tot_len;
    u_short check_sum;
}udp_hdr;
udp_hdr *udp;

void pcap_callback(unsigned char * arg,const struct pcap_pkthdr *packet_header,const unsigned char *packet_content){
    //打印数据：
//    for(int i=0;i<packet_header->caplen;i++){
//        printf(" %02x",packet_content[i]);
//        if((i+1)%16==0){ printf("\n"); }
//    }

    u_int eth_len=sizeof(struct eth_hdr);
    u_int ip_len=sizeof(struct ip_hdr);
    u_int tcp_len=sizeof(struct tcp_hdr);
    u_int udp_len=sizeof(struct udp_hdr);
    printf("analyse information:\n\n");
    static int id=1;
    printf("id=%d\n",id++);

    printf("Packet length : %d\n",packet_header->len);
    printf("Number of bytes : %d\n",packet_header->caplen);
    printf("Received time : %s\n",ctime((const time_t*)&packet_header->ts.tv_sec));
    printf("ethernet header information:\n");
    ethernet=(eth_hdr *)packet_content;
    printf("src_mac : %02x-%02x-%02x-%02x-%02x-%02x\n",ethernet->src_mac[0],ethernet->src_mac[1],ethernet->src_mac[2],ethernet->src_mac[3],ethernet->src_mac[4],ethernet->src_mac[5]);
    printf("dst_mac : %02x-%02x-%02x-%02x-%02x-%02x\n",ethernet->dst_mac[0],ethernet->dst_mac[1],ethernet->dst_mac[2],ethernet->dst_mac[3],ethernet->dst_mac[4],ethernet->dst_mac[5]);
    printf("ethernet type : %u\n",ethernet->eth_type);
    if(ntohs(ethernet->eth_type)==0x0800){
        printf("IPV4 is used\n");
        printf("IPV4 header information:\n");
        ip=(ip_hdr*)(packet_content+eth_len);
        printf("source ip : %d.%d.%d.%d\n",ip->sourceIP[0],ip->sourceIP[1],ip->sourceIP[2],ip->sourceIP[3]);
        printf("dest ip : %d.%d.%d.%d\n",ip->destIP[0],ip->destIP[1],ip->destIP[2],ip->destIP[3]);
        if(ip->protocol==6){
            printf("tcp is used:\n");
            tcp=(tcp_hdr*)(packet_content+eth_len+ip_len);
            printf("tcp source port : %u\n",tcp->sport);
            printf("tcp dest port : %u\n",tcp->dport);
        }
        else if(ip->protocol==17){
            printf("udp is used:\n");
            udp=(udp_hdr*)(packet_content+eth_len+ip_len);
            printf("udp source port : %u\n",udp->sport);
            printf("udp dest port : %u\n",udp->dport);
        }
        else {
            printf("other transport protocol is used\n");
        }
    }
    else {
        printf("ipv6 is used\n");
    }
    printf("------------------done-------------------\n");
    printf("\n\n");
}

int main(int argc,char** argv){
    char* device=argv[1];   //命令行参数方式传递网卡名称
    char errbuf[1024];
    pcap_t *pcap_handle=pcap_open_live(device,65535,1,0,errbuf);

    if(pcap_handle==NULL){
        printf("%s\n",errbuf);
        return 0;
    }
    printf("Successfully Captured %s.\n",device);

    struct bpf_program filter;
    pcap_compile(pcap_handle,&filter,"tcp and greater 200",1,0);
    pcap_setfilter(pcap_handle,&filter);

    printf("---------packet--------\n");
    int id=0;//传入回调函数记录ID
    if(pcap_loop(pcap_handle,100,pcap_callback,(unsigned char *)&id)<0){//接收十个数据包
        printf("error\n");
        return 0;
    }
    pcap_close(pcap_handle);
}
