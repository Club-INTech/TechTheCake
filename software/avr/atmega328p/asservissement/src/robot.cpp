#include "robot.h"
#include <avr/eeprom.h>

// Constructeur avec assignation des attributs
Robot::Robot() : 	
			x_(0)
			,y_(0)
			,angle_origine_(0.0)
			,etat_rot_(true)
			,etat_tra_(true)
			,translation(0.75,3.5,0.0)
			,rotation(0.9,3.5,0.0)
{
	TWI_init();
	serial_t_::init();
	TimerCounter_t::init();
	serial_t_::change_baudrate(9600);

	changer_orientation(PI);
    
    // Chargement en mémoire des valeurs dans l'EEPROM
    translation.kp(eeprom_read_float((float*)(0)));
    translation.kd(eeprom_read_float((float*)(1)));
    rotation.kp   (eeprom_read_float((float*)(2)));
    rotation.kd   (eeprom_read_float((float*)(3)));
    translation.valeur_bridage(eeprom_read_dword((uint32_t*)(4)));
    rotation.valeur_bridage   (eeprom_read_dword((uint32_t*)(5)));
}

void Robot::asservir()
{
	int32_t pwmTranslation;
	int32_t pwmRotation;

	if (etat_rot_)
		pwmRotation = rotation.pwm(mesure_angle_,10);
	else
		pwmRotation = 0;

	if(etat_tra_)
		pwmTranslation = translation.pwm(mesure_distance_,20);
	else
		pwmTranslation = 0;
	
	moteurGauche.envoyerPwm(pwmTranslation - pwmRotation);
	moteurDroit.envoyerPwm(pwmTranslation + pwmRotation);
	
}

//calcul de la nouvelle position courante du robot, en absolu sur la table (mm et radians)
void Robot::update_position()
{
	static int32_t last_mesure_distance = 0;
	static int32_t last_mesure_angle = 0;
	
	int16_t delta_distance_tic = mesure_distance_ - last_mesure_distance;
	int16_t delta_angle_tic = mesure_angle_ - last_mesure_angle;
	
	float delta_distance_mm = delta_distance_tic * CONVERSION_TIC_MM;
	float delta_angle_rad = delta_angle_tic * CONVERSION_TIC_RADIAN;
	
	x_ += ( delta_distance_mm * cos_table(angle()) );
	y_ += ( delta_distance_mm * sin_table(angle()) );
	
	angle(delta_angle_rad);
	
	last_mesure_distance = mesure_distance_;
	last_mesure_angle = mesure_angle_;
}

