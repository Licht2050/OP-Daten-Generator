#include "generic_sync_server.h"

using nlohmann::json;


GenericSyncServer::GenericSyncServer(int port) : port(port) {
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(port);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, 3) < 0) {
        perror("listen");
        exit(EXIT_FAILURE);
    }
}

void GenericSyncServer::send_json(const json& j) {
    int addrlen = sizeof(address);
    int new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t *)&addrlen);
    if (new_socket < 0) {
        perror("accept");
        exit(EXIT_FAILURE);
    }

    std::string jsonString = j.dump();
    send(new_socket, jsonString.c_str(), jsonString.size(), 0);
    close(new_socket);
}

GenericSyncServer::~GenericSyncServer() {
    close(server_fd);
}

