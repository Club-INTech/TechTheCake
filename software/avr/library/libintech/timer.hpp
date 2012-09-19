#ifndef TIMER_HPP
#define TIMER_HPP

#include <stdint.h>
#include <avr/io.h>

#include "utils.h"
#include "prescaler.hpp"
#include "singleton.hpp"

template<uint8_t ID>
struct TimerRegisters;

template<>
struct TimerRegisters<0>{
    static uint16_t get_TCNT(){
        return TCNT0;
    }

    static void set_TCNT( uint16_t new_tcnt){
       TCNT0 = new_tcnt;
    }
    
    static void set(){
        sbi(TIMSK0,TOIE0);
    }
};

template<>
struct TimerRegisters<1>{
    static uint16_t get_TCNT(){
        return TCNT1;
    }

    static void set_TCNT( uint16_t new_tcnt){
       TCNT1 = new_tcnt;
    }
    
    static void set(){
        sbi(TIMSK1,TOIE1);
    }
};

template<>
struct TimerRegisters<2>{
    static uint16_t get_TCNT(){
        return TCNT2;
    }

    static void set_TCNT( uint16_t new_tcnt){
       TCNT2 = new_tcnt;
    }
    
    static void set(){
        sbi(TIMSK2,TOIE2);
    }
};

#if  defined (__AVR_ATmega2560__)\
    || defined (__AVR_ATmega2561__)\
    || defined (__AVR_ATmega1280__)


template<>
struct TimerRegisters<3>{
    static uint16_t get_TCNT(){
        return TCNT3;
    }

    static void set_TCNT( uint16_t new_tcnt){
       TCNT3 = new_tcnt;
    }
    
    static void set(){
        sbi(TIMSK3,TOIE3);
    }
};

template<>
struct TimerRegisters<4>{
    static uint16_t get_TCNT(){
        return TCNT4;
    }

    static void set_TCNT( uint16_t new_tcnt){
       TCNT4 = new_tcnt;
    }
    
    static void set(){
        sbi(TIMSK4,TOIE4);
    }
};

template<>
struct TimerRegisters<5>{
    static uint16_t get_TCNT(){
        return TCNT5;
    }

    static void set_TCNT( uint16_t new_tcnt){
       TCNT5 = new_tcnt;
    }
    
    static void set(){
        sbi(TIMSK5,TOIE5);
    }
};

#endif

template<uint8_t ID_,uint16_t PRESCALER_RATIO_>
class Timer
{
    
public:
  static const uint8_t ID = ID_;
  static const uint16_t PRESCALER_RATIO = PRESCALER_RATIO_;
  
private:
  typedef Prescaler<ID,PRESCALER_RATIO> prescaler_;
  typedef TimerRegisters<ID_> register_;

public:

    static void init()
    {
        static bool is_init = false;
        if (is_init == false)
        {
            prescaler_::set();
            register_::set();
            is_init = true;
        }
    }

    
  static inline uint32_t value()
  {
      return register_::get_TCNT();
  }

  static inline void value(uint32_t new_value)
  {
      register_::set_TCNT(new_value);
  }
  
  static inline void disable()
  {
      Prescaler<ID_,0>::set();
  }
  
  static inline void enable()
  {
      prescaler_::set();
  }
  
};

#endif
