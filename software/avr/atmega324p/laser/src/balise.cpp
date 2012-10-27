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
    
    /*
    else if (strcmp(order, "clock") == 0)
    {
        serial_pc::print(synchronisation.clock());
    }
    
    // Ping des balises
    else if (strcmp(order, "ping") == 0)
    {
        // Demande au PC l'ID de la balise à interroger
        uint8_t id;
        serial_pc::print("id ?");
        serial_pc::read(id);
        
        // ID connu ?
        if (id > BALISE_NUMBER-1)
        {
            serial_pc::print("id inconnu");
        }
        
        // Ping de la balise
        else
        {
            serial_pc::print("Envoi du ping...");
            xbee::send(balise_address[id], "c");
            char buffer[10];
            serial_pc::print("Attente réponse...");
            if (xbee::read(buffer, 1000) == xbee::READ_TIMEOUT)
            {
				serial_pc::print("timeout");
			}
			else
			{
				serial_pc::print(buffer);
            }
        }
    }*/
    
    // Ping des balises
    else if (strcmp(order, "ping") == 0)
    {
        for (uint8_t id = 0; id < BALISE_NUMBER; id++)
        {
			// Affichage de l'ID sur la série
			serial_pc::print_noln("ping ID");
			serial_pc::print_noln(id);
			serial_pc::print_noln(" ");
			
			xbee::send(balise_address[id], "?");
            uint8_t ping;
            if (xbee::read(ping, TIMEOUT) == xbee::READ_SUCCESS)
            {
				serial_pc::print(ping);
			}
			else
			{
				serial_pc::print("introuvable");
			}
		}
    }
    
    // Valeur des balises
    else if (strcmp(order, "valeur") == 0)
    {
        for (uint8_t id = 0; id < BALISE_NUMBER; id++)
        {
			// Affichage de la valeur
			serial_pc::print_noln("valeur ID");
			serial_pc::print_noln(id);
			serial_pc::print_noln(" ");
			
			xbee::send(balise_address[id], "v");
            uint16_t distance;
            uint16_t clock = timer_toptour::value();
            if (xbee::read(distance, TIMEOUT) == xbee::READ_SUCCESS)
            {
				serial_pc::print(distance);
			}
			else
			{
				serial_pc::print("introuvable");
			}
			
			// Affichage de l'offset
			serial_pc::print_noln("offset ID");
			serial_pc::print_noln(id);
			serial_pc::print_noln(" ");
			
            uint16_t offset;
            uint16_t aller_retour;
            if (xbee::read(offset, TIMEOUT) == xbee::READ_SUCCESS)
            {
				aller_retour = timer_toptour::value() - clock;
				serial_pc::print(angle(offset + aller_retour/2));
			}
			else
			{
				serial_pc::print("introuvable");
			}
		}
    }
    
    /*
    // Affichage des clocks des balises
    else if (strcmp(order, "bclock") == 0)
    {
        for (uint8_t id = 0; id < BALISE_NUMBER; id++)
        {
			// Affichage de l'ID sur la série
			serial_pc::print_noln("bclock ID");
			serial_pc::print_noln(id);
			serial_pc::print_noln(" ");
			
			xbee::send(balise_address[id], "c");
            uint32_t clock;
            if (xbee::read(clock, TIMEOUT) == xbee::READ_SUCCESS)
            {
				serial_pc::print(clock);
			}
			else
			{
				serial_pc::print("introuvable");
			}
		}
    }
    
    // Affichage des latence de transmission
    else if (strcmp(order, "latence") == 0)
    {
        for (uint8_t id = 0; id < BALISE_NUMBER; id++)
        {
			// Affichage de l'ID sur la série
			serial_pc::print_noln("latence ID");
			serial_pc::print_noln(id);
			serial_pc::print_noln(" ");
			
			uint32_t clock = synchronisation.clock();
			uint8_t buffer;
			xbee::send(balise_address[id], "c");
            if (xbee::read(buffer, TIMEOUT) == xbee::READ_SUCCESS)
            {
				serial_pc::print(synchronisation.clock() - clock);
			}
			else
			{
				serial_pc::print("introuvable");
			}
		}
    }
    
    // Affichage des l'écart des clock des balises avec la clock du serveur
    else if (strcmp(order, "bclockdiff") == 0)
    {
        for (uint8_t id = 0; id < BALISE_NUMBER; id++)
        {
			// Affichage de l'ID sur la série
			serial_pc::print_noln("clockdiff ID");
			serial_pc::print_noln(id);
			serial_pc::print_noln(" ");
			
			xbee::send(balise_address[id], "c");
            uint32_t clock;
            if (xbee::read(clock, TIMEOUT) == xbee::READ_SUCCESS)
            {
				serial_pc::print(synchronisation.clock() - clock);
			}
			else
			{
				serial_pc::print("introuvable");
			}
		}
    }
    
    // Synchronisation des balises
    else if (strcmp(order, "synchro") == 0)
    {
        // Demande au PC l'ID de la balise à interroger
        uint8_t id;
        serial_pc::print("id ?");
        serial_pc::read(id);
        
        // ID connu ?
        if (id > BALISE_NUMBER-1)
        {
            serial_pc::print("id inconnu");
        }
        
        // Lancement de la synchro
        else
        {
            synchronisation.synchroniser_serveur(balise_address[id]);
            xbee::send(balise_address[id], "c");
            uint32_t clock;
            if (xbee::read(clock, TIMEOUT) == xbee::READ_SUCCESS)
            {
				serial_pc::print(synchronisation.clock() - clock);
			}
        }
    }
    
    // Synchronisation des balises
    else if (strcmp(order, "mediane") == 0)
    {
        xbee::send(balise_address[0], "m");
        int32_t mediane;
        if (xbee::read(mediane, TIMEOUT) == xbee::READ_SUCCESS)
        {
			serial_pc::print(mediane);
		}
		else 
		{
			serial_pc::print("erreur");
		}
    }
    */
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
    
    
    
    /******Commandes de synchronisation******/
    /*
    //Ping du deuxieme avr
    if( strcmp(order, "??") == 0 )
    {
    char buffer[17];
    Serial<0>::print("Ping du second arduino");
    Serial<1>::print("?");
    Serial<1>::read(buffer);
    if( strcmp(buffer, "!") == 0 )
    {
        Serial<0>::print("Ping arduino 2 réussi");
    }
    }
    
    //Demande de synchronisation
    if( strcmp(order, "a") == 0 )
    {
    Serial<0>::print("Test de Synchronisation");
    synchronisation();
    }
    
    //Recuperation de l'horloge
    if( strcmp(order, "t") == 0 )
    {
    Serial<0>::print(clock);
    }
    
    //Recuperation des 2 horloges
    if( strcmp(order, "tt") == 0 )
    {
    char buffer[17];
    Serial<0>::print("Timers local et distant:");
    Serial<1>::print("t");
    Serial<1>::read(buffer);
    Serial<0>::print(clock);
    Serial<0>::print(buffer);
    }
    
    //Recuperation des 2 horloges en ms
    if( strcmp(order, "mm") == 0 )
    {
    float r;
    float t;
    Serial<0>::print("Timers local et distant:");
    Serial<1>::print("t");
    Serial<1>::read(t);
    r = clock / 64.0;
    Serial<0>::print(r);
    r = t / 64.0;
    Serial<0>::print(r);
    }
*/
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
int16_t Balise::angle(uint16_t offset)
{
    //temps à soustraire de l'angle pour avoir la valeur au moment du passage du laser
    int32_t diff = ((int32_t)timer_toptour::value() - (int32_t)offset);
        
    while (diff<0){ //Assez mystère...
		diff = diff + last_period_;
    }

	return diff;
    //return diff *(float)360/(float)last_period;
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

