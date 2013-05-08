#include "balise.h"

Balise::Balise():
    motor_control(20,2.5,0.048),
    last_period_(0)
{
    
    // -----------------------
    // Liaison série
    // -----------------------
    // UART0
    serial_pc::init();
    serial_pc::change_baudrate(ROBOT_BAUDRATE);
    serial_pc::activer_acquittement(true);
    
    // UART1 (Xbee)
    xbee::init();
    xbee::change_baudrate(BALISE_BAUDRATE);
    
    // -----------------------
    // Compte-tour
    // -----------------------
    
    // Initialisation du timer
    timer_toptour::init();
    
    // Input sur INT2 = PB2
    cbi(DDRB,PORTB2);
    
    // Pull-up activée sur INT2
    sbi(PORTB,PORTB2);
    
    // Interruption sur front montant
    sbi(EICRA,ISC21);
    sbi(EICRA,ISC20);
    sbi(EIMSK,INT2);
    
    // -----------------------
    // Moteur
    // -----------------------
    
    // Codeuse A/B en input
    cbi(DDRC, DDC0);
    cbi(DDRC, DDC1);
    
    // Pull-up activée
    sbi(PORTC,PORTC0);
    sbi(PORTC,PORTC1);
    
    // Interruptions codeuse sur PORTC
    // A = PCINT17
    // B = PCINT16
    sbi(PCMSK2, PCINT16);
    sbi(PCMSK2, PCINT17);
    sbi(PCICR, PCIE2);
    
    timer_control::init();
    
    motor.maxPWM(150);
    motor_control.consigne(DEFAULT_SPEED_ORDER);
    
    motor_off();
    
    // -----------------------
    // Alimentation des lasers
    // -----------------------
    
    // Attention, ici DIR est un créneau et PWM est constant
    
    // Pin PWM en output
    sbi(DDRB,PORTB0);
    
    // Pin DIR pour alimenter les lasers
    pwm_laser::init();
	pwm_laser::value(127);

    // -----------------------
    // Diode debug
    // -----------------------

    sbi(DDRD,PORTD7);

    // -----------------------
    // Interruptions
    // -----------------------
    
    sei();
}

