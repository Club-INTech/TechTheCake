#ifndef ASCENCEUR_H
#define ASCENCEUR_H

#include <libintech/moteur.hpp>
#include <libintech/asservissement.hpp>

#define COMPTEUR_BLOCAGE_MAX 30 // ~ 1 sec (à vérifier)

enum AscenseurPosition {ASCENSEUR_HAUT = 55000, ASCENSEUR_BAS = -75000};

template<class Moteur>
class Ascenceur
{
	public:
		
		Ascenceur();
		void asservir();
		void consigne(int32_t consigne);
		void consigne(AscenseurPosition);
		void codeuse(int32_t);
		int32_t codeuse();
		void desasservir();
		void reasservir();
						
	private:
	
		Moteur _moteur;
		Asservissement _asservissement;		
		int32_t _codeuse;
		uint8_t _compteur_blocage;
		bool _est_asservi;
		
};

#endif
