#include "client.h"


Client::Client(int port, string ip){
    this->port = port;
    this->ip = ip;
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
    memset(&clientAddr, 0, sizeof(clientAddr));
    clientAddr.sin_family = AF_INET;
    clientAddr.sin_port = htons(0);
    clientAddr.sin_addr.s_addr = INADDR_ANY;
    if (bind(sockfd, (struct sockaddr *) &clientAddr, sizeof(clientAddr)) < 0)
    {
        perror("ERROR on binding");
        exit(1);
    }
}

void Client::send(const LamportClock& lamport_clock, long long& send_timestamp){
    string message = to_string(lamport_clock.get());

    send_timestamp = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::system_clock::now().time_since_epoch()).count();
    int n = sendto(sockfd, message.c_str(), message.length(), 0, (struct sockaddr *) &serverAddr, sizeof(serverAddr));
    if (n < 0)
    {
        perror("ERROR writing to socket");
        exit(1);
    }
}

DataPacket Client::receive(long long& receive_timestamp){
    char buffer[1024];
    int n = recvfrom(sockfd, buffer, sizeof(buffer) - 1, 0, (struct sockaddr *) &clientAddr, &clientAddrLen);
    if (n < 0)
    {
        perror("ERROR reading from socket");
        exit(1);
    }

    receive_timestamp = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::system_clock::now().time_since_epoch()).count();

    buffer[n] = '\0';  // Null-terminate the string
    std::string message(buffer);

    // Parse message
    DataPacket data_packet = DataPacket::from_string(message);
    return data_packet;
}

void Client::close(){
    ::close(sockfd);
}

Client::~Client(){
    close();
}


// function to calculate ntp offset
void calculate_ntp_offset(
                                long long client_receive_timestamp, 
                                long long client_reply_timestamp, 
                                long long server_send_timestamp, 
                                long long server_receive_timestamp,
                                long long& message_duration,
                                long long& clock_drift
                                ){
    long long latency = (server_receive_timestamp - server_send_timestamp) - (client_reply_timestamp - client_receive_timestamp);
    message_duration = latency / 2;

    clock_drift = ((client_receive_timestamp - server_send_timestamp) - (server_receive_timestamp - client_reply_timestamp))/2;
}   
    
    

int main(int argc, char const *argv[]){
    std::string host;
    int port = 0;
    if (!load_server_config("synchronization_config.json", host, port)) {
        std::cerr << "Failed to load server config." << std::endl;
        return 1;
    }

    

    json json_file;
    if (!load_config_to_json("synchronization_config.json", json_file)) {
        std::cerr << "Failed to load server config." << std::endl;
        return 1;
    }

    int request_interval = json_file["synchronization"]["request_interval"].get<int>();

    
    while (true)
    {
        sleep(request_interval);
        LamportClock lamport_clock;
        Client c(port, host);

        lamport_clock.increment();
        cout << "Sending: " << lamport_clock.get() << endl;

        long long send_timestamp = 0;
        c.send(lamport_clock, send_timestamp);

        long long receive_timestamp = 0;
        DataPacket received_data = c.receive(receive_timestamp);
        cout << received_data.to_string() << endl;

        long long message_duration = 0;
        long long clock_drift = 0;

        calculate_ntp_offset(received_data.receive_timestamp,
                            received_data.reply_timestamp,
                            send_timestamp,
                            receive_timestamp,
                            message_duration,
                            clock_drift
                            );
        cout << "Server send timestamp: " << send_timestamp << endl;
        cout << "Server receive timestamp: " << receive_timestamp << endl;
        cout << "Message duration: " << message_duration << endl;
        cout << "Clock drift: " << clock_drift << endl;

    }

    // T0 = 1693580577266103
    // T1 = 1693580577266146,
    // T2 = 1693580577266174,
    // T3 = 1693580577266242
    // offset = ((T1 - T0) + (T2 - T3)) / 2

    return 0;
}