
#ifndef SERVER_H
#define SERVER_H

#include <iostream>
#include <fstream>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>
#include "lamport_clock.h"
#include "help.h"


class Server
{
    private:
        /* data */
        int sockfd;
        struct sockaddr_in serverAddr;

    public:
        Server(int port, std::string ip = "127.0.0.1");
        void send(const DataPacket &data_packet, struct sockaddr_in &clientAddr);
        RecieveData receive(struct sockaddr_in &clientAddr);
        ~Server();
};


#endif

