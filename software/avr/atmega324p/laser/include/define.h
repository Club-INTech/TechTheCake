#ifndef DEFINE_H
#define DEFINE_H

#define MODE_XBEE_S8            0
#define BALISE_BAUDRATE   		115200
#define ROBOT_BAUDRATE    		38400
#define PING_ID           		4
#define DEFAULT_SPEED_ORDER		15
#define TIMEOUT			  		100
#define PI                      3.14159265359
#define ANGLE_ORIGIN_OFFSET     2.05

#define BALISE_NUMBER     		2

#define OFFSET_FACTOR 	  		0.5

#if MODE_XBEE_S8 == 1

// Adresses des balises (Xbee S8)
static uint64_t balise_address[BALISE_NUMBER] = {0x0013A2004098CD8F};
typedef uint64_t xbee_address;

#else

// Adresses des balises (Xbee)
// PAN ID: 7378
static uint16_t balise_address[BALISE_NUMBER] = {0x5001, 0x5002};
typedef uint16_t xbee_address;

#endif

#endif
