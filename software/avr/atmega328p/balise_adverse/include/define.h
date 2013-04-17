#ifndef _UTILS_H_
#define _UTILS_H_

#define MODE_XBEE_S8            1

/**
 * Défini l'intervalle de temps minimum à prendre en considération pour une double impulsion
 * @def TIME_THRESHOLD_MIN
 */
#define TIME_THRESHOLD_MIN 100

#define BAUDRATE 115200

#if MODE_XBEE_S8 == 1
#define SERVER_ADDRESS 0x0013A2004096049E
#else
#define SERVER_ADDRESS 0x5001
#endif

#endif
