#include <stdint.h>
#include <libintech/utils.h>
#include <util/delay.h>
#include <avr/io.h>

int main(){
  //mode output pour la led
  sbi(DDRD, DDD5);
  while(1){
    //mettre du jus
    sbi(PORTD, PORTD5);
    _delay_ms(25);
    //...ou pas
    cbi(PORTD, PORTD5);
    _delay_ms(50);
  }
  return 0;
}
