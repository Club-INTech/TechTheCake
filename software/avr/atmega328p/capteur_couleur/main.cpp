#include <stdint.h>
#include <libintech/utils.h>
#include <util/delay.h>
#include <avr/io.h>
#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>

#define AQUITTEMENT Serial<0>::print("_")

typedef enum {RAS,BLEU,ROUGE,INDECIS} Couleur;

int main(){
  cbi(DDRB, DDB3); //lecture de la mesure couleur
  sbi(DDRB, DDB1); //sortie pour la couleur des leds
  sbi(DDRB, DDB2);

  sbi(PORTB, PORTB4);
  cbi(PORTB, PORTB5);

  Serial<0>::init();
  Serial<0>::change_baudrate(9600);
  Serial<0>::print("initialisation de la serie");

  while(1){
    char buffer[17];
    Serial<0>::read(buffer);
    AQUITTEMENT;

    if(strcmp(buffer, "?") == 0){
      Serial<0>::print("1");

    }else if(strcmp(buffer, "c") == 0){
      Couleur couleur=RAS;
      sbi(PORTB, PORTB1);
      cbi(PORTB, PORTB2);
      _delay_ms(100);//on attend un peu
      if( !rbi(PINB, PORTB3) ){ //ROUGE, le capteur est à 0 quand il y a reception!
        couleur=ROUGE;
      }
      cbi(PORTB, PORTB1);
      sbi(PORTB, PORTB2);
      _delay_ms(100);
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

  }

  return 0;
}

