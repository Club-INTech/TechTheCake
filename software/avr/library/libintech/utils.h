/** 
 * Fonctions et macros générales utiles
 * 
 * @author Philippe TILLET phil.tillet@gmail.com
 * @author Marc BLANC-PATIN marc.blancpatin@gmail.com
 * 
 */

#ifndef UTILS_H
#define UTILS_H

/**
 * @def sbi(port,bit)
 * @brief Met à 1 le bit du port
 * @param port Port concerné
 * @param bit Bit concerné
 * 
 * Met à 1 le bit du port.
 */
#ifndef sbi
#define sbi(port,bit) (port) |= (1 << (bit))
#endif

/**
 * @def cbi(port,bit)
 * @brief Met à 0 le bit du port
 * @param port Port concerné
 * @param bit Bit concerné
 * 
 * Met à 0 le bit du port.
 */
#ifndef cbi
#define cbi(port,bit) (port) &= ~(1 << (bit))
#endif

/**
 * @def tbi(port,bit)
 * @brief Bascule (toggle) le bit du port
 * @param port Port concerné
 * @param bit Bit concerné
 * 
 * Bascule (toggle) le bit du port (0 -> 1 et 1 -> 0)
 */
#ifndef tbi
#define tbi(port,bit) (port) ^= (1 << (bit))
#endif

/**
 * @def rbi(port,bit)
 * @brief Lit le bit du port
 * @param port Port concerné
 * @param bit Bit concerné
 * 
 * Renvoie la valeur du bit
 */
#ifndef rbi
#define rbi(port,bit) ((port & (1 << bit)) >> bit)
#endif

template<class T>
T max(T a, T b) {
    if (a > b) {
        return a;
    }
    return b;
}

template<class T>
T min(T a, T b) {
    if (a < b) {
        return a;
    }
    return b;
}

#endif