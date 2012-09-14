#include "robot.h"

// Constructeur avec assignation des attributs
Robot::Robot() : 	
			couleur_('v')
			,x_(0)
			,y_(0)
			,angle_origine_(0.0)
			,etat_rot_(true)
			,etat_tra_(true)
			,est_bloque_(false)
			,translation(0.75,3.5,0.0)
			,rotation(0.9,3.5,0.0)
{
	TWI_init();
	serial_t_::init();
	TimerCounter_t::init();
	serial_t_::change_baudrate(9600);

	changer_orientation(PI);
	changerVitesseRot(2);
	changerVitesseTra(2);
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
	static int32_t last_distance = 0;
	int16_t delta_distance_tic = mesure_distance_ - last_distance;
	float delta_distance_mm = delta_distance_tic * CONVERSION_TIC_MM;
	float angle = get_angle();

	x_ += ( delta_distance_mm * cos_table(angle) );
	y_ += ( delta_distance_mm * sin_table(angle) );

	last_distance = mesure_distance_;
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
	
	//couleur du robot (utile pour l'angle_origine et le recalage)
	else if(strcmp(buffer,"ccr") == 0){
		couleur_ = 'r';
	}
	else if(strcmp(buffer,"ccv") == 0)
	{
		couleur_ = 'v';
	}
	else if(strcmp(buffer,"ec") == 0)
	{
		serial_t_::print((char)couleur_);
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
		update_position();
		serial_t_::print((int32_t)x_);
	}
	else if(strcmp(buffer,"ey") == 0)
	{
		update_position();
		serial_t_::print((int32_t)y_);
	}
	else if(strcmp(buffer,"eo") == 0)
	{
		serial_t_::print((int32_t)(get_angle() * 1000));
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

	//recalage de la position
	else if(strcmp(buffer,"recal") == 0)
	{
		recalage();
	}

	//demande d'acquittement
	else if(strcmp(buffer,"acq") == 0)
	{
		if(est_stoppe())
		{
			if(est_bloque_)
				serial_t_::print("STOPPE");
			else
				serial_t_::print("FIN_MVT");
		}
		else
			serial_t_::print("EN_MVT");
	}

	//demande de la position courante
	else if(strcmp(buffer,"pos") == 0)
	{
		update_position();
		serial_t_::print((int32_t)x_);
		serial_t_::print((int32_t)y_);
	}

	//vitesses prédéfinies
	else if(strcmp(buffer,"ctv") == 0)
	{
		int16_t valeur;
		serial_t_::read(valeur);
		changerVitesseTra(valeur);
	}
	else if(strcmp(buffer,"crv") == 0)
	{
		int16_t valeur;
		serial_t_::read(valeur);
		changerVitesseRot(valeur);
	}

}
////////////////////////////// VITESSES /////////////////////////////
void Robot::changerVitesseTra(int16_t valeur)
{
	float vb_translation[] = {60.0,100.0,200.0};
	float kp_translation[] = {0.75,0.75,0.5};
	float kd_translation[] = {2.0,2.5,4.0};
	
	translation.valeur_bridage(vb_translation[valeur-1]);
	translation.kp(kp_translation[valeur-1]);
	translation.kd(kd_translation[valeur-1]);
}
void Robot::changerVitesseRot(int16_t valeur)
{
	float vb_rotation[] = {80.0,100.0,200.0};
	float kp_rotation[] = {1.5,1.2,0.9};
	float kd_rotation[] = {2.0,3.5,3.5};
	
	rotation.valeur_bridage(vb_rotation[valeur-1]);
	rotation.kp(kp_rotation[valeur-1]);
	rotation.kd(kd_rotation[valeur-1]);
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
float Robot::get_angle()
{
	float angle_radian = mesure_angle_ * CONVERSION_TIC_RADIAN + angle_origine_;
	
	while (angle_radian > PI)
		angle_radian -= 2*PI;
	while (angle_radian <= -PI)
		angle_radian += 2*PI;
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
	angle_origine_ = new_angle - (get_angle() - angle_origine_);
}

//le robot est considéré stoppé si les vitesses sont nulles et les écarts à la consigne négligeables
bool Robot::est_stoppe()
{
	volatile bool rotation_stoppe = abs(rotation.erreur()) < 105;
	volatile bool translation_stoppe = abs(translation.erreur()) < 100;
	bool bouge_pas = rotation.erreur_d()==0 && translation.erreur_d()==0;
	return rotation_stoppe && translation_stoppe && bouge_pas;
}

void Robot::tourner(float angle)
{
	est_bloque_ = false;
	float angle_tic = (angle - angle_origine_)/CONVERSION_TIC_RADIAN;
	rotation.consigne(angle_optimal( angle_tic, mesure_angle_ ));
	//attendre un tour de timer avant de continuer (éventuel problème avec attribut volatile)
	while(compteur.value()>0){ asm("nop"); }
}

void Robot::translater(float distance)
{
	est_bloque_ = false;
	translation.consigne(translation.consigne()+distance/CONVERSION_TIC_MM);
	//attendre un tour de timer avant de continuer (éventuel problème avec attribut volatile)
	while(compteur.value()>0){ asm("nop"); }
}

//pour stopper le robot on l'asservit sur sa position courante
void Robot::stopper()
{
	if (not est_stoppe())
	{
		rotation.consigne(mesure_angle_);
		translation.consigne(mesure_distance_);
	}
}

void Robot::gestion_blocage()
{
	static float compteurBlocage=0;
	bool moteur_force = abs(moteurGauche.pwm()) > 45 || abs(moteurDroit.pwm()) > 45;
	bool bouge_pas = rotation.erreur_d()==0 && translation.erreur_d()==0;
	
	if (bouge_pas && moteur_force)
	{
		if(compteurBlocage==100){
			stopper();
			est_bloque_ = true;
			compteurBlocage=0;
		}
		else
			compteurBlocage++;
	}
	else
		compteurBlocage=0;
}

/////////////////////////// FONCTIONS BLOQUANTES POUR LE RECALAGE ///////////////////////

void Robot::recalage()
{
	changerVitesseTra(1);
	changerVitesseRot(1);
	translater_bloc(-1000.0);
	etat_rot_ = false;
	changerVitesseTra(2);
	translater_bloc(-300.0);
	if (couleur_ == 'r') x_ = (-LONGUEUR_TABLE/2+LARGEUR_ROBOT/2); else x_ = (LONGUEUR_TABLE/2-LARGEUR_ROBOT/2);
	if (couleur_ == 'r') changer_orientation(0.0); else changer_orientation(PI);
	etat_rot_ = true;
	_delay_ms(500);
	changerVitesseTra(1);
	translater_bloc(220.0);
	tourner_bloc(PI/2);
	translater_bloc(-1000.0);
	etat_rot_ = false;
	changerVitesseTra(2);
	translater_bloc(-300.0);
	y_ = (LARGEUR_ROBOT/2);
	changer_orientation(PI/2);
	etat_rot_ = true;
	_delay_ms(500);
	changerVitesseTra(1);
	translater_bloc(150.0);
	if (couleur_ == 'r') tourner_bloc(0.0); else tourner_bloc(PI);
	changerVitesseTra(2);
	changerVitesseRot(1);
	_delay_ms(200);
	serial_t_::print("FIN_REC");
}

void Robot::translater_bloc(float distance)
{
	translater(distance);
	while(not est_stoppe() && not est_bloque_){
		asm("nop");
	}
}

void Robot::tourner_bloc(float angle)
{
	tourner(angle);
	while(not est_stoppe() && not est_bloque_){
		asm("nop");
	}
}
