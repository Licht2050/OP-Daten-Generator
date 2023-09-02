#ifndef HELP_H
#define HELP_H

#include <iostream>
#include "lamport_clock.h"
#include <string>
#include <fstream>
#include <nlohmann/json.hpp>
#include <chrono>



// DataPacket struct to hold information for each packet
struct DataPacket {
    LamportClock lamport_clock;
    std::string sender;
    long long reply_timestamp;
    long long receive_timestamp;

    DataPacket();
    DataPacket(const LamportClock &lamport_clock, const std::string &sender, long long receive_timestamp);
    DataPacket(const LamportClock &lamport_clock, const std::string &sender, long long receive_timestamp, long long reply_timestamp);
    
    // Konvertiert DataPacket zu JSON-String
    std::string to_string() const;

    // Erstellt ein DataPacket aus einem JSON-String
    static DataPacket from_string(const std::string& s);
};

// RecieveData struct to hold data received by the server
struct RecieveData {
    LamportClock lamport_clock;
    long long receive_timestamp;

    RecieveData(const LamportClock &lamport_clock, long long receive_timestamp);
};


bool load_server_config(const std::string& file_path, std::string& host, int& port);
bool load_config_to_json (const std::string& file_path, nlohmann::json& json_file);
long long get_current_timestamp();

#endif