# Variablen
CXX = g++
CXXFLAGS = -Wall -Wno-psabi -std=c++14 -I/usr/include/boost

# Targets
all: server

server: server.cpp help.cpp lamport_clock.cpp
	$(CXX) $(CXXFLAGS) -o server server.cpp help.cpp lamport_clock.cpp 


clean:
	rm -f server
