#ifndef TUNVPN_HPP
#define TUNVPN_HPP

#include "utils.hpp"
#include <thread>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <sys/epoll.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <pthread.h>
#include  <sys/stat.h>
#include <errno.h>
#include <unistd.h>
#include <sys/epoll.h>
#include <netdb.h>
#include <string>
#include <vector>
#include <assert.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <linux/if_tun.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <sys/types.h>
#include <linux/if_tun.h>
#include <linux/ip.h>
#include <unistd.h>
#include <netinet/tcp.h>

typedef int (*PFCALLBACL)(struct epoll_event *);
typedef struct EPOLL_DATA_S{
    int epoll_Fd;
    int event_Fd;
    PFCALLBACL pfCallBack;
}Epoll_Data_S;


class Tun_VPN{
    static int serverfd[MAX_THREADS];
    static int serverfd_cnt;
    static int epoll_listenfd;
    static int epoll_recvfd;
    static pthread_mutex_t* mutex;
    static epoll_event* events;
    //using Singleton in multi-thread
    static Tun_VPN* vpn;
    int clientfd;
    int tunfd;
    int index;
    bool busy;
    static Msg fromtun;
    static Msg fromclient;
    in_addr tunAddr;
    time_t recv_time;
    time_t send_time;
    Tun_VPN(char* addr, int index){
        busy = false;
        clientfd = -1;
        tunfd = -1;
        send_time = time(NULL);
        tunAddr = {0};
        inet_aton(addr, &tunAddr);
        this->index = index;

        struct ifreq ifr = {0};
        char buffer[256];
        if((tunfd= open("/dev/net/tun", O_RDWR)) < 0) {
            perror("Cannot open TUN dev");
        }
        ifr.ifr_flags = IFF_TUN | IFF_NO_PI;
        snprintf(ifr.ifr_name,IF_NAMESIZE,"TinyVpn%d",this->index);
        if (ioctl(tunfd, TUNSETIFF, (void *)&ifr) < 0) {
            perror("Cannot initialize TUN device");
            close(tunfd);
        }
        sprintf(buffer,"ip link set dev %s up", ifr.ifr_name);
        system(buffer);
        sprintf(buffer,"ip a add 10.0.%d.1/24 dev %s", index, ifr.ifr_name);
        system(buffer);
        sprintf(buffer,"ip link set dev %s mtu %u", ifr.ifr_name, 1500 - MSG_HEADER);
        system(buffer);

        make_socket_non_blocking(tunfd);
        epoll_ctl_add(epoll_recvfd, tunfd, receive_epoll_event);
    }
    
    static int RecvPkt(int fd, char* buffer, int len){
        int remained = len;
        while(remained > 0){
            ssize_t recvn = read(fd, buffer + len - remained, remained);
            if(recvn == -1){
                usleep(100);
                continue;
            }
            else if(recvn == 0)
                return 0;
            else if(recvn > 0)
                remained -= recvn;
            else
                return -1;
        }
        return len;
    }
    
    int readMsg_from_tun(){
        ssize_t len;
        if((len = read(tunfd, fromtun.data, MAX_DATA_FIELD)) <= 0){
            return len;
        }
        iphdr* tun_iphdr = (struct iphdr*)fromtun.data;
        if(tun_iphdr->version==4) {
            if(tun_iphdr->protocol==1){
                tun_iphdr->saddr = tunAddr.s_addr;
                return write(tunfd, &fromtun.data, len + 5);
            }
            else if(tun_iphdr->daddr == tunAddr.s_addr && busy) {
                fromtun.packet_len = len + 5;
                fromtun.type = REPLY_FOR_CONNECTION;
                return write(clientfd, &fromtun, len + 5);
            }
        }
        return 0;
    }
    
    static int make_socket_non_blocking(int fd){ 
        int flags, s;  
        flags = fcntl (fd, F_GETFL, 0);  
        if(flags == -1){  
            perror ("fcntl");  
            return -1;  
        }  
        flags |= O_NONBLOCK;  
        s = fcntl (fd, F_SETFL, flags);  
        if (s == -1){
            perror ("fcntl");
            return -1;  
        }  
        return 0;  
    }

