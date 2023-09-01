# ifndef CLIENT_H
# define CLIENT_H

# include <iostream>
# include <sys/types.h>
# include <sys/socket.h>
# include <netinet/in.h>
# include <arpa/inet.h>
# include <unistd.h>
# include <cstring>
# include "lamport_clock.h"
# include "help.h"
#include <sstream>
#include <vector>
#include <map>


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
    Client(int port, string ip);
    void send(const LamportClock& lamport_clock, long long& send_timestamp);
    DataPacket receive(long long& receive_timestamp);
    void close();
    ~Client();
};


# endif