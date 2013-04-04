/* dans ce fichier, il y a trois timers, l'un pour générer un pwm pour le servomoteur,
 * l'autre pour le pilotage auto du robot selon une ligne, le troisième pour le pwm du moteur.
 * Le premier timer est justifié car le pwm standard des avr ne correspond pas au signal 50Hz
 * nécéssaire pour les servo; l'autre car on réserve la boucle inifinie du coeur du programme
 * à la gestion de la série qui est bloquante en lecture.
 * voili, voilà, bonne lecture.
 */

#include <stdint.h>
#include <util/delay.h>
#include <avr/interrupt.h>
#include <libintech/utils.h> 
#include <libintech/pwm.hpp>
#include <libintech/timer.hpp>
#include <libintech/serial/serial_0_interrupt.hpp>//j'ai pas pu classer les include par taille...
#include <libintech/serial/serial_0.hpp>// du coup lui il arrive après ;-)

#define TAILLE_HIST 7 // on moyenne les lectures des capteurs de lignes pour éliminer le bruit
#define SEUIL 2 // le nombre de valeurs identiques à relever pour se convaincre de l'état des capteurs
#define OFFSET_FREQ 100 // permet d'avoir un cycle de 20ms pour le signal du servo
#define GAUCHE 150 // voir la génération du signal sur le timer 0, correspond à ~15ms à l'état haut par cycle
#define DROITE 128 // correspond à 5ms à l'état haut
#define JMP 5//sauts entre deux valeurs de direction

typedef Serial<0> serialPC;
typedef PWM<0,ModeFastPwm,1,'B'> moteur;


typedef Timer<2, 1024> freqServo;// la gestion du contrôle du servomoteur
int dir = 100;
int objectif = 0;//différent de la direction réelle, permet de rĝler la vitesse de rotation
bool etat = false;// état de la pin qui fournit le signal du servo

typedef Timer<1, 8> asserv;// la vérification de l'asservissement en direction et en vitesse

int vit = 1;//largeur du pwm pour que ça avance, fixe en suiveur de ligne

int off = 63000;

// gestion de l'historique des valeurs d'état des capteurs de ligne
int mem_cursor = 0;
int historique[TAILLE_HIST];
int moy=0;

int main(){
  // initialisation 

  serialPC::init();//la série, comme d'habitude
  serialPC::change_baudrate(9600);
  serialPC::print("Serie ok");

  cbi(DDRD,DDD6);// capteur de ligne
  cbi(DDRB,DDB0);// capteur de ligne
  for(int i=0;i<TAILLE_HIST;i++) //initialisation de l'historique comme si on était bien placé
    historique[i]=0;
  
  dir = ( GAUCHE + DROITE ) / 2;//initialisation du signal du servo
  sbi(DDRB,DDB3); // pin de contrôle de servomoteur
  freqServo::init();

  moteur::init();
  // lecture de ordres sur la série
  while(1){
    char reception[20];//port serie
    serialPC::read(reception);
    if( strcmp(reception,"asservir") == 0 ){
      asserv::init();
      vit = 200;
    }else if( strcmp(reception,"q") == 0 ){//direction
      if( dir < GAUCHE )
        dir += JMP;
      serialPC::print(dir);
    }else if( strcmp(reception,"d") == 0 ){//pareil
      if( dir > DROITE )
        dir -= JMP;
      serialPC::print(dir);
    }else if( strcmp(reception,"z") == 0 ){//vitesse+
      if( vit < 245 )
        vit += 10;
      moteur::value(vit);
      serialPC::print(vit);
    }else if( strcmp(reception,"s") == 0 ){//vitesse-
      if(vit >= 190)
        vit -= 10;
      moteur::value(vit);
      serialPC::print(vit);
    }
  }
  return 0;
}

// génère un genre de pwm qui va bien pour le servomoteur
// on remarque qu'un cycle complet dure toujours ( le timer - OFFSET_FREQ )
ISR(TIMER2_OVF_vect){
  if(etat){//si on était à l'état bas
    freqServo::value(OFFSET_FREQ - dir);
  }else{ //sinon
    freqServo::value(OFFSET_FREQ + dir);
  }
  etat = !etat;
  tbi(PORTB,PORTB3);// on bascule le pin se sortie
}

ISR(TIMER1_OVF_vect){
  static int i=0;
  // correction de la direction
  moy -= historique[mem_cursor];
  if(rbi(PINB,PINB0) ){
    serialPC::print("G");
    historique[mem_cursor] = -1; 
    serialPC::print(objectif);
    serialPC::print(dir);
  }else if(rbi(PIND,PIND6) ){
    serialPC::print("D");
    historique[mem_cursor] = 1;
    serialPC::print(objectif);
    serialPC::print(dir);
  }else{
    historique[mem_cursor] = 0;
  }
  moy += historique[mem_cursor];
  mem_cursor = (mem_cursor+1)%TAILLE_HIST;

  if(moy < -1*SEUIL )
    objectif = GAUCHE;
  if(moy > SEUIL )
    objectif = DROITE;

  if(i%30==0){
    if( dir < objectif && dir < GAUCHE ){
      dir++;
    }else if( dir > objectif && dir > DROITE){
      dir--;
    }
  }
  i++;

  // correction de la vitesse, ben pour l'instant ça n'a pas l'air nécéssaire.
  moteur::value(vit); 

  //prépare la prochaine itération
  asserv::value(off);
}