    int readMsg_from_client(){
        int len = RecvPkt(clientfd, (char*)&fromclient, MSG_HEADER);
        if(len <= 0)
            return -1;
        recv_time = time(NULL);

        if (fromclient.type == REQUEST_FOR_CONNECTION){
            len = RecvPkt(clientfd, fromclient.data, fromclient.packet_len - MSG_HEADER);
            if(len == fromclient.packet_len - 5){
                iphdr *client_iphdr  = (struct iphdr*)fromclient.data;
                if(client_iphdr->version == 4){
                    client_iphdr->saddr = tunAddr.s_addr;
                }
                if(client_iphdr->saddr == tunAddr.s_addr){
                    write(tunfd, fromclient.data, fromclient.packet_len - 5);
                }
            }
            else{
                return -1;
            }
        }
        else if(fromclient.type == REQUEST_FOR_ADDR){
            fromclient.type = REPLY_FOR_ADDR;
            snprintf(fromclient.data, MAX_DATA_FIELD, "%s 0.0.0.0 202.38.120.242 8.8.8.8 202.106.0.20 ", inet_ntoa(tunAddr));
            fromclient.packet_len = strlen(fromclient.data) + 5;
            return write(clientfd, &fromclient, fromclient.packet_len);
        } 
        else if(fromclient.type == HEARTBEATS) {
            printf("beat...\n");
            return 0;
        } 
        return 0;
    }

public:
    void start(){
        while(true){
            if(!busy)
                process_wait_epoll(epoll_listenfd, 5);
            else {
                process_wait_epoll(epoll_recvfd, 1);
            }
            if(time(NULL) - send_time > 20 && busy){
                send_time = time(NULL);
                Msg linked;
                linked.type = HEARTBEATS;
                linked.packet_len = 5;
                write(clientfd, &linked, linked.packet_len);
            }
        }
    }

    void reset(){
        close(tunfd);
        tunfd = -1;
        busy = false;
        close(clientfd);
        clientfd = -1;
        memset(&tunAddr,0,sizeof(tunAddr));
    }

    static bool singletonCreated(){
        return vpn != NULL;
    }

    static Tun_VPN* getVPN(char* addr, int index){
        if(vpn == NULL){
            vpn = new Tun_VPN(addr,index);
        }
        return vpn;
    }

    static void process_wait_epoll(int epollFd, int timeout) {
        int n;
        int i;
        n = epoll_wait(epollFd, events, 100, timeout);
        for (i = 0; i < n; i++) {
            Epoll_Data_S *data = (Epoll_Data_S *)(events[i].data.ptr);
            data->pfCallBack(&(events[i]));
        }
    }

    static int epoll_ctl_add(int epfd, int fd, PFCALLBACL pfCallBack){
        int op = EPOLL_CTL_ADD;
        struct epoll_event ee;
        Epoll_Data_S *data;
        data = (Epoll_Data_S*)malloc(sizeof(Epoll_Data_S));
        if (data == NULL) {
            printf("malloc error");
            return -1;
        }
        data->epoll_Fd = epfd;
        data->event_Fd = fd;
        data->pfCallBack = pfCallBack;
        ee.events = EPOLLIN |  EPOLLHUP;
        ee.data.ptr = (void *)data;
        if (epoll_ctl(epfd, op, fd, &ee) == -1){
            printf("epoll_ctl(%d, %d) failed", op, fd);
            perror("epoll");
            return -1;
        }
    }

    static void epoll_ctl_del(int epfd, int fd){
        int op = EPOLL_CTL_DEL;
        if (epoll_ctl(epfd, op, fd, NULL) == -1)
        {
            printf("epoll_ctl(%d, %d) failed", op, fd);
        }
        return;
    }
    
