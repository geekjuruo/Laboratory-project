#include <jni.h>
#include <string>
#include <cstring>
#include <android/log.h>
#include <iostream>
#include <arpa/inet.h>
#include <android/log.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <resolv.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/un.h>		/* for Unix domain sockets */
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <cerrno>
#include <pthread.h>
#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <netinet/in.h>
#include <netinet/ether.h>
#include <netinet/ip.h>
#include <netinet/ip6.h>
#include <netinet/tcp.h>
#include <netinet/udp.h>
#include <netinet/ip_icmp.h>
#include <linux/netlink.h>


extern "C"

using namespace std;

// =========================== 常规 Define =========================== //

#define TAG "BACK JNI"        // 后台JNI Debug 输出 LOG 的标识
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO,TAG ,__VA_ARGS__)
#define LOGW(...) __android_log_print(ANDROID_LOG_WARN,TAG ,__VA_ARGS__)
#define LOGD(...) __android_log_print(ANDROID_LOG_DEBUG,TAG ,__VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR,TAG ,__VA_ARGS__)
#define LOGF(...) __android_log_print(ANDROID_LOG_FATAL,TAG ,__VA_ARGS__)


#define MAXBUF 4104
#define SERV_BUFFER 245760
#define MAX_MESSAGE_LENGTH 4096
#define MAX_HEART_TIME 60
#define MSG_HDR_SIZE 5                                  // 信息头长度为 5，包含4字节的length 和1字节的type

#define PACKET_IN  1
#define PACKET_OUT 2

#define CHECK(operator_)  do { if ( (operator_) == -1 ) { LOGF("(line %d): ERROR - %s.\n", __LINE__, strerror( errno ) ); exit( 1 );  } } while ( false )

// =========================== 消息类型定义 =========================== //

// 客户端消息的结构体定义如下:
struct Message {                            // 用于发送
    int  length;                            // 整个结构体的字节长度
    char type;                              // 类型
    char data[MAX_MESSAGE_LENGTH];          // 数据段
};

// 客户端主要用到下面五种消息类型:
// 类型 100 IP地址请求
const char IP_REQUEST   = 100;
// 类型 101 IP地址回应
const char IP_RESPONSE  = 101;
// 类型 102 上网请求
const char WEB_REQUEST  = 102;
// 类型 103 上网回应
const char WEB_RESPONSE = 103;
// 类型 104 心跳包
const char HEART_BEAT   = 104;

//// 客户端主要用到下面五种消息类型:
//// 类型 100 IP地址请求
//#define IP_REQUEST  100
//// 类型 101 IP地址回应
//#define IP_RESPONSE 101
//// 类型 102 上网请求
//#define WEB_REQUEST 102
//// 类型 103 上网回应
//#define WEB_RESPONSE 103
//// 类型 104 心跳包
//#define HEART_BEAT  104

// 从客户端获取服务器ipv6地址和端口
char* SERVER_ADDR = "2402:f000:4:72:808::9a47";         // 服务器地址
int SERVER_PORT = 5678;                                 // 服务器端口
char server_ipv6_address[MAX_MESSAGE_LENGTH];           // 服务器ipv6地址
bool server_ready = false;                              // 是否从前端获取到了服务器端口和服务器ipv6地址

// =========================== 全局变量记录 =========================== //


int heartbeat_send_counter = 0;         // 心跳包发送计时
int heartbeat_recv_time = 0;            // 心跳包接收时间
int out_length = 0;
int out_times = 0;
int in_length = 0;
int in_times = 0;

int sockfd;                             // 与服务器连接的 socket
int vpn_handle;
int fifo_handle;
int fifo_handle_stats;

bool isClosed = false;                  // 后台线程是否在运行
bool hasIP = false;                     // 是否收取到 ipv4 地址请求响应包

pthread_mutex_t traffic_mutex_in;       // 发送数据包信息记录锁
pthread_mutex_t traffic_mutex_out;      // 接收数据包信息记录锁

// =========================== 后台 函数 =========================== //

