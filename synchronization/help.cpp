#include "help.h"

using namespace std;

// Initialize members using initializer list
DataPacket::DataPacket() : lamport_clock(), sender(""), reply_timestamp(0), receive_timestamp(0) {}

// Initialize members using initializer list
DataPacket::DataPacket(const LamportClock &lamport_clock, const std::string &sender, long long receive_timestamp)
    : lamport_clock(lamport_clock), sender(sender), reply_timestamp(0), receive_timestamp(receive_timestamp) {}

// Initialize members using initializer list
DataPacket::DataPacket(const LamportClock &lamport_clock, const std::string &sender, long long receive_timestamp, long long reply_timestamp)
    : lamport_clock(lamport_clock), sender(sender), reply_timestamp(reply_timestamp), receive_timestamp(receive_timestamp) {}

// Convert DataPacket to json string
std::string DataPacket::to_string() const {
    json j;
    j["lamport_clock"] = lamport_clock.get();
    j["sender"] = sender;
    j["reply_timestamp"] = reply_timestamp;
    j["receive_timestamp"] = receive_timestamp;
    return j.dump();
}

// Create a DataPacket from a json string
DataPacket DataPacket::from_string(const std::string& s) {
    json j = json::parse(s);
    LamportClock lc;
    lc.set(j["lamport_clock"].get<int>());
    std::string sender = j["sender"].get<std::string>();
    long long reply_timestamp = j["reply_timestamp"].get<long long>();
    long long receive_timestamp = j["receive_timestamp"].get<long long>();
    return DataPacket(lc, sender, receive_timestamp, reply_timestamp);
}

// Initialize members using initializer list
RecieveData::RecieveData(const LamportClock &lamport_clock, long long receive_timestamp)
    : lamport_clock(lamport_clock), receive_timestamp(receive_timestamp) {}




// function to load server config from json file
bool load_server_config(const std::string& file_path, std::string& host, int& port){
    std::ifstream i(file_path);
    if (!i.is_open()) {
        std::cerr << "Could not open config file." << std::endl;
        return false;
    }
    
    json j;
    i >> j;

    if (j.find("udp_server") != j.end()) {
        host = j["udp_server"]["host"];
        port = j["udp_server"]["port"];
    } else {
        std::cerr << "Invalid config format." << std::endl;
        return false;
    }
    
    return true;
}

// function to load json file
bool load_config_to_json (const std::string& file_path, json& json_file){
    std::ifstream i(file_path);
    if (!i.is_open()) {
        std::cerr << "Could not open config file." << std::endl;
        return false;
    }
    
    i >> json_file;
    
    return true;
}