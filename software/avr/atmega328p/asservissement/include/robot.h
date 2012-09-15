#ifndef robot_h
#define robot_h

#include "Cos.h"
#include "twi_master.h"

#include <stdint.h>
#include <avr/io.h>
#include <util/delay.h>

#include <libintech/asservissement.hpp>
#include <libintech/serial/serial_impl.hpp>
#include <libintech/serial/serial_0.hpp>
#include <libintech/timer.hpp>
#include <libintech/pwm.hpp>
#include <libintech/moteur.hpp>
#include <libintech/register.hpp>
#include <libintech/singleton.hpp>

#define PI 3.14159265
#define PI_TIC 4414

#define LARGEUR_ROBOT 200.0
#define LONGUEUR_TABLE 3000.0


#define CONVERSION_TIC_MM 0.10360
#define CONVERSION_TIC_RADIAN 0.0007117

class Robot : public Singleton<Robot>{
// Par défaut les attributs sont publics dans une struct


private:

	//Moteur sur le Timer 2 en FastPWM . Pont en H sur le PORTD4
	typedef Timer<2,ModeFastPwm,1> T_G;
	Moteur< T_G, AVR_PORTD<PORTD4> > moteurGauche;
	
	//Moteur sur le Timer 0 en FastPWM . Pont en H sur le port B0
	typedef Timer<0,ModeFastPwm,1> T_D;
	Moteur<T_D, AVR_PORTB<PORTB0> > moteurDroit;
	
	//Timer 1 en mode compteur, Prescaler de 1
	typedef Timer<1,ModeCounter,1> TimerCounter_t;
	TimerCounter_t compteur;
	
	typedef Serial<0> serial_t_;
	
	float x_;
	float y_;
	float angle_origine_;
	
	bool etat_rot_;
	bool etat_tra_;
	
	int32_t mesure_distance_;
	int32_t mesure_angle_;
	
	Asservissement translation;
	Asservissement rotation;
	
public:
	
	Robot();
	
	//gestion des mesures courantes
	void mesure_angle(int32_t); 
	void mesure_distance(int32_t); 
	float get_angle();
	
	void changer_orientation(float new_angle);
	
	void changerVitesseTra(int16_t valeur);
	void changerVitesseRot(int16_t valeur);
	
	void asservir();
	void update_position();
	void communiquer_pc();
	
	int32_t angle_optimal(int32_t angle, int32_t angleBkp);
	
	void tourner(float angle);
	void translater(float distance);

	void stopper();
};

#endif
