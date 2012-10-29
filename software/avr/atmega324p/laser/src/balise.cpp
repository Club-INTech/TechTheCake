#include "balise.h"

Balise::Balise():
    last_period_(0) 
{
    
    // -----------------------
    // Liaison série
    // -----------------------
    // UART0
    serial_pc::init();
    serial_pc::change_baudrate(ROBOT_BAUDRATE);
    
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
    
    // Interruptions codeuse sur PORTC
    // A = PCINT17
    // B = PCINT16
    sbi(PCMSK2, PCINT16);
    sbi(PCMSK2, PCINT17);
    sbi(PCICR, PCIE2);

	// Output PWM et DIR
    sbi(DDRD,PORTD6);
    sbi(DDRD,PORTD7);
    
    pwm_moteur::init();
    motor_off();
    
    // -----------------------
    // Alimentation des lasers
    // -----------------------
    
    // Attention, ici DIR est un créneau et PWM est constant
    
    // Pin PWM en output
    sbi(DDRB,PORTB3);
    
    // Seuil pour le PWM des lasers (cf formule datasheet)
    // f_wanted = 20 000 000 / (2 * prescaler * (1 + OCR0A))
    // Valeur fixée = 48KHz (ne pas aller au dessus, le pont redresseur chauffe sinon)
    //pwm_laser::init();
    //pwm_laser::value(170);

    // Pin DIR Laser en output
    sbi(DDRB,PORTB4);
    
    // Réglage pin DIR en PWM mode CTC
    cbi(TCCR0A,WGM00);
    sbi(TCCR0A,WGM01);
    cbi(TCCR0B,WGM02);
    
    // Toggle OCR0B
    sbi(TCCR0A,COM0B0);
    cbi(TCCR0A,COM0B1);
    
    // Seuil pour le PWM (cf formule datasheet)
    // f_wanted = 20 000 000 / (2 * prescaler * (1 + OCR0A))
    // Valeur fixée = 48KHz (ne pas aller au dessus, le pont redresseur chauffe sinon)
    OCR0A = 170;

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
        diode_blink();
    }
    
    else if (strcmp(order, "pwm") == 0)
    {
        uint16_t pwm;
        serial_pc::print("valeur du pwm:");
        serial_pc::read(pwm);
        pwm_moteur::value(pwm);
    }
    
    // Ping des balises
    else if (strcmp(order, "ping") == 0)
    {
        for (uint8_t id = 0; id < BALISE_NUMBER; id++)
        {
			// Affichage de l'ID sur la série
			serial_pc::write("ping ID");
			serial_pc::write(id);
			serial_pc::write(" ");
			
			xbee::send(balise_address[id], "?");
            uint8_t ping;
            uint16_t source_address;
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
    
    // Valeur des balises
    else if (strcmp(order, "valeur") == 0)
    {
        for (uint8_t id = 0; id < BALISE_NUMBER; id++)
        {
            // Calcul du temps d'aller retour
            // ! Attention ! Ne marche que si le moteur tourne
            uint16_t clock1 = timer_toptour::value();
            uint16_t aller_retour;
            uint16_t offset_;
            uint8_t distance_;
            float angle_;
            
            // Envoi d'une demande de valeur
			xbee::send(balise_address[id], "v");
            
            if (xbee::read(distance_, TIMEOUT) == xbee::READ_SUCCESS && xbee::read(offset_, TIMEOUT) == xbee::READ_SUCCESS)
            {
				// Calcul de l'aller retour
				uint16_t clock2 = timer_toptour::value();
				aller_retour = clock2 - clock1;
				
				// Cas où le timer est réinitialisé en passant devant l'aimant pendant la transmission
				if (clock2 < clock1)
				{
					aller_retour += last_period();
				}
				
				angle_ = angle(offset_ + aller_retour/2);
				
				// Suppression des valeurs si pas assez récente
				if (offset_ == 0 || offset_ >= last_period())
				{
					distance_ = 0;
					angle_ = 0;
				}
				
				// Affichage de la distance
				serial_pc::print_noln("distance ID");
				serial_pc::print_noln(id);
				serial_pc::print_noln(" ");
				serial_pc::print(distance_);
				
				// Affichage de l'angle
				serial_pc::print_noln("angle ID");
				serial_pc::print_noln(id);
				serial_pc::print_noln(" ");
				serial_pc::print(angle_, 1);
			}
			else
			{
				serial_pc::print("introuvable");
			}
		}
    }
    
    // Allumer les lasers
    else if (strcmp(order, "laser_on") == 0)
    {
        if (last_period() > 0)
        {
            laser_on();
        }
        else
        {
            serial_pc::print("Le moteur n'est pas allumé");
        }
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
		serial_pc::print(codeur);
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
 * Retourne l'angle que font les lasers actuellement, en degrés
 * 
 * Attention: valeur fausse tant que le moteur n'a pas une vitesse suffisante 
 * pour éviter l'overflow du timer top-tour
 * 
 */
float Balise::angle(int32_t offset)
{
    //temps à soustraire de l'angle pour avoir la valeur au moment du passage du laser
    int32_t t0 = ((int32_t)timer_toptour::value() - offset);
    
    while (t0 < 0) {
		t0 += last_period();
    }
	
	return (float)t0 * 360.0 / (float)last_period();
}

// -----------------------
// Controle des lasers
// -----------------------
    
void Balise::laser_on()
{
    // Activation du timer PWM pour DIR
    cbi(TCCR0B,CS02);
    cbi(TCCR0B,CS01);
    sbi(TCCR0B,CS00);
    
    // Pin PWM à 5V
    sbi(PORTB,PORTB3);
}

void Balise::laser_off()
{
    // Désactivation du timer PWM pour DIR
    cbi(TCCR0B,CS02);
    cbi(TCCR0B,CS01);
    cbi(TCCR0B,CS00);
    
    // Pin PWM à 0V
    cbi(PORTB,PORTB3);
}

// -----------------------
// Controle du moteur
// -----------------------

void Balise::motor_on()
{
    pwm_moteur::value(40);
}

void Balise::motor_off()
{
    pwm_moteur::value(0);
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

/**
 * Renvoie un entier correspondant au codage suivant :
 * 
 * angle en degrés [0,512] sur les 9 bits de poids faible
 * distance en mm [0,4096] sur les 12 bits (ou plus) suivants
 * 
 */
uint32_t Balise::format_value(uint16_t distance, uint16_t angle)
{
    uint32_t value = (uint32_t) distance << 9;
    value = value | (uint32_t) angle;
    
    return value;
}

// void Balise::asservir(int32_t vitesse_courante)
// {
//  int16_t pwm = asservissement_moteur_.pwm(vitesse_courante);
//  Serial<0>::print(pwm);
//  moteur_.envoyerPwm(pwm);
// }