////////////////////////////// PROTOCOLE SERIE ///////////////////////////////////
void Robot::communiquer_pc(){
	char buffer[17];
	serial_t_::read(buffer);

	//ping
	if(strcmp(buffer,"?") == 0)
	{
		serial_t_::print(0);
	}
	
	//maj des constantes d'asservissement en rotation
	else if(strcmp(buffer,"crp") == 0)
	{
		float valeur;
		serial_t_::read(valeur);
		rotation.kp(valeur);
	}
	else if(strcmp(buffer,"crd") == 0)
	{
		float valeur;
		serial_t_::read(valeur);
		rotation.kd(valeur);
	}
	else if(strcmp(buffer,"cri") == 0)
	{
		float valeur;
		serial_t_::read(valeur);
		rotation.ki(valeur);
	}
	else if(strcmp(buffer,"crm") == 0)
	{
		float valeur;
		serial_t_::read(valeur);
		rotation.valeur_bridage(valeur);
	}

	//maj des constantes d'asservissement en translation
	else if(strcmp(buffer,"ctp") == 0)
	{
		float valeur;
		serial_t_::read(valeur);
		translation.kp(valeur);
	}
	else if(strcmp(buffer,"ctd") == 0)
	{
		float valeur;
		serial_t_::read(valeur);
		translation.kd(valeur);
	}
	else if(strcmp(buffer,"cti") == 0)
	{
		float valeur;
		serial_t_::read(valeur);
		translation.ki(valeur);
	}
	else if(strcmp(buffer,"ctm") == 0)
	{
		float valeur;
		serial_t_::read(valeur);
		translation.valeur_bridage(valeur);
	}

	//maj de la position absolue du robot
	else if(strcmp(buffer,"cx") == 0)
	{
		serial_t_::read(x_);
	}
	else if(strcmp(buffer,"cy") == 0)
	{
		serial_t_::read(y_);
	}
	else if(strcmp(buffer,"co") == 0)
	{
		float valeur;
		serial_t_::read(valeur);
		changer_orientation(valeur);
	}
	
	//renvoi de la position absolue du robot
	else if(strcmp(buffer,"ex") == 0)
	{
		serial_t_::print((int32_t)x_);
	}
	else if(strcmp(buffer,"ey") == 0)
	{
		serial_t_::print((int32_t)y_);
	}
	else if(strcmp(buffer,"eo") == 0)
	{
		serial_t_::print((int32_t)(angle() * 1000));
	}

	//ordre de translation
	else if(strcmp(buffer,"d") == 0)
	{
		float valeur;
		serial_t_::read(valeur);
		translater(valeur);
	}

	//ordre de rotation
	else if(strcmp(buffer,"t") == 0)
	{
		float valeur;
		serial_t_::read(valeur);
		tourner(valeur);
	}

	//ordre d'arret (asservissement aux angle et position courants)
	else if(strcmp(buffer,"stop") == 0)
	{
		stopper();
	}

	//stopper asservissement rotation/translation
	else if(strcmp(buffer,"cr0") == 0)
	{
		etat_rot_ = false;
	}
	else if(strcmp(buffer,"ct0") == 0)
	{
		etat_tra_ = false;
	}

	//démarrer asservissement rotation/translation
	else if(strcmp(buffer,"cr1") == 0)
	{
		etat_rot_ = true;
	}
	else if(strcmp(buffer,"ct1") == 0)
	{
		etat_tra_ = true;
	}

	//demande de la position courante
	else if(strcmp(buffer,"pos") == 0)
	{
		serial_t_::print((int32_t)x_);
		serial_t_::print((int32_t)y_);
	}

	// Changement de la vitesse de translation
	else if(strcmp(buffer,"ctv") == 0)
	{
        float kp, kd;
        uint32_t brid;
        
        serial_t_::read(kp);
        serial_t_::read(kd);
        serial_t_::read(brid);
        
        changerVitesseTra(kp, kd, brid);
	}
	
	// Changement de la vitesse de rotation
	else if(strcmp(buffer,"crv") == 0)
	{
        float kp, kd;
        uint32_t brid;
        
        serial_t_::read(kp);
        serial_t_::read(kd);
        serial_t_::read(brid);
        
        changerVitesseRot(kp, kd, brid);
	}
	
	//envoi des paramètres pour l'évaluation des conditions de blocage
	else if(strcmp(buffer,"?bloc") == 0)
	{
		serial_t_::print((int16_t)abs(moteurGauche.pwm()));
		serial_t_::print((int16_t)abs(moteurDroit.pwm()));
		serial_t_::print((int16_t)rotation.erreur_d());
		serial_t_::print((int16_t)translation.erreur_d());
	}
	
	//envoi des paramètres pour l'évaluation des conditions d'arret
	else if(strcmp(buffer,"?arret") == 0)
	{
		serial_t_::print((int16_t)abs(rotation.erreur()));
		serial_t_::print((int16_t)abs(translation.erreur()));
		serial_t_::print((int16_t)rotation.erreur_d());
		serial_t_::print((int16_t)translation.erreur_d());
	}
	
	// Réécriture dans l'eeprom
	else if (strcmp(buffer, "eeprom") == 0)
    {
        float kp_rot, kd_rot, kp_tra, kd_tra;
        uint32_t val_brid_tra, val_brid_rot;
       
        // Acquisition
        serial_t_::read(kp_tra);
        serial_t_::read(kd_tra);
        serial_t_::read(kp_rot);
        serial_t_::read(kd_rot);
        serial_t_::read(val_brid_tra);
        serial_t_::read(val_brid_rot);
        
        // Enregistrement en local
        translation.kp(kp_tra);
        translation.kd(kd_tra);
        rotation.kp   (kp_rot);
        rotation.kd   (kd_rot);
        translation.valeur_bridage(val_brid_tra);
        rotation.valeur_bridage(val_brid_rot);
        
        // Enregistrement dans l'EEPROM
        eeprom_write_float((float*)(0), kp_tra);
        eeprom_write_float((float*)(1), kd_tra);
        eeprom_write_float((float*)(2), kp_rot);
        eeprom_write_float((float*)(3), kd_rot);
        eeprom_write_dword((uint32_t*)(4), val_brid_tra);
        eeprom_write_dword((uint32_t*)(5), val_brid_rot);
    }
}
////////////////////////////// VITESSES /////////////////////////////