void Balise::execute(char *order)
{
    // Ping
    if (strcmp(order, "?") == 0)
    {
        serial_pc::print(PING_ID);
    }
    
    /*
    else if (strcmp(order, "pwm") == 0)
    {
        int16_t pwm;
        serial_pc::print("valeur du pwm:");
        serial_pc::read(pwm);
        serial_pc::write("nouveau pwm fixé à ");
        serial_pc::print(pwm);
        moteur.envoyerPwm(pwm);
    }
    */
    
    else if (strcmp(order, "pwm") == 0)
    {
        serial_pc::print(pwm_);
    }
    
    else if (strcmp(order, "err") == 0)
    {
        serial_pc::print(motor_control.erreur());
    }
    
    else if (strcmp(order, "speed_order") == 0)
    {
		int16_t order;
        serial_pc::print("nouvelle consigne:");
        serial_pc::read(order);
        motor_control.consigne(order);
        serial_pc::write("nouvelle consigne fixée à ");
        serial_pc::print(order);
    }
    
    // Ping d'une balise
    else if (strcmp(order, "ping") == 0)
    {
        serial_pc::print("ID ?");
        
        uint8_t id;
        serial_pc::read(id);
        
        xbee::send(balise_address[id], "?");
        uint8_t ping;
        xbee_address source_address;
        uint8_t signal_strength;
        
        if (xbee::read(ping, source_address, signal_strength, TIMEOUT) == xbee::READ_SUCCESS)
        {
            // Identifiant et adresse de la balise
            serial_pc::write("réponse: ");
            serial_pc::write(ping);
            serial_pc::write(", adresse: ");
            serial_pc::write(source_address);
				
            // Force du signal
            serial_pc::write(", signal: -");
            serial_pc::write(signal_strength);
            serial_pc::write("dBm (");
            serial_pc::write(signal_strength * -100 / 92 + 100);
            serial_pc::write("%)");
            serial_pc::send_ln();
        }
        else
        {
            serial_pc::print("NO_RESPONSE");
        }
    }
    
    // Ping de toutes les balises
    else if (strcmp(order, "ping_all") == 0)
    {
        for (uint8_t id = 0; id < BALISE_NUMBER; id++)
        {
			xbee::send(balise_address[id], "?");
            uint8_t ping;
            xbee_address source_address;
            uint8_t signal_strength;
            if (xbee::read(ping, source_address, signal_strength, TIMEOUT) == xbee::READ_SUCCESS)
            {
				// Identifiant et adresse de la balise
				serial_pc::write("réponse: ");
				serial_pc::write(ping);
				serial_pc::write(", adresse: ");
				serial_pc::write(source_address);
				
				// Force du signal
				serial_pc::write(", signal: -");
				serial_pc::write(signal_strength);
				serial_pc::write("dBm (");
				serial_pc::write(signal_strength * -100 / 92 + 100);
				serial_pc::write("%)");
				serial_pc::send_ln();
			}
			else
			{
				serial_pc::print("aucune réponse");
			}
		}
    }
    
    // Calcul du latence de transmission
    else if (strcmp(order, "latence") == 0)
    {
        if (last_period() == 0)
        {
            serial_pc::print("Le moteur doit être allumé pour le calcul de latence");
            return;
        }
        
        for (uint8_t id = 0; id < BALISE_NUMBER; id++)
        {			
			// Temps avant transmission
			uint16_t clock1 = timer_toptour::value();
			
			xbee::send(balise_address[id], "?");
			
			// Temps après transmission
			uint16_t clock2 = timer_toptour::value();
            uint32_t buffer;
            
            if (xbee::read(buffer, TIMEOUT) == xbee::READ_SUCCESS)
            {
				// Temps après réception
				uint16_t clock3 = timer_toptour::value();
				
				int16_t transmit_time = (clock2 < clock1) ? clock2 - clock1 + last_period() : clock2 - clock1;
				int16_t reception_time = (clock3 < clock2) ? clock3 - clock2 + last_period() : clock3 - clock2;
				int16_t total_time = (clock3 < clock1) ? clock3 - clock1 + last_period() : clock3 - clock1;

				serial_pc::write("émission: ");
				serial_pc::write(transmit_time);
				serial_pc::write(", réception: ");
				serial_pc::write(reception_time);
				serial_pc::write(", total: ");
				serial_pc::print(total_time);
			}
			else
			{
				serial_pc::print("aucune réponse");
			}
		}
    }
    
    // Valeur des balises
    else if (strcmp(order, "value") == 0)
    {
        serial_pc::print("ID ?");
        
        uint8_t id;
        serial_pc::read(id);
        
        uint16_t offset_;
        uint8_t distance_;
        uint32_t value;
        float angle_;

        // Envoi d'une demande de valeur
		xbee::send(balise_address[id], "v");
            
        // Calcul du temps d'aller retour
        // ! Attention ! Ne marche que si le moteur tourne
        uint16_t clock1 = timer_toptour::value();
            
        if (xbee::read(value, TIMEOUT) == xbee::READ_SUCCESS)
        {
            // Calcul de l'aller retour
			uint16_t clock2 = timer_toptour::value();
				
			// Décodage de la transmission
			offset_ = value >> 8;
			distance_ = (value << 24) >> 24;
				
			int16_t aller_retour = clock2 - clock1;
			
			// Cas où le timer est réinitialisé en passant devant l'aimant pendant la transmission
			if (clock2 < clock1)
			{
                aller_retour += last_period();
			}

			angle_ = angle(offset_ + aller_retour);
				
			// Suppression des valeurs si pas assez récente
			if (offset_ == 0 || offset_ >= last_period())
			{
				serial_pc::print("OLD_VALUE");
                serial_pc::print("OLD_VALUE");
                return;
			}
            
            // Lasers non vus par la balise
            if (distance_ == 0)
            {
                serial_pc::print("UNVISIBLE");
                serial_pc::print("UNVISIBLE");
                return;
            }
            
            // Affichage de la distance
            serial_pc::print(distance_);
            serial_pc::print(angle_, 3);
		}
		else
		{
			serial_pc::print("NO_RESPONSE");
            serial_pc::print("NO_RESPONSE");
		}
    }
    
    // Allumer les lasers
    else if (strcmp(order, "laser_on") == 0)
    {
		laser_on();
		/*
        if (last_period() > 0)
        {
            laser_on();
        }
        else
        {
            serial_pc::print("Le moteur n'est pas allumé");
        }*/
    }
    
    // Eteindre les lasers
    else if (strcmp(order, "laser_off") == 0)
    {
        laser_off();
    }
    
    // Allumer le moteur
    else if (strcmp(order, "motor_on") == 0)
    {
        motor_on();
    }
    
    // Arreter le moteur
    else if (strcmp(order, "motor_off") == 0)
    {
        motor_off();
        
        // Force l'extinction des lasers pour éviter une surchauffe
        laser_off();
    }
    
    // Vitesse actuelle du moteur
    else if(strcmp(order, "speed") == 0)
    {
        serial_pc::print(last_period());
    }
    
    // Fréquence du moteur
    else if(strcmp(order, "freq") == 0)
    {
		float freq = (last_period() == 0) ? 0. : (float)F_CPU / ((float)last_period() * 64.);
        serial_pc::print(freq, 1);
    }
    
    // Valeur de la codeuse du moteur
    else if(strcmp(order, "codeuse") == 0)
    {
		serial_pc::print(encoder);
    }
}

