#ifndef UTIL_H
#define UTIL_H


#define MAX_DATA_FIELD 4096
#define MAX_THREADS     5
#define EPOLL_EVENT_MAX  100
#define EVENT_LIST_MAX   100
#define LISTENQ          10

#define TIME_INTERVAL 60
#define BEATS_INTERVAL 20
#define MSG_HEADER 5

#define REQUEST_FOR_ADDR 100
#define REPLY_FOR_ADDR 101
#define REQUEST_FOR_CONNECTION 102
#define REPLY_FOR_CONNECTION 103
#define HEARTBEATS 104

struct Msg{
    int packet_len;
    char type;
    char data[MAX_DATA_FIELD];
};

#endif