#include <stdint.h>
#include <util/delay.h>
#include <libintech/utils.h> //controle de la led
#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>

int main(){
  //initialisation led
  sbi(DDRB,DDB5);

  //port serie
  char reception[10];
  Serial<0>::init();
  Serial<0>::change_baudrate(9600);
  Serial<0>::print("initialisation de la serie");

  //lecture du pin
  cbi(DDRB,0);

  while(1){
    if(rbi(PINB,PORTB0)){
      Serial<0>::print("pas contact\n");
    }else{
      Serial<0>::print("contact\n");
    }
    _delay_ms(1000);
  }
  return 0;
}