// -----------------------
// Controle du top tour
// -----------------------

/**
 * Retourne la dernière période mesurée de la tourelle
 * 
 */
uint16_t Balise::last_period()
{
    return last_period_;
}

/**
 * Met à jour la dernière periode mesurée
 * 
 */
void Balise::last_period(uint16_t period)
{
    last_period_ = period;
}

/**
 * Retourne l'angle des lasers à une certaine date, en degrés
 * 
 * Attention: valeur fausse tant que le moteur n'a pas une vitesse suffisante 
 * pour éviter l'overflow du timer top-tour
 * 
 */
float Balise::angle(int32_t offset)
{
    // Temps à soustraire de l'angle pour avoir la valeur au moment du passage du laser
    int32_t t0 = ((int32_t)timer_toptour::value() - offset);
    
    // En cas d'offset grand, le moteur a pu faire plusieurs tours
    // Approximation sur la période, considérée comme constante
    while (t0 < 0) {
		t0 += last_period();
    }
    
    // Angle sur [0, 2*Pi]
    float angle = (float)t0 * 2 * PI / (float)last_period();
    
    // Soustraction de l'angle pour ramener l'origine
    angle -= ANGLE_ORIGIN_OFFSET;
    if (angle < 0)
    {
        angle += 2 * PI;
    }
    else if (angle > 2 * PI)
    {
        angle -= 2 * PI;
    }
    
    // Angle sur [-Pi, Pi]
    angle -= PI;
	
	return angle;
}

// -----------------------
// Controle des lasers
// -----------------------
    
void Balise::laser_on()
{
    // Activation du timer PWM pour DIR
	pwm_laser::value(127);
    
    // Pin PWM du pont H à 5V
    sbi(PORTB,PORTB0);
}

void Balise::laser_off()
{
    // Désactivation du timer PWM pour DIR
	pwm_laser::value(0);
    
    // Pin PWM du pont H à 0V
    cbi(PORTB,PORTB0);
}

// -----------------------
// Controle du moteur
// -----------------------

void Balise::motor_on()
{
    timer_control::enable();
}

void Balise::motor_off()
{
    timer_control::disable();
    pwm_ = 0;
    motor.envoyerPwm(0);
}

void Balise::control(int32_t current_speed)
{
	pwm_ = motor_control.pwm(current_speed);
	motor.envoyerPwm(pwm_);
}

// -----------------------
// Controle des diodes
// -----------------------

void Balise::diode_on()
{
    sbi(PORTD,PORTD7);
}

void Balise::diode_off()
{
    cbi(PORTD,PORTD7);
}

void Balise::diode_blink()
{
    diode_blink(50, 8);
}

void Balise::diode_blink(uint16_t period, uint8_t number)
{
    for (uint8_t i = 1; i <= number; i++)
    {
        diode_on();
        for (uint16_t i = 1; i <= period; i++) _delay_ms(1);
        diode_off();
        for (uint16_t i = 1; i <= period; i++) _delay_ms(1);
    }
}



