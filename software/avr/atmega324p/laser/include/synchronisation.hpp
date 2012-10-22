#ifndef SYNCHRONISATION_H
#define SYNCHRONISATION_H

#include <stdint.h>
#include <string.h>

#include "libintech/timer.hpp"
#include <libintech/xbee.hpp>
#include <libintech/serial/serial_0.hpp>

#define SYNCHRO_ITERATIONS 9


template<class Timer, class Xbee>
class Synchronisation
{
private:
    volatile uint32_t clock_;
    
public:
    
    Synchronisation(): clock_(0) 
	{
		// Initialisation du Timer
		Timer::init();
	}

	/**
	 * Méthode appelée par les clients (balises) pour se synchroniser avec le serveur
	 * 
	 * @param server Adresse XBEE du serveur de clock
	 * 
	 */
    uint32_t synchroniser_client(uint16_t server)
    {
		char buffer[17];
		uint32_t t1;
		uint32_t tp;
		uint32_t t4;
		uint32_t delta[SYNCHRO_ITERATIONS];
		
		for (int8_t i = 0; i < SYNCHRO_ITERATIONS; i++)
		{
			// Début de la synchronisation, trame aller (Etape 2)
			t1 = clock_;
			Xbee::send(server, "a");
			
			// Attente de la réponse pour le calcul aller retour (Etape 5)
			Xbee::read(buffer);
			t4 = clock_;
			
			// Demande de récuperation de la valeur de tp (Etape 6)
			Xbee::send(server, "tp?");
			Xbee::read(tp);

			// Calcul de l'écart teta entre les deux horloges (Etape 8)
			delta[i] = tp - (t1 + t4)/2;
		}
		
		sort(delta, SYNCHRO_ITERATIONS);
		uint32_t mediane = delta[SYNCHRO_ITERATIONS/2];
		clock_ += mediane;
		
		return mediane;
	}
    
    /**
     * Méthode appelée par le serveur pour lancer la synchronisation sur un périphérique
     * L'horloge du serveur sert de référence
     * 
     * @param client Adresse XBEE du client à synchroniser
     * 
     */
    void synchroniser_serveur(uint16_t client)
    {
		char buffer[17];
		uint32_t tp;
		
		// Demande au client de se synchroniser sur le serveur (Etape 1)
		Xbee::send(client, "s");
		
		for (int8_t i = 1; i <= SYNCHRO_ITERATIONS; i++)
		{
			// Attente de la trame aller (Etape 3)
			Xbee::read(buffer);
			
			// Note le temps d'arrivée et envoie la trame retour (Etape 4)
			tp = clock_;
			Xbee::send(client, "b");
				
			// Attente de la demande d'envoi de tp
			Xbee::read(buffer);
			
			// Envoi de la valeur de tp (Etape 7)
			Xbee::send(client, tp);
		}
	}
    
    /**
     * A appeler à chaque interruption du timer utilisé pour la clock
     * 
     */
    void interruption()
    {
		clock_++;
	}
    
    /**
     * Récupère la valeur courante de l'horloge
     * 
     * @param ms Renvoie la valeur en ms au lieu de la valeur brute du timer
     * 
     */
    uint32_t clock(bool ms = false)
    {
		if (!ms) return clock_;
		
		return clock_/(F_CPU/256000);
	}
	
private:

	/**
	 * Tri du tableau des écarts
	 * 
	 */
	void sort(uint32_t delta[], uint8_t size)
	{
		for (uint8_t i = 0; i < size; i++)
		{
			for (uint8_t j = 0; j < i; j++)
			{
				if (delta[i] > delta[j])
				{
					uint32_t temp = delta[i];
					delta[i] = delta[j];
					delta[j] = temp;
				}
			}
		}
	}
};

#endif
