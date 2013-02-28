#ifndef ASCENCEUR_H
#define ASCENCEUR_H

#include <libintech/moteur.hpp>
#include <libintech/asservissement.hpp>

#define COMPTEUR_BLOCAGE_MAX 10 // ~ 1 sec (à vérifier)

enum AscenseurPosition {ASCENSEUR_HAUT = 55000, ASCENSEUR_BAS = -75000};

template<class Moteur, class Codeuse>
class Ascenseur
{
	public:
		
		Ascenseur();
		Codeuse libcodeuse;
		void asservir();
		void consigne(int32_t consigne);
		void consigne(AscenseurPosition);
		void codeuse(int32_t);
		int32_t codeuse();
		void desasservir();
		void reasservir();
		void modifierVitesseKpKdKi(int8_t PWM, float kp, float kd, float ki);
						
	private:
	
		Moteur _moteur;
		Asservissement _asservissement;		
		int32_t _codeuse;
		uint8_t _compteur_blocage;
		bool _est_asservi;
		
};

#endif
