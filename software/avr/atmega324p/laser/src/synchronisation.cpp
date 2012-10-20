#include "synchronisation.h"
#include "libintech/timer.hpp"
#include "libintech/serial/serial_1.hpp"

template<class Timer , class Serial>
Synchronisation<Timer , Serial>::Synchronisation() : clock_(0) 
{
    Timer::init();
}

template<class Timer , class Serial>
void Synchronisation<Timer , Serial>::synchroniser()
{
    //Declaration des variables
    char buffer[17];
    uint32_t tp;
    
    // Commence une synchronisation
    Serial::print("début synchro");
    Serial::read(buffer);
    
    if(strcmp(buffer, "!") == 0)
    {
        tp = clock_;
        Serial::print("!");
        
        //Attente de la demande d'envoie de tp
        Serial::read(buffer);
        if(strcmp(buffer, "tp?") == 0)
        {
            //Envoie de la valeur de tp
            Serial::print(tp);
        }
    }
}


template<class Timer , class Serial>
void Synchronisation<Timer , Serial>::interruption()
{
    clock_++;
}

template<class Timer , class Serial>
uint32_t Synchronisation<Timer , Serial>::clock()
{
    return clock_;
}

template class Synchronisation<Timer<0,1>,Serial<1> >;