// 初始化全局变量
void do_init() {
    isClosed = false;                   // 后台线程开始运行
    hasIP = false;                      // 暂时没有收到 ipv4 地址请求响应包
    server_ready = false;               // 需要从前端获取服务器 ipv6 地址和端口号
    heartbeat_send_counter = 0;         // 发送心跳包个数为 0
    heartbeat_recv_time = 0;            // 心跳包接收时间为 0
    out_length = 0;                     // 发送包大小
    out_times = 0;                      // 发送包个数
    in_length = 0;                      // 接收包大小
    in_times = 0;                       // 接收包个数
}

// 退出处理
void do_exit() {
    if(sockfd) {
        CHECK(close(sockfd));                               // 关闭 socket
    }
    CHECK(close(vpn_handle));                               // 关闭管道
    CHECK(close(fifo_handle));                              // 关闭管道
    CHECK(close(fifo_handle_stats));                        // 关闭管道
}

// 清空获取和发送的包数量和大小数据
void info_init() {
    pthread_mutex_lock(&traffic_mutex_out);
    out_length = 0;
    out_times = 0;
    pthread_mutex_unlock(&traffic_mutex_out);
    pthread_mutex_lock(&traffic_mutex_in);
    in_length = 0;
    in_times = 0;
    pthread_mutex_unlock(&traffic_mutex_in);
}

// 更新获取和发送的包数量和大小数据
void info_update(int len, int packet_type) {
    if (packet_type == PACKET_IN) {
        pthread_mutex_lock(&traffic_mutex_in);
        in_length += len;                   // 收到上网包长度记录
        in_times ++;                        // 收到上网包个数加一
        pthread_mutex_unlock(&traffic_mutex_in);
    } else if (packet_type == PACKET_OUT) {
        pthread_mutex_lock(&traffic_mutex_out);
        out_length += len;
        out_times ++;
        pthread_mutex_unlock(&traffic_mutex_out);
    }
}

// =========================== 线程 函数 =========================== //

// 退出检测函数
void* check_quit_thread(void *arg) {
    char buffer[MAXBUF + 1];
    bzero(buffer, MAXBUF + 1);
    while(!isClosed) {
        int len = read(fifo_handle, buffer, MAXBUF);
        if(buffer[0] == '9' && buffer[1] == '9' && buffer[2] == '9') {
            isClosed = true;
            LOGE("VPN 退出！！");
        }
    }
    return NULL;
}

// 定时器线程，定期发送心跳包，读写虚接口的流量信息写入管道
void* time_thread(void *arg) {
    // 构建心跳包
    Message heart_beat;
    bzero(&heart_beat, sizeof(Message));
//    heart_beat.length = sizeof(Message);
    heart_beat.length = 8;
    heart_beat.type = HEART_BEAT;
    char buffer[MAXBUF + 1];
    char fifo_buffer[MAXBUF + 1];
    bzero(buffer, MAXBUF + 1);
    memcpy(buffer, &heart_beat, sizeof(Message));

    while(!isClosed) {
        // 检测是否超时断开连接
        int current_time = time((time_t*)NULL);                     // 记录当前时间
        if(current_time - heartbeat_recv_time >= MAX_HEART_TIME) {  // 测试是否超时，超时退出
            LOGF("We Lost Server!!!\n");
            exit(1);
        }

        // 定期发送心跳包
        if(heartbeat_send_counter == 0) {
            // Send Heart Beat Package
//            int len = send(sockfd, buffer, MSG_HDR_SIZE, 0);
//            int len = send(sockfd, buffer, 8, 0);
            Message msg;
            bzero(&msg, sizeof(Message));
            msg.type = HEART_BEAT;
            msg.length = 0;
            int len = send(sockfd, (char *) &msg, sizeof(int) + sizeof(char), 0);
            LOGE("发送心跳包成功，length = %d", len);
            if(len != MSG_HDR_SIZE) {           // 发送长度保证为 5
                LOGF("Something happened while sending heart beats!\n");
            }
            heartbeat_send_counter = 19;
        }
        else {
            heartbeat_send_counter--;
        }


        // 读写虚接口的流量信息写入管道
        bzero(fifo_buffer, MAXBUF + 1);
        sprintf(fifo_buffer, "%d %d %d %d ", out_length, out_times, in_length, in_times);
        CHECK(write(fifo_handle_stats, fifo_buffer, strlen(fifo_buffer) + 1));

        // 每秒清空获取的包数量和大小
        info_init();
        sleep(1);
    }
    LOGD("timer thread exit \n");
    return NULL;
}

