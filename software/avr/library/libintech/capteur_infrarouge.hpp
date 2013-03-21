#ifndef INFRAROUGE_HPP
#define INFRAROUGE_HPP

#include <stdint.h>
#include <avr/io.h>

// Librairie INTech permettant de récupérer la médiane d'un ring_buffer
#include <libintech/algorithm.hpp>

/** @file libintech/capteur_infrarouge.hpp
 *  @brief Ce fichier crée une classe capteur_infrarouge pour pouvoir utiliser simplement les capteurs.
 *  @author Thibaut ~MissFrance~
 *  @date 08 mai 2012
 */

//Angle du cône de vision: 8°
//Distance maximale: 120 cm

#define NB_ECHANTILLON                  8
#define VAL_PRESCALER_INFRA             128

#define NB_VALEURS_MEDIANE_INFRAROUGE   4

typedef ring_buffer<uint16_t, NB_VALEURS_MEDIANE_INFRAROUGE> ringBufferInfra;

/** @class capteur_infrarouge
 *  @brief Classe pour gérer les capteurs
 */


/*class CapteurBase
{

}*/

template< class PinRegister >
class CapteurInfrarouge
{
private:
    ringBufferInfra ringBufferValeurs;
    uint16_t derniereDistance;

//  static const uint16_t    val_ADCH[NB_ECHANTILLON];
//  static const uint16_t    val_mm[NB_ECHANTILLON] ;

   public:	//constructeur
   CapteurInfrarouge() :
    derniereDistance(0)
    {  //Initialisation de pas mal de choses pour pouvoir utiliser un convertisseur analogique/numérique.
       PinRegister::enable();
       PinRegister::prescaler(VAL_PRESCALER_INFRA); //le même pour tous les capteurs
    }

  // Retourne la valeur après regression linéaire (donc en mm)
  // de la distance
  uint16_t value()
  {
    return derniereDistance;
  }

  void refresh()
  {
      uint8_t ind = indice_tab(PinRegister::read());
      ringBufferValeurs.append(regression_lin(val_ADCH(ind), val_ADCH(ind+1), val_mm(ind), val_mm(ind+1), ADCH));
    derniereDistance = mediane(ringBufferValeurs);
  }  
  // Retourne la valeur brute (sans regression linéaire) (donc
  // sans unité) de la distance. On appelle ADCH
  uint16_t value_brut()
  {
       return ADCH;
  }

  private:
  uint32_t regression_lin(uint16_t x1, uint16_t x2, uint16_t y1, uint16_t y2, uint16_t x)
  {
    uint32_t pourcentage = (uint32_t)((x1 - x)*100) / (x1 - x2);
    return (pourcentage * y2 + (100 - pourcentage) * y1) / 100;
  }

  uint16_t val_ADCH(uint8_t i) {
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

  uint16_t val_mm(uint8_t i) {
    switch((i)) {
    case 0 : return 70; 
    case 1 : return 100;
    case 2 : return 200;
    case 3 : return 300;
    case 4 : return 400;
    case 5 : return 500;
    case 6 : return 600;
    case 7 : return 900;
    default: return 1500; //cas impossible
    }
  }


  // Cette fonction permet de trouver le plus petit indice de la table
  // des ADCH pour ensuite pouvoir faire une regression linéaire.
  uint16_t indice_tab(uint16_t adch)
  {
      uint16_t i;
      for (i = 1; i < NB_ECHANTILLON -1; i++)
        if (adch >= val_ADCH(i))
          return i-1;
      return NB_ECHANTILLON-2;
  }
  
};
/*template <> 
const uint16_t    CapteurInfrarouge<class DirectionRegister>::val_ADCH[NB_ECHANTILLON]   = {200, 64, 36, 22, 17, 13, 9, 5};
template <>
const uint16_t    CapteurInfrarouge<class DirectionRegister>::val_mm[NB_ECHANTILLON]     = {70, 100, 200, 300, 400, 500, 600, 900};*/

#endif


