#include <stdint.h>
//#include <libintech/utils.h>
#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>
#include <util/delay.h>
//#include <avr/io.h>

int main(){
  char reception[10];
  Serial<0>::init();
  Serial<0>::change_baudrate(9600);
  Serial<0>::print("Bonjour, comment allez vous?");
  while(1){
    Serial<0>::read(reception);
    if(strcmp(reception,"bien")==0){
    Serial<0>::print("tant mieux");
    }else{
    Serial<0>::print("dommage, crève charogne!");
    }
  }
  return 0;
}
