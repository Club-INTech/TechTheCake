#include <stdint.h>
#include <util/delay.h>
#include <libintech/utils.h> //controle de la led
#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>
#include <libintech/pwm.hpp>

typedef PWM<0,ModeFastPwm,8,'B'> truc;

int main(){
  //port serie
  char reception[10];
  Serial<0>::init();
  Serial<0>::change_baudrate(9600);
  Serial<0>::print("Serie ok");

  truc::init();
  truc::value(20);

  while(1){
      
  }
  return 0;
}
