#include "synchronisation.h"
    

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
    uint32_t t1;
    uint32_t tp;
    uint32_t t4;
    uint32_t teta;
    
    // Commence une synchronisation
    t1 = clock_;
    Serial::print("!");
    Serial::read(buffer);
    t4 = clock_;
    
    if(strcmp(buffer, "!") == 0)
    {
        //Recuperation de la valeur de t2'
        Serial::print("t1");
        Serial::read(buffer);

        
        //Calcul de l'écart teta entre les deux horloges
        teta = tp - (t1 + t4)/2;
        clock_ = clock_ + teta;
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