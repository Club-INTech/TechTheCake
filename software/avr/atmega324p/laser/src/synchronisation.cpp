#include "synchronisation.h"

#include "libintech/timer.hpp"
#include <libintech/xbee.hpp>
#include <libintech/serial/serial_0.hpp>

template<class Timer, class Xbee>
Synchronisation<Timer,Xbee>::Synchronisation(): clock_(0) 
{
    //On enregistre la valeur de l'adresse du Xbee
    //adresse = a;
    
    //Initialisation du Timer
    Timer::init();
}

template<class Timer, class Xbee>
void Synchronisation<Timer,Xbee>::synchroniser_client()
{
	/*
    //Declaration des variables
    char buffer[17];
    uint32_t t1;
    uint32_t tp;
    uint32_t t4;
    uint32_t teta;
    
    // Début de la synchronisation
    t1 = clock_;
    Xbee::send(adresse, "!");
    Xbee::read(buffer);
    t4 = clock_;
    
    if(strcmp(buffer, "!") == 0)
    {
        //Recuperation de la valeur de tp
        Xbee::send(adresse, "tp?");
        Xbee::read(tp);

        //Calcul de l'écart teta entre les deux horloges
        teta = tp - (t1 + t4)/2;
        clock_ = clock_ + teta;
    }
    */
}

template<class Timer , class Xbee>
void Synchronisation<Timer, Xbee>::synchroniser_serveur(uint16_t add)
{
	/*
    //Declaration des variables
    char buffer[17];
    uint32_t tp;
    
    // Commence une synchronisation
    Xbee::send(add, "début synchro");
    Xbee::read(buffer);
    
    if(strcmp(buffer, "!") == 0)
    {
        tp = clock_;
        Xbee::send(add, "!");
        
        //Attente de la demande d'envoie de tp
        Xbee::read(buffer);
        if(strcmp(buffer, "tp?") == 0)
        {
            //Envoie de la valeur de tp
            Xbee::send(add, tp);
        }
    }
    * */
}


template<class Timer , class Xbee>
void Synchronisation<Timer , Xbee>::interruption()
{
    clock_++;
}

template<class Timer , class Xbee>
uint32_t Synchronisation<Timer , Xbee>::clock()
{
    return clock_;
}

