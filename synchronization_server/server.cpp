#include "server.h"



Server::Server(int port, std::string ip){
    sockfd = socket(PF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0)
    {
        perror("ERROR opening socket");
        exit(1);
    }
    memset(&serverAddr, 0, sizeof(serverAddr));
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(port);
    serverAddr.sin_addr.s_addr = inet_addr(ip.c_str());
    if (bind(sockfd, (struct sockaddr *) &serverAddr, sizeof(serverAddr)) < 0)
    {
        perror("ERROR on binding");
        exit(1);
    }
}


void Server::send(const DataPacket &data_packet, struct sockaddr_in &clientAddr){
    const string &msg = data_packet.to_string();
    int n = sendto(sockfd, msg.c_str(), msg.length(), 0, (struct sockaddr *) &clientAddr, sizeof(clientAddr));
    if (n < 0)
    {
        perror("ERROR writing to socket");
        exit(1);
    }
}

RecieveData Server::receive(struct sockaddr_in &clientAddr){
    char buffer[1024]={0};
    socklen_t clientAddrLen = sizeof(clientAddr);
    int n = recvfrom(sockfd, buffer, 1024, 0, (struct sockaddr *) &clientAddr, &clientAddrLen);
    if (n < 0)
    {
        perror("ERROR in recvfrom");
        exit(1);
    }
    string message(buffer, n);
    LamportClock lamport_clock;
    lamport_clock.update(stoi(message));
    // time in milliseconds
    
    // time in microseconds
    auto receive_timestamp = get_current_timestamp();
    return RecieveData(lamport_clock, receive_timestamp);
}

Server::~Server(){
    close(sockfd);
}




int main(){
    std::string host;
    int port = 0;
    if (!load_server_config("synchronization_config.json", host, port)) {
        std::cerr << "Failed to load server config." << std::endl;
        return 1;
    }

    Server s(port, host);
    struct sockaddr_in clientAddr;
    cout << "Waiting for data..." << endl;
    while (true){
        RecieveData recieve_data = s.receive(clientAddr);
        // cout << "Received: " << recieve_data.receive_timestamp << endl;
        recieve_data.lamport_clock.increment();
        DataPacket data_packet(recieve_data.lamport_clock, "server", recieve_data.receive_timestamp);
        
        // time in microseconds
        auto send_timestamp = get_current_timestamp();
        data_packet.reply_timestamp = send_timestamp;
        s.send(data_packet, clientAddr);
        // cout << "Sending: " << data_packet.to_string() << endl;
    }
    

    return 0;
}
