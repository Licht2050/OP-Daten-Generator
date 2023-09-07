
# ifndef LAMPORT_CLOCK_H
# define LAMPORT_CLOCK_H


# include <iostream>


using namespace std;

class LamportClock
{
    private:
        /* data */
        int clock;

    public:
        LamportClock();
        void increment();
        void update(int timestamp);
        void set(int timestamp);
        int get() const;
};



# endif