// 读取虚接口线程
void* vpn_packet_thread(void *arg) {
    char buffer[MAXBUF + 1];
    bzero(buffer, MAXBUF + 1);

    int len, maxfdp = vpn_handle + 1;

    Message msg;
    bzero(&msg, sizeof(Message));
    fd_set fds;

    while(!isClosed) {
        FD_ZERO(&fds);
        FD_SET(vpn_handle ,&fds);
        switch (select(maxfdp, &fds, NULL, NULL, NULL)) {
            case -1:
                LOGF("(line %d): ERROR - %s.\n", __LINE__, strerror( errno ) );
                exit(1);
            case 0:
                break;
            default:
                if(FD_ISSET(vpn_handle, &fds)) {
                    Message tun_packet;
                    memset(&tun_packet, 0, sizeof(Message));
                    tun_packet.type = 102;
                    len = read(vpn_handle, tun_packet.data, MAXBUF);
                    if (len > 0) {
                        tun_packet.length = len + sizeof(int) + sizeof(char);
                        CHECK(send(sockfd, (char *) &tun_packet, tun_packet.length, 0));
                    }

//                    char buffer[MAXBUF + 1];                // 初始化接收 buffer
//                    bzero(buffer, MAXBUF + 1);
//                    Message send_msg;
//                    bzero(&send_msg, sizeof(Message));
//                    len = read(vpn_handle, send_msg.data, MAXBUF);
//                    LOGE("Read %d Bytes from pipe", len);
////                    send_msg.length = sizeof(Message);
//                    send_msg.length = len + 8;
//                    send_msg.type = WEB_REQUEST;
//                    memcpy(buffer, &send_msg, sizeof(Message));
////                    CHECK(send(sockfd, buffer, sizeof(Message), 0));
//                    CHECK(send(sockfd, buffer, len + 8, 0));

//
//                    CHECK(len = read(vpn_handle, buffer, MAXBUF));          // 持续读取虚接口;
//                    LOGE("Read %d Bytes from pipe", len);
//
//                    // 封装 102(上网请求)类型的报头;
//                    msg.length = len + MSG_HDR_SIZE;                        // 从虚接口中读入数据，并加上信息头长度
//                    msg.type = WEB_REQUEST;
//                    memcpy(msg.data, buffer, size_t(len));
//                    memcpy(buffer, &msg, sizeof(Message));
//                    // 通过 IPV6 套接字发送给 4over6 隧道服务器。
//                    int real_send_len = send(sockfd, buffer, sizeof(Message), 0);
//                    if(real_send_len != sizeof(Message)) {
//                        LOGD("Send Error!\n");
//                    }

                    // 记录发送长度
                    info_update(len, PACKET_OUT);

                    // 发送结束后清空 buffer
                    bzero(&msg, sizeof(Message));
                    bzero(buffer, MAXBUF + 1);
                }
        }
    }
    LOGD("vpn_handle thread exit \n");
    return NULL;
}

// =========================== main 函数 =========================== //

