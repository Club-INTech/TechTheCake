#ifndef SYNCHRONISATION_H
#define SYNCHRONISATION_H

#include <stdint.h>
#include <string.h>

#include "libintech/timer.hpp"
#include "libintech/serial/serial_1.hpp"
#include <libintech/xbee.hpp>



template<class Timer , class Xbee>
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