#ifndef SYNCHRONISATION_H
#define SYNCHRONISATION_H

#include <stdint.h>
#include <string.h>



template<class Timer , class Serial>
class Synchronisation
{
private:
    volatile uint32_t clock_;
    
public:
    Synchronisation();
    
    void synchroniser();
    
    void interruption();
    
    uint32_t clock();
};

#endif