#include <iostream>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>
#include <cstdlib>
#include "lamport_clock.h"
#include "help.h"

using namespace std;

class Client {
private:
    int sockfd;
    struct sockaddr_in serverAddr;
    struct sockaddr_in clientAddr;
    socklen_t clientAddrLen;
    int port;
    string ip;

public:
    Client(int port, const string& ip);
    void send(const LamportClock& lamport_clock);
    DataPacket receive();
    void close();
};

Client::Client(int port, const string& ip) : port(port), ip(ip) {
    sockfd = socket(PF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("ERROR opening socket");
        exit(1);
    }

    memset(&serverAddr, 0, sizeof(serverAddr));
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(port);
    serverAddr.sin_addr.s_addr = inet_addr(ip.c_str());

    memset(&clientAddr, 0, sizeof(clientAddr));
    clientAddr.sin_family = AF_INET;
    clientAddr.sin_port = htons(0);
    clientAddr.sin_addr.s_addr = INADDR_ANY;

    if (bind(sockfd, (struct sockaddr *)&clientAddr, sizeof(clientAddr)) < 0) {
        perror("ERROR on binding");
        exit(1);
    }
}

void Client::send(const LamportClock& lamport_clock) {
    string message = to_string(lamport_clock.get());
    int n = sendto(sockfd, message.c_str(), message.length(), 0, (struct sockaddr *)&serverAddr, sizeof(serverAddr));
    if (n < 0) {
        perror("ERROR writing to socket");
        exit(1);
    }
}

DataPacket Client::receive() {
    char buffer[1024];
    clientAddrLen = sizeof(clientAddr);
    int n = recvfrom(sockfd, buffer, sizeof(buffer) - 1, 0, (struct sockaddr *)&clientAddr, &clientAddrLen);
    if (n < 0) {
        perror("ERROR reading from socket");
        exit(1);
    }

    buffer[n] = '\0'; // Null-terminate the string
    string message(buffer);
    // Parse the message to create a DataPacket object.
    // You would implement this based on how you've implemented DataPacket.
    DataPacket data_packet; // Assume a constructor or a method that can initialize it from a string

    return data_packet;
}

void Client::close() {
    ::close(sockfd);
}

int main(int argc, char const *argv[]) {
    if (argc < 3) {
        cerr << "Usage: " << argv[0] << " <port> <ip>" << endl;
        return 1;
    }

    LamportClock lamport_clock;
    Client c(atoi(argv[1]), argv[2]);

    lamport_clock.increment();
    cout << "Sending: " << lamport_clock.get() << endl;
    c.send(lamport_clock);

    DataPacket received_data = c.receive();
    cout << "Received: " << received_data.to_string() << endl;

    c.close();
    return 0;
}
