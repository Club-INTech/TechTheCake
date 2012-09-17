#include "balise.h"

Balise::Balise()  
{
    // -----------------------
    // Liaison série
    // -----------------------
    
    // UART0
    serial_pc::init();
    serial_pc::change_baudrate(ROBOT_BAUDRATE);
    
    // UART1
    serial_radio::init();
    serial_radio::change_baudrate(BALISE_BAUDRATE);
    
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
    
    
    
    // -----------------------
    // Alimentation des lasers
    // -----------------------
    
    // Attention, ici DIR est un créneau et PWM est constant
    
    // Pin PWM Laser en output
    sbi(DDRB,PORTB3);
    
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
            
        }
    }
    
    // Allumer les lasers
    else if (strcmp(order, "laser_on") == 0)
    {
        if (max_counter() > 0)
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
    else if(strcmp(order, "motor_speed") == 0)
    {
        serial_pc::print(max_counter());
    }
}

void Balise::max_counter(uint16_t valeur)
{
    max_counter_ = valeur;
}

uint16_t Balise::max_counter()
{
    return max_counter_;
}

/**
 * Retourne l'angle que font les lasers actuellement, en degrés
 * 
 * Attention: valeur fausse tant que le moteur n'a pas une vitesse suffisante 
 * pour éviter l'overflow du timer top-tour
 * 
 */
int16_t Balise::get_angle(uint16_t offset)
{
    if (max_counter_ == 0) return -1;
    
    //temps à soustraire de l'angle pour avoir la valeur au moment du passage du laser
    int32_t diff = ((int32_t)timer_toptour::value() - (int32_t)offset*4/5);
        
    while(diff<0){ //Assez mystère...
      diff+=(int32_t)max_counter_;
    }

    return diff *(float)360/(float)max_counter_ ;
}

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

void Balise::motor_on()
{
    
}

void Balise::motor_off()
{
    
}

void Balise::diode_on()
{
    sbi(PORTD,PORTD7);
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

void Balise::diode_off()
{
    cbi(PORTD,PORTD7);
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

