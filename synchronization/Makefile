# Variablen
CXX = g++
CXXFLAGS = -Wall -std=c++11

# Targets
all: server client

server: server.cpp help.cpp lamport_clock.cpp
	$(CXX) $(CXXFLAGS) -o server server.cpp help.cpp lamport_clock.cpp

client: client.cpp help.cpp lamport_clock.cpp
	$(CXX) $(CXXFLAGS) -o client client.cpp help.cpp lamport_clock.cpp

clean:
	rm -f server client