// 后台主函数 Main
int main(void) {

    // 初始化全局变量
    do_init();

    char buffer[MAXBUF + 1];                // 初始化接收 buffer
    bzero(buffer, MAXBUF + 1);

    // 创建虚拟管道
    char * pipe_name = "/data/data/com.example.thu_4over6_vpn/mypipe";
    char * pipe_name_stats = "/data/data/com.example.thu_4over6_vpn/mypipe_stats";

    mkfifo(pipe_name, 0666);
    mkfifo(pipe_name_stats, 0666);
    CHECK(fifo_handle = open(pipe_name, O_RDWR|O_CREAT|O_TRUNC));
    CHECK(fifo_handle_stats = open(pipe_name_stats, O_RDWR|O_CREAT|O_TRUNC));

    // 读写管道线程初始化
    pthread_mutex_init(&traffic_mutex_in, NULL);
    pthread_mutex_init(&traffic_mutex_out, NULL);


    // 与服务器进行 socket 连接
    struct sockaddr_in6 server_socket;                                  // 创建 ipv6 套接字
    CHECK(sockfd = socket(AF_INET6, SOCK_STREAM, 0));                   // 创建和服务器连接的 socket 并获取 socket 描述符
    LOGE("socket连接1：socket created!\n");

    LOGE("after server ipv6 address %s，%d", SERVER_ADDR, SERVER_PORT);

    bzero(&server_socket, sizeof(server_socket));
    server_socket.sin6_family = AF_INET6;
    server_socket.sin6_port = htons(SERVER_PORT);
    CHECK(inet_pton(AF_INET6, SERVER_ADDR, &server_socket.sin6_addr));
    LOGE("socket连接2：address created!\n");

    LOGE("server ipv6 address %s，%d", SERVER_ADDR, SERVER_PORT);
    CHECK(connect(sockfd, (struct sockaddr *) &server_socket, sizeof(server_socket)));
    LOGE("socket连接3：Connect Succeeded!\n");

    // 构建定时器线程
    heartbeat_recv_time = time((time_t*)NULL);                      // 初始化心跳包接收时间
    pthread_t timer_thread;                                         // 构建定时器线程
    pthread_create(&timer_thread, NULL, time_thread, NULL);         // 构建定时器线程

//    // 发送消息类型为 100 的 IP 请求消息;
//    Message msg;
//    bzero(&msg, sizeof(Message));
////    msg.length = sizeof(Message);
//    msg.length = 8;
//    msg.type = IP_REQUEST;
//    memcpy(buffer, &msg, sizeof(Message));
////    CHECK(send(sockfd, buffer, sizeof(Message), 0));
//    CHECK(send(sockfd, buffer, 8, 0));

    Message msg;
    bzero(&msg, sizeof(Message));
    msg.type = IP_REQUEST;
    msg.length = 0;
    CHECK(send(sockfd, (char *) &msg, sizeof(int) + sizeof(char), 0));


    // while 循环中接收服务器发送来的消息，并对消息类型进行判断;
    while(!isClosed) {
        int len = 0, len2 = 0;                          // len = 4, len2 = length - 4
        bzero(buffer, MAXBUF + 1);                  // 接收数据包前清空缓存区
        bzero(&msg, sizeof(Message));

        // 读取数据包
        CHECK(len = recv(sockfd, buffer, sizeof(int), 0));    // 先获取 4 字节大小的 length
        int td_len = *(int*) buffer - 4;            // 获取 length 的数值，再计算接下来要读入的长度（type + data length）
        for (int i = 0; i < td_len; i++) {
            int temp_len = 0;
            CHECK(temp_len = recv(sockfd, buffer + 4 + i, 1, 0));       // 从 buffer + 4 开始每次读取一个字节，慢慢读完 length 长度
            len2 += temp_len;
        }
        LOGE("Receive %d + %d Bytes From Server!\n", len, len2);

        // 解析数据包，将数据拷贝到 Message
        bzero(&msg, sizeof(Message));                                   // 清空数据包内容
        memcpy(&msg, buffer, sizeof(Message));                          // 将数据从缓冲区拷贝到Message中
//        memcpy(&msg, buffer, len + len2);                          // 将数据从缓冲区拷贝到Message中

        if(!hasIP && msg.type == IP_RESPONSE) {                         // 收到地址响应包

            LOGE("Type: IP_RESPONSE\nContents: %s\n", msg.data);
            char b[1024] = "";
            bzero(b, sizeof(b));
            sprintf(b, "%s%d \0", msg.data, sockfd);
            int pre_write_len = strlen(b) + 1;
            int real_write_len = write(fifo_handle, b, size_t(pre_write_len));      // 将 IPV4 地址以及 DNS 信息写回到管道
            if(pre_write_len != real_write_len) {                                   // 检查是否将data全部写入到管道中
                fprintf( stderr, "(line %d): ERROR - %s.\n", __LINE__, strerror( errno ) );
                exit(1);
            }

            sleep(1);               // 等待写过程处理

            // Now Wait for File Handle
            memset(buffer, 0, MAXBUF + 1);
            len = read(fifo_handle, buffer, MAXBUF);
            if(len != sizeof(int)) {
                LOGE("File Handle Read Error! Read %s (len:%d)\n", buffer, len);
                exit(1);
            }
            vpn_handle = *(int*)buffer;
            vpn_handle = ntohl(vpn_handle);
            LOGE("Get VPN Handle %d Succeeded!\n", vpn_handle);

            // 创建 VPN 服务线程
            pthread_t vpn_thread, exit_thread;
            pthread_create(&vpn_thread, NULL, vpn_packet_thread, NULL);
            pthread_create(&exit_thread, NULL, check_quit_thread, NULL);
            hasIP = true;
        }
        else if(msg.type == HEART_BEAT) {                       // 收到心跳包，重新记录收到心跳包的时间即可，由定时线程进行回复心跳包
            LOGE("Type: HEARTBEAT\nContents: %s\n", msg.data);
            heartbeat_recv_time = time((time_t*)NULL);
        }
        else if(msg.type == WEB_RESPONSE) {                     // 收到上网回应包
            LOGE("Type: DATA_REC (length: %d)\nContents: %s\n", msg.length, msg.data);
            int pre_write_len = msg.length - MSG_HDR_SIZE;
            int real_write_len = write(vpn_handle, msg.data, size_t(pre_write_len));
            if (real_write_len != pre_write_len) {
                fprintf( stderr, "(line %d): ERROR - %s.\n", __LINE__, strerror( errno ) );
            }

            // 加锁计数
            info_update(pre_write_len, PACKET_IN);
        }
        else {
            LOGD("Unknown Receive Type %d!\n", msg.type);
            LOGD("Contents: %s\n", msg.data);
        }
    }
    do_exit();

    return EXIT_SUCCESS;
}


