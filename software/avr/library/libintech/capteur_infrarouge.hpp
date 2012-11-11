#ifndef INFRAROUGE_HPP
#define INFRAROUGE_HPP
#include <stdint.h>
#include <avr/io.h>
#include "algorithm.hpp"

/** @file libintech/capteur_infrarouge.hpp
 *  @brief Ce fichier crée une classe capteur_infrarouge pour pouvoir utiliser simplement les capteurs SRF05.
 *  @author Thibaut ~MissFrance~
 *  @date 08 mai 2012
 */


/** @class capteur_infrarouge
 *  @brief Classe pour gérer les capteurs
 */

uint16_t fonctionDegueuPourTabval_ADCH(uint8_t i) {
    switch((i)) {
    case 0 : return 200; 
    case 1 : return 64;
    case 2 : return 36;
    case 3 : return 22;
    case 4 : return 17;
    case 5 : return 13;
    case 6 : return 9;
    case 7 : return 5;
    default: return 0; //cas impossible
    }
}
uint16_t fonctionDegueuPourTabval_mm(uint8_t i) {
    switch((i)) {
    case 0 : return 70; 
    case 1 : return 100;
    case 2 : return 200;
    case 3 : return 300;
    case 4 : return 400;
    case 5 : return 500;
    case 6 : return 600;
    case 7 : return 900;
    default: return 0; //cas impossible
    }
}

template< class PinRegister >
class CapteurInfrarouge
{
private:
  static const uint16_t NB_ECHANTILLON =  8;

public :
//  static const uint16_t    val_ADCH[NB_ECHANTILLON];
//  static const uint16_t    val_mm[NB_ECHANTILLON] ;

   public:	//constructeur
   CapteurInfrarouge()
    {  //Initialisation de pas mal de choses pour pouvoir utiliser un convertisseur analogique/numérique.
        PinRegister::prescalar(128);
        PinRegister::enable();
    }

  // Retourne la valeur après regression linéaire (donc en mm)
  // de la distance
  uint16_t value()
  {
      uint8_t ind = indice_tab(ADCH);
      return regression_lin(fonctionDegueuPourTabval_ADCH(ind), fonctionDegueuPourTabval_ADCH(ind+1), fonctionDegueuPourTabval_mm(ind), fonctionDegueuPourTabval_mm(ind+1), ADCH);
  }
  
  // Retourne la valeur brute (sans regression linéaire) (donc
  // sans unité) de la distance. On l'appelle ADCH
  uint16_t value_brut()
  {
      return ADCH;
  }

  private:
  // Cette fonction permet de trouver le plus petit indice de la table
  // des ADCH pour ensuite pouvoir faire une regression linéaire.
  uint16_t indice_tab(uint16_t adch)
  {
      uint16_t i;
      for (i = 1; i < NB_ECHANTILLON -1; i++)
        if (adch >= fonctionDegueuPourTabval_ADCH(i))
          return i-1;
      return NB_ECHANTILLON-2;
  }
  

  
};
/*template <> 
const uint16_t    CapteurInfrarouge<class DirectionRegister>::val_ADCH[NB_ECHANTILLON]   = {200, 64, 36, 22, 17, 13, 9, 5};
template <>
const uint16_t    CapteurInfrarouge<class DirectionRegister>::val_mm[NB_ECHANTILLON]     = {70, 100, 200, 300, 400, 500, 600, 900};*/

#endif


