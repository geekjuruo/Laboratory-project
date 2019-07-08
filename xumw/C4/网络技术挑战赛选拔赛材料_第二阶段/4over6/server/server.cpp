#include <iostream>
#include <cstdio>
#include <cstring>
#include "4over6vpn.hpp"

using namespace std;

#define PORTS 4
int main(){
    Tun_VPN::Sync_Mutex();
    Tun_VPN::initListenEpollFd(MAX_THREADS);
    Tun_VPN::initServerFdPool(AF_INET6,"5678",LISTENQ);
    system("iptables -F");
    system("iptables -t nat -F");
    system("echo \"1\" > /proc/sys/net/ipv4/ip_forward");
    system("iptables -A FORWARD -j ACCEPT");
    system("iptables -t nat -A POSTROUTING  -s 10.0.0.0/8 -j MASQUERADE");
    int i;
    for(i=0; i < PORTS - 1; i++) {
        if(fork() == 0){
            break;
        }
    }
    assert(!Tun_VPN::singletonCreated());
    char addr[100];
    snprintf(addr,100,"10.0.%d.%d",i,i+3);
    Tun_VPN* vpn = Tun_VPN::getVPN(addr, i);
    vpn->start();
}