// =========================== JNI 函数 =========================== //


// ================== MainActivity ================== //

extern "C" JNIEXPORT jint JNICALL
Java_com_example_thu_14over6_1vpn_MainActivity_startVpnFromJNI(JNIEnv *env, jobject instance, jstring addr_, jint port) {
    LOGE("4over6 VPN java call C to start");
    LOGE("4over6 VPN thread Begins!");

    const char *addr = env->GetStringUTFChars(addr_, 0);
    SERVER_ADDR = (char *) addr;                                // 从前端获取服务器 ipv6 地址
    SERVER_PORT = port;                                         // 从前端获取服务器端口
    memcpy(server_ipv6_address, (char *)addr, strlen(addr));    // 拷贝到管道
    LOGE("server ipv6 address %s，%d", server_ipv6_address, SERVER_PORT);
    env->ReleaseStringUTFChars(addr_, addr);

    main();
    LOGE("4over6 VPN thread Ends!");

    return 0;
}

extern "C" JNIEXPORT jint JNICALL
Java_com_example_thu_14over6_1vpn_MainActivity_quitVpnFromJNI(JNIEnv *env, jobject instance) {
    isClosed = true;
    LOGE("VPN 程序 退出！！");

    CHECK(pthread_mutex_destroy(&traffic_mutex_in));
    CHECK(pthread_mutex_destroy(&traffic_mutex_out));
    return 0;
}

// JNI function demo
extern "C" JNIEXPORT jstring JNICALL
Java_com_example_thu_14over6_1vpn_MainActivity_stringFromJNI(
        JNIEnv *env,
        jobject /* this */) {
    std::string hello = "Hello from C++";
    return env->NewStringUTF(hello.c_str());
}