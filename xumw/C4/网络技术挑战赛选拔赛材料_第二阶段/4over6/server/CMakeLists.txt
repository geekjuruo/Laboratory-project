cmake_minimum_required(VERSION 3.5)
project(Tun_VPN)

set(CMAKE_CXX_STANDARD 11)

set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

include_directories(include)
add_executable(Server server.cpp 4over6vpn.hpp utils.hpp)

target_link_libraries(Server Threads::Threads)


