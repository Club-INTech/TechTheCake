/**
 * \file main.cpp
 *
 * Fichier principal qui sert juste à appeler les fichiers, créer la structure Robot et faire le traitement du port série
 */

#include <util/delay.h>
#include <avr/interrupt.h>

#include <libintech/serial/serial_0_interrupt.hpp>
#include <stdint.h>
#include "robot2.h"

void setup();
static int8_t mb1 = 0;
static int8_t mb2 = 0;
static int32_t codeuse1 = 0; 
static int32_t codeuse2 = 0; 

int main()
{
	setup();
	
    Robot & robot = Robot::Instance();
	while(1)
	{
 		robot.communiquer_pc();
	}
	return 0;
}

ISR(TIMER0_OVF_vect){}
ISR(TIMER2_OVF_vect){}
ISR(TIMER1_OVF_vect, ISR_NOBLOCK){
	Robot & robot = Robot::Instance();
	
	//mise à jour des attribut stockant la distance parcourue en tic et l'angle courant en tic
	//int32_t infos[2];
	//get_all(infos);
    
    robot.mesure_distance(codeuse1 + codeuse2);
    robot.mesure_angle(codeuse1 - codeuse2);
	Serial<0>::print(codeuse1);
	Serial<0>::print(codeuse2);
	Serial<0>::print("#");

	//mise à jour du pwm envoyé aux moteurs pour l'asservissement
	robot.asservir();
	
	//calcul de la nouvelle position courante du robot, en absolu sur la table (mm et radians)
	robot.update_position();
}

// Interruption codeur 1
ISR (INT0_vect)
{
	if(mb1) --codeuse1;
	else ++codeuse1;

	mb1 = rbi(PINC,PINC0);
}

// Interruption codeur 2
ISR (INT1_vect)
{
	if(mb2) ++codeuse2;
	else --codeuse2;

	mb2 = rbi(PINC,PINC1);
}


void setup()
{
/**
 * Activer en lecture les 4 pins
 * Activer les interr INT0/1 sur front montant
 **/
	//Activation des interruptions externes
	sbi(EIMSK,INT0);
	sbi(EIMSK,INT1);

	//Activation des interruptions sur fronts montants
	//INT0
	sbi(EICRA,ISC01);
	sbi(EICRA,ISC00);
	//INT1
	sbi(EICRA,ISC11);
	sbi(EICRA,ISC10);

	//Pins en lecture des pins
	cbi(DDRD,DDD2); // Signal A moteur Gauche
	cbi(DDRD,DDD3); // Signal A moteur Droit
	cbi(DDRC,DDC0); // Signal B moteur Gauche
	cbi(DDRC,DDC1); // Signal B moteur Droit
}
