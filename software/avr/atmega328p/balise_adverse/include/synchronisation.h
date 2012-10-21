#ifndef SYNCHRONISATION_H
#define SYNCHRONISATION_H

#include <stdint.h>
#include <string.h>

#include "libintech/timer.hpp"
#include <libintech/serial/serial_0.hpp>
#include <libintech/xbee.hpp>



template<class Timer , class Xbee>
class Synchronisation
{
private:
    volatile uint32_t clock_;
    
    uint16_t adresse;
    
public:
    
    Synchronisation(uint16_t a);
    
    void synchroniser_client();
    
    void synchroniser_serveur();
    
    void interruption();
    
    uint32_t clock();
};

#endif