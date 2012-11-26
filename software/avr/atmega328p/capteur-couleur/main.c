#include <stdint.h>
#include <libintech/utils.h>
#include <util/delay.h>
#include <avr/io.h>
#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>

typedef enum {RAS,BLEU,ROUGE,INDECIS} Couleur;

int main(){
  cbi(DDRB, DDB3); //lecture de la mesure
  sbi(DDRB, DDB4); //mode output sur le pin
  sbi(DDRB, DDB5);

  Serial<0>::init();
  Serial<0>::change_baudrate(9600);
  Serial<0>::print("initialisation de la serie");

  sbi(PORTB, PORTB4);
  cbi(PORTB, PORTB5);
  Couleur couleur;
  while(1){
    couleur=RAS;
    sbi(PORTB, PORTB4);
    cbi(PORTB, PORTB5);
    _delay_ms(25);//on attend un peu
    if( !rbi(PINB, PORTB3) ){ //ROUGE, le capteur est à 0 quand il y a reception!
      couleur=ROUGE;
    }
    cbi(PORTB, PORTB4);
    sbi(PORTB, PORTB5);
    _delay_ms(25);
    if( !rbi(PINB, PORTB3) ){ //BLEU
      if(couleur==ROUGE){
        couleur=INDECIS;
      }else{
        couleur=BLEU;
      }
    }
    switch(couleur){
      case RAS:
        Serial<0>::print("ras");
        break;
      case BLEU:
        Serial<0>::print("bleu");
        break;
      case ROUGE:
        Serial<0>::print("rouge");
        break;
      case INDECIS:
        Serial<0>::print("indecis");
        break;
    }
  }
  return 0;
}

