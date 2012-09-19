#ifndef MOTEUR_HPP
#define MOTEUR_HPP

#include "pwm.hpp"
#include "safe_enum.hpp"
#include "register.hpp"
#include <libintech/utils.h>
#include "serial/serial_impl.hpp"

struct direction_def
{
    enum type{ RECULER, AVANCER};
};
typedef safe_enum<direction_def> Direction;


template<class PWM, class DirectionRegister>
class Moteur
{
    static const uint8_t TIMER_ID = PWM::ID;
    static const uint16_t PRESCALER_VALUE = PWM::PRESCALER_RATIO;
    
private:
  void direction(Direction dir)
  {
        if(dir == Direction::AVANCER){
          DirectionRegister::clear();
        }
        else if(dir == Direction::RECULER){
          DirectionRegister::set();
        }
  }
  
public:
  Moteur() : maxPWM_(255)
  {
      PWM::init();
  }
  
  void envoyerPwm(int16_t pwm)
  {   
    pwm_ = pwm;
    if (pwm>0) {
      direction(Direction::AVANCER);
      PWM::value(min(pwm, maxPWM_)); //Bridage
    }
    else {
      direction(Direction::RECULER);
      PWM::value(min(-pwm,maxPWM_)); //Bridage
    }
  }
  
  int16_t pwm()
  {
    return pwm_;
  }
  
  void maxPWM(int16_t maxPWM){
    maxPWM_ = maxPWM;
  }
  
  int16_t maxPWM() const{
    return maxPWM_;
  };
  
private:
  int16_t maxPWM_;
  int16_t pwm_;
};


#endif