// Changement de la vitesse de translation
void Robot::changerVitesseTra(float kp, float kd, uint32_t brid)
{
    translation.valeur_bridage(brid);
    translation.kp(kp);
    translation.kd(kd);
    
    // Enregistrement dans l'EEPROM
    eeprom_write_float((float*)(0), kp);
    eeprom_write_float((float*)(1), kd);
    eeprom_write_dword((uint32_t*)(4), brid);
    
}
void Robot::changerVitesseRot(float kp, float kd, uint32_t brid)
{
	rotation.valeur_bridage(brid);
	rotation.kp(kp);
	rotation.kd(kd);
    
    // Enregistrement dans l'EEPROM
    eeprom_write_float((float*)(2), kp);
    eeprom_write_float((float*)(3), kd);
    eeprom_write_dword((uint32_t*)(5), brid);
}
////////////////////////////// ACCESSEURS /////////////////////////////////
void Robot::mesure_angle(int32_t new_angle)
{
	mesure_angle_ = new_angle;
}
void Robot::mesure_distance(int32_t new_distance)
{
	mesure_distance_ = new_distance;
}
float Robot::angle(float delta_angle_rad)
{
	static float angle_radian = angle_origine_;
	angle_radian += delta_angle_rad;
	return angle_radian;
}
////////////////////////// MÉTHODES DE CALCUL ET DE DÉPLACEMENT ////////////////////////////
//calcule l'angle le plus court pour atteindre angle à partir de angleBkp (ie sans faire plusieurs tours)
// le déplacement DOIT etre relatif à angleBkp, et non pas sur un intervalle défini genre [0,2*PI[, 
// puisque angleBkp a enregistré les tours du robot sur lui meme, depuis l'initialisation.
int32_t Robot::angle_optimal(int32_t angle, int32_t angleBkp)
{
	while (angle > angleBkp+PI_TIC)
		angle -= 2*PI_TIC;
	while (angle <= angleBkp-PI_TIC)
		angle += 2*PI_TIC;
	return angle;
}

//attribuer une nouvelle orientation au robot, en radian.
// Les valeurs en tic (mesure_angle_) ne sont pas modifiées, car liées aux déplacement des codeuses.
void Robot::changer_orientation(float new_angle)
{
	angle_origine_ = new_angle - (angle() - angle_origine_);
	angle(new_angle - angle());
}

void Robot::tourner(float angle)
{
	float angle_tic = (angle - angle_origine_)/CONVERSION_TIC_RADIAN;
	rotation.consigne(angle_optimal( angle_tic, mesure_angle_ ));
	//attendre un tour de timer avant de continuer (éventuel problème avec attribut volatile)
	while(compteur.value()>0){ asm("nop"); }
}

void Robot::translater(float distance)
{
	translation.consigne(translation.consigne()+distance/CONVERSION_TIC_MM);
	//attendre un tour de timer avant de continuer (éventuel problème avec attribut volatile)
	while(compteur.value()>0){ asm("nop"); }
}

//pour stopper le robot on l'asservit sur sa position courante
void Robot::stopper()
{
	rotation.consigne(mesure_angle_);
	translation.consigne(mesure_distance_);
}