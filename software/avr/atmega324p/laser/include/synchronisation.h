#ifndef SYNCHRONISATION_H
#define SYNCHRONISATION_H

#include <stdint.h>
#include <string.h>

#include "libintech/timer.hpp"
#include <libintech/xbee.hpp>
#include <libintech/serial/serial_0.hpp>


template<class Timer, class Xbee>
class Synchronisation
{
private:
    volatile uint32_t clock_;
    
    uint16_t adresse;
    
public:
    
    Synchronisation();
    
    void synchroniser_client();
    
    void synchroniser_serveur(uint16_t);
    
    void interruption();
    
    uint32_t clock();
};

#endif