    static int accept_epoll_event(struct epoll_event* pstEvent){
        Epoll_Data_S* data = (Epoll_Data_S *)(pstEvent->data.ptr);
        int epfd = data->epoll_Fd;
        int fd = data->event_Fd;
        sockaddr_in new_connection;
        int connlen = sizeof(sockaddr_in);
        if (pthread_mutex_trylock(mutex) == 0) {
            if(-1 != (vpn->clientfd = accept(fd, (sockaddr*)&new_connection, (socklen_t*) &connlen))){
                printf("connected to client: %s\n", inet_ntoa(new_connection.sin_addr));
                make_socket_non_blocking(vpn->clientfd);
                
                struct timeval timeout;
                timeout.tv_sec = 100;
                timeout.tv_usec = 0;
                setsockopt(vpn->clientfd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
                int enable=1;
                setsockopt(vpn->clientfd, SOL_TCP,TCP_NODELAY,&enable,sizeof(enable));
                
                epoll_ctl_add(epoll_recvfd, vpn->clientfd, receive_epoll_event);
                vpn->busy = true;
                vpn->send_time = time(NULL);
            }
            pthread_mutex_unlock(mutex);
        }
        return 0;
    }

    static int receive_epoll_event(struct epoll_event* pstEvent){
        Epoll_Data_S *data = (Epoll_Data_S *)(pstEvent->data.ptr);
        int epfd = data->epoll_Fd;
        int fd = data->event_Fd;
        if (pstEvent->events & EPOLLHUP){
            printf("sleeping: %d & %d\n", epfd, fd);
        }
        else if (pstEvent->events & EPOLLIN){
            printf("wake up %d& reading %d\n", epfd, fd);
            if(fd == vpn->clientfd){
                if(vpn->busy == false || vpn->readMsg_from_client() < 0){
                    printf("Client lose connection: %s", inet_ntoa(vpn->tunAddr));
                }
            }
            else if(fd == vpn->tunfd){
                if (vpn->readMsg_from_tun() < 0){
                    printf("Tunnel lose connection: %s", inet_ntoa(vpn->tunAddr));
                }
                return 0;
            }
        }
        else{
            printf("disconnected[%s] EPOLLERR\n",inet_ntoa(vpn->tunAddr));
        }
        vpn->busy = false;
        epoll_ctl_del(epfd, fd);
        close(fd);
        free(data);
        return 0;
    } 

    static int Sync_Mutex(){
        pthread_mutexattr_t attr;
        int ret;
        mutex=(pthread_mutex_t*)mmap(NULL, sizeof(pthread_mutex_t), PROT_READ|PROT_WRITE, MAP_SHARED|MAP_ANON, -1, 0);
        if( MAP_FAILED==mutex) {
            perror("mutex mmap failed");
            return -1;
        }
        pthread_mutexattr_init(&attr);
        ret = pthread_mutexattr_setpshared(&attr,PTHREAD_PROCESS_SHARED);
        if(ret != 0) {
            fprintf(stderr, "mutex set shared failed");
            return -1;
        }
        pthread_mutex_init(mutex, &attr);
    }

    static int initListenEpollFd(int event_max=EPOLL_EVENT_MAX){
        epoll_listenfd = epoll_create(event_max);
        if (-1 == epoll_listenfd) {
            printf("epoll create failed\r\n");
            return -1;
        }
        return epoll_listenfd;
    }

    static int initServerFdPool(int family, const char* service,int listenq){
        assert(serverfd_cnt==0);
        printf("initServerFdPool\n");
        addrinfo hints;
        addrinfo *res, *ressave;
        const int on = 1;
        int listenfd;

        memset(&hints, 0, sizeof(addrinfo));
        hints.ai_family = family;    /* Allow IPv4  and IPv6*/
        hints.ai_flags = AI_PASSIVE;    /* For wildcard IP address */
        hints.ai_protocol = 0;          /* Any protocol */
        hints.ai_socktype = SOCK_STREAM;

        if (getaddrinfo (NULL, service, &hints, &res) != 0){
            perror("get addr info failed");
            exit(0);
        }
        ressave = res;
        do {
            listenfd =socket(res->ai_family, res->ai_socktype, res->ai_protocol);
            if (listenfd < 0)
                continue;
            setsockopt(listenfd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof (on));

            if (bind(listenfd, res->ai_addr, res->ai_addrlen) == 0){
                listen(listenfd, listenq);
                make_socket_non_blocking(listenfd);
                if(serverfd_cnt < MAX_THREADS - 1){
                    serverfd[serverfd_cnt++] = listenfd;
                } 
                else{
                    close(listenfd);
                }
            }else {
                close(listenfd);
            }
        } while ( (res = res->ai_next) != NULL);
        
        freeaddrinfo (ressave);
        for(int i = 0; i < serverfd_cnt; i++) {
            epoll_ctl_add(epoll_listenfd, serverfd[i], accept_epoll_event);
        }
    }
};

int Tun_VPN::serverfd[MAX_THREADS];
int Tun_VPN::serverfd_cnt = 0;
int Tun_VPN::epoll_listenfd = 0;
int Tun_VPN::epoll_recvfd = 0;
pthread_mutex_t* Tun_VPN::mutex = NULL;
Tun_VPN* Tun_VPN::vpn = NULL;
epoll_event* Tun_VPN::events = new epoll_event[EVENT_LIST_MAX];

#endif