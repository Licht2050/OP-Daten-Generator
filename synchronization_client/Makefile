# Variablen
CXX = g++
CXXFLAGS = -Wall -std=c++14 -I/usr/include/boost
LDFLAGS = -L/usr/lib/x86_64-linux-gnu/ -lboost_system

# Targets
all: server client

server: server.cpp help.cpp lamport_clock.cpp
	$(CXX) $(CXXFLAGS) -o server server.cpp help.cpp lamport_clock.cpp $(LDFLAGS)

client: client.cpp help.cpp lamport_clock.cpp generic_sync_server.cpp
	$(CXX) $(CXXFLAGS) -o client client.cpp help.cpp lamport_clock.cpp generic_sync_server.cpp $(LDFLAGS)

clean:
	rm -f server client
