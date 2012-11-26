#ifndef INFRAROUGE_HPP
#define INFRAROUGE_HPP
#include <stdint.h>
#include <avr/io.h>

/** @file libintech/capteur_infrarouge.hpp
 *  @brief Ce fichier crée une classe capteur_infrarouge pour pouvoir utiliser simplement les capteurs.
 *  @author Thibaut ~MissFrance~
 *  @date 08 mai 2012
 */

//Angle du cône de vision: 8°

#define NB_ECHANTILLON                  8
#define VAL_PRESCALER_INFRA             128
#define NB_VALEURS_MEDIANE_INFRAROUGE   4

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
    uint16_t ringBufferValeurs[NB_VALEURS_MEDIANE_INFRAROUGE];
    uint16_t derniereDistance;
    uint8_t  indiceBuffer;

//  static const uint16_t    val_ADCH[NB_ECHANTILLON];
//  static const uint16_t    val_mm[NB_ECHANTILLON] ;

   public:	//constructeur
   CapteurInfrarouge() :
    derniereDistance(0)
    {  //Initialisation de pas mal de choses pour pouvoir utiliser un convertisseur analogique/numérique.
       PinRegister::disable();
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
    PinRegister::enable();
    _delay_us(200); //pour laisser le temps aux registres de s'adapter (valeur expérimentale)
      uint8_t ind = indice_tab(ADCH);
      ringBufferValeurs[indiceBuffer++]=regression_lin(val_ADCH(ind), val_ADCH(ind+1), val_mm(ind), val_mm(ind+1), ADCH);
    PinRegister::disable();
            if(!(indiceBuffer&=(NB_VALEURS_MEDIANE_INFRAROUGE-1))) //calcul de la médiane
            {
                tri_fusion(0, NB_VALEURS_MEDIANE_INFRAROUGE-1);
                derniereDistance=ringBufferValeurs[NB_VALEURS_MEDIANE_INFRAROUGE/2];
            }
  }  
  // Retourne la valeur brute (sans regression linéaire) (donc
  // sans unité) de la distance. On l'appelle ADCH
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
    default: return 0; //cas impossible
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
  
    void fusionner(uint8_t deb, uint8_t milieu, uint8_t fin) {
    uint8_t i1=deb, i2=milieu+1, i3=0, i;
    uint16_t tabAux[NB_VALEURS_MEDIANE_INFRAROUGE];

    while(i1<=milieu && i2<=fin)
    {
        if(ringBufferValeurs[i1]<ringBufferValeurs[i2])
            tabAux[i3++]=ringBufferValeurs[i1++];
        else
            tabAux[i3++]=ringBufferValeurs[i2++];
    }
    while(i1<=milieu)
        tabAux[i3++]=ringBufferValeurs[i1++];

    while(i2<=fin)
        tabAux[i3++]=ringBufferValeurs[i2++];
    for(i=0; i<=fin-deb; i++)
        ringBufferValeurs[i+deb]=tabAux[i];
    }

    void tri_fusion(uint8_t debut, uint8_t fin) { //testé et fonctionnel
    if(debut < fin)
    {
        uint8_t milieu=(fin+debut)/2;
        tri_fusion(debut, milieu);
        tri_fusion(milieu+1, fin);
        fusionner(debut, milieu, fin);
    }
    }
  
};
/*template <> 
const uint16_t    CapteurInfrarouge<class DirectionRegister>::val_ADCH[NB_ECHANTILLON]   = {200, 64, 36, 22, 17, 13, 9, 5};
template <>
const uint16_t    CapteurInfrarouge<class DirectionRegister>::val_mm[NB_ECHANTILLON]     = {70, 100, 200, 300, 400, 500, 600, 900};*/

#endif


