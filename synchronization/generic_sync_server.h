#ifndef GENERIC_SYNC_SERVER_H
#define GENERIC_SYNC_SERVER_H

#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <iostream>
#include <string>
#include <nlohmann/json.hpp>

class GenericSyncServer {
    private:
        int server_fd;
        struct sockaddr_in address;
        int port;
    
    public:
        GenericSyncServer(int port);
        void send_json(const nlohmann::json& j);
        ~GenericSyncServer();

};

#endif