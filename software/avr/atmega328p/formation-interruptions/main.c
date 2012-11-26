#include <stdint.h>
#include <util/delay.h>
#include <avr/interrupt.h>
#include <libintech/utils.h>
#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>

int main(){
  //initialisation led
  sbi(DDRB,DDB5);

  //port serie
  Serial<0>::init();
  Serial<0>::change_baudrate(9600);
  Serial<0>::print("initialisation de la serie");

  //passage d'un pin en ouput
  sbi(DDRD,DDD6);
  cbi(PORTD,PORTD6);//éteint

  //activation des interruptions
  sei();
  sbi(EICRA,ISC01);//Configuration front montant
  sbi(EICRA,ISC00);
  sbi(EICRA,ISC11);//Configuration front montant
  sbi(EICRA,ISC10);
  sbi(EIMSK,INT0);//Activation proprement dite
  sbi(EIMSK,INT1);
  while(1){
    Serial<0>::print("tout vas bien.");
    tbi(PORTD,PORTD6);
    _delay_ms(1000);
  }
  return 0;
}

ISR(INT0_vect){
  Serial<0>::print("0");
}
ISR(INT1_vect){
  Serial<0>::print("1");
}
