#include "client.h"
#include <thread>
#include "generic_sync_server.h"
#include <boost/interprocess/shared_memory_object.hpp>
#include <boost/interprocess/sync/named_semaphore.hpp>
#include <boost/interprocess/mapped_region.hpp>


using namespace boost::interprocess;
using nlohmann::json;
using namespace std;


Client::Client(int port, string ip)
    : sockfd(-1), port(port), ip(ip) {
    open();
}

void Client::send(const LamportClock& lamport_clock, long long& send_timestamp){
    string message = to_string(lamport_clock.get());

    // Get current timestamp and send message
    send_timestamp = get_current_timestamp();
    int sentBytes = sendto(sockfd, message.c_str(), message.length(), 0, (struct sockaddr *) &serverAddr, sizeof(serverAddr));
    if (sentBytes < 0){
        throw std::runtime_error("Error writing to socket");
    }
}

DataPacket Client::receive(long long& receive_timestamp){
    char buffer[BUFFER_SIZE];
    int receivedBytes = recvfrom(sockfd, buffer, sizeof(buffer) - 1, 0, (struct sockaddr *) &clientAddr, &clientAddrLen);
    if (receivedBytes < 0){
        throw std::runtime_error("Error reading from socket");
    }

    receive_timestamp = get_current_timestamp();

    buffer[receivedBytes] = '\0';  // Null-terminate the string
    std::string message(buffer);

    // Parse message
    DataPacket data_packet = DataPacket::from_string(message);
    return data_packet;
}

void Client::open(){
    if (sockfd != -1) {
        cerr << "Socket already opened." << endl;
        return;
    }

    // Initialize socket
    sockfd = socket(PF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0){
        throw std::runtime_error("Error opening socket");
    }

    memset(&serverAddr, 0, sizeof(serverAddr));
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(port);
    serverAddr.sin_addr.s_addr = inet_addr(ip.c_str());

    memset(&clientAddr, 0, sizeof(clientAddr));
    clientAddr.sin_family = AF_INET;
    clientAddr.sin_port = htons(0);
    clientAddr.sin_addr.s_addr = INADDR_ANY;

    if (bind(sockfd, (struct sockaddr *) &clientAddr, sizeof(clientAddr)) < 0){
        throw std::runtime_error("Error on binding");
    }
}

void Client::close(){
    if (sockfd == -1) {
        cerr << "Socket already closed." << endl;
        return;
    }
    ::close(sockfd);
    sockfd = -1;
}

Client::~Client(){
    close();
}


// function to calculate ntp offset
void calculate_ntp_offset(long long client_receive_timestamp, long long client_response_timestamp, 
                            long long server_send_timestamp, long long server_receive_timestamp,
                            long long& message_duration, long long& clock_drift){

    long long latency = (server_receive_timestamp - server_send_timestamp) - (client_response_timestamp - client_receive_timestamp);
    message_duration = latency / 2;
    clock_drift = ((client_receive_timestamp - server_send_timestamp) - (server_receive_timestamp - client_response_timestamp))/2;
}   
    




int main(int argc, char const *argv[]){
    try{
        // Entfernen des Shared Memory und des Semaphores, falls sie bereits existieren
        shared_memory_object::remove("MySharedMemory");  
        named_semaphore::remove("MySemaphore");

        // Erzeugung des Shared Memory
        shared_memory_object shm(create_only, "MySharedMemory", read_write);
        shm.truncate(sizeof(SharedData));
    
        // Erzeugung des Semaphores
        named_semaphore sem(create_only, "MySemaphore", read_write);
        
        // Mappen des Shared Memory in den Prozessadressraum
        mapped_region region(shm, read_write);

        // Ein Zeiger auf den gemappten Bereich
        SharedData* data = static_cast<SharedData*>(region.get_address());

        json json_file;
        if (!load_config_to_json("synchronization_config.json", json_file)) {
            throw std::runtime_error("Failed to load server config.");
        }

        std::string host = json_file["udp_server"]["host"].get<std::string>();
        int port = json_file["udp_server"]["port"].get<int>();
        int request_interval = json_file["synchronization"]["request_interval"].get<int>();
        int num_samples = 0;
        const int sample_limit = 10; // Number of samples to average over
        long long message_duration_sum = 0, clock_drift_sum = 0;

        Client c(port, host);
        LamportClock lamport_clock;
        long long send_timestamp = 0, receive_timestamp = 0;
        long long message_duration = 0, clock_drift = 0;

        while (true){
            // std::this_thread::sleep_for(std::chrono::seconds(request_interval));
            std::this_thread::sleep_for(std::chrono::milliseconds(request_interval));
            lamport_clock.increment();

            cout << "Sending: " << lamport_clock.get() << endl;
            c.send(lamport_clock, send_timestamp);

            DataPacket received_data = c.receive(receive_timestamp);
            cout << received_data.to_string() << endl;

            calculate_ntp_offset(
                received_data.receive_timestamp,
                received_data.reply_timestamp,
                send_timestamp,
                receive_timestamp,
                message_duration,
                clock_drift);
            
            clock_drift_sum += clock_drift;
            message_duration_sum += message_duration;
            num_samples++;

            
            if (num_samples >= sample_limit) {
                message_duration = message_duration_sum / num_samples;
                clock_drift = clock_drift_sum / num_samples;
                
                // lock the shared memory for writing 
                sem.wait();
                data->message_duration = message_duration;
                data->offset = clock_drift;
                
                // unlock the shared memory
                sem.post();
                // reset the variables
                num_samples = 0;
                message_duration_sum = 0;
                clock_drift_sum = 0;
            }
        }
    } catch(const std::exception& e){
        std::cerr << "An error occurred: " << e.what() << std::endl;
        // Entfernen des Shared Memory
        named_semaphore::remove("MySemaphore");
        shared_memory_object::remove("MySharedMemory");
        
        return 1;
    }

    // Entfernen des Shared Memory
    named_semaphore::remove("MySemaphore");
    shared_memory_object::remove("MySharedMemory");
    return 0;
}