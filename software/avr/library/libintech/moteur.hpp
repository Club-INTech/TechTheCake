/** 
 * Classe de contrôle d'un moteur (PWM et Direction)
 * 
 * @author Philippe TILLET phil.tillet@gmail.com
 * @author Marc BLANC-PATIN marc.blancpatin@gmail.com
 * 
 */

#ifndef MOTEUR_HPP
#define MOTEUR_HPP

#include "pwm.hpp"
#include "safe_enum.hpp"
#include "register.hpp"
#include "utils.h"
#include "serial/serial_impl.hpp"

struct direction_def {

    enum type {
        RECULER, AVANCER
    };
};
typedef safe_enum<direction_def> Direction;

/**
 * 
 * PWM                  Timer en mode PWM utilisé pour générer le PWM du moteur (cf pwm.hpp)
 * DirectionRegister    Pin utilisé pour la sortie de la direction (cf register.hpp)
 * 
 */
template<class PWM, class DirectionRegister>
class Moteur {
    static const uint8_t TIMER_ID = PWM::ID;
    static const uint16_t PRESCALER_VALUE = PWM::PRESCALER_RATIO;

private:

    void direction(Direction dir) {
        if (dir == Direction::AVANCER) {
            DirectionRegister::clear();
        } else if (dir == Direction::RECULER) {
            DirectionRegister::set();
        }
    }

private:
    int16_t maxPWM_;
    int16_t pwm_;

public:

    Moteur() : maxPWM_(255) {
        PWM::init();
		DirectionRegister::set_output();
    }

    /**
     * Fixe la valeur du PWM du moteur, et prend en compte le signe pour la direction
     * 
     * @param pwm       Valeur du PWM ([-255,255] pour un timer 8 bit, [-65535,65535] pour un 16 bit)
     */
    void envoyerPwm(int16_t pwm) {
        pwm_ = pwm;
        if (pwm > 0) {
            direction(Direction::AVANCER);
            PWM::value(min(pwm, maxPWM_)); //Bridage
        } else {
            direction(Direction::RECULER);
            PWM::value(min(-pwm, maxPWM_)); //Bridage
        }
    }

    /**
     * @return Retourne la valeur courante du PWM
     */
    int16_t pwm() {
        return pwm_;
    }

    /**
     * Fixe le PWM max pour le moteur
     * 
     * @param maxPWM
     */
    void maxPWM(int16_t maxPWM) {
        maxPWM_ = maxPWM;
    }

    /**
     * @return Retourne la valeur du PWM max fixé pour ce moteur
     */
    int16_t maxPWM() const {
        return maxPWM_;
    };

};


#endif
