# include "lamport_clock.h"

LamportClock::LamportClock(){
    clock = 0;
}

void LamportClock::increment(){
    clock++;
}

void LamportClock::update(int timestamp){
    clock = max(clock, timestamp) + 1;
}

void LamportClock::set(int timestamp){
    clock = timestamp;
}

int LamportClock::get() const{
    return clock;
}

// Path: OP-Daten-Generator/synchronization/lamport_clock.cpp

