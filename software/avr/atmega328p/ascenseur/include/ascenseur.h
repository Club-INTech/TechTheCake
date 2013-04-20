#ifndef ASCENSEUR_H
#define ASCENSEUR_H

#include <libintech/asservissement.hpp>

#define COMPTEUR_BLOCAGE_MAX 10 // ~ 1 sec (à vérifier)

enum AscenseurPosition {ASCENSEUR_HAUT = 55000, ASCENSEUR_BAS = -75000};

template<class Moteur>
class Ascenseur
{
	public:
		Ascenseur();
		void asservir();
		void modifierVitesseKpKdKi(uint8_t bridage, float kp, float kd, float ki);
		void consigne(int32_t);
		void consigne(AscenseurPosition);
		void changerValeurCodeuse(int32_t);
		int32_t valeurCodeuse();

	private:
		Moteur _moteur;
		Asservissement _asservissement;
		int8_t _compteur_blocage;
		int32_t _codeuse;
};

#endif
