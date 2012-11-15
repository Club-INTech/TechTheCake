include(atmega328p.cmake)
set(MICROCONTROLEURS actionneurs_arduino2 asservissement compteur capteurs balise_adverse table_maker print_serial mesure_impulsion infrarouges capteur_vieux jumper ntp ping pont_h)
add_microcontrolers(m328p "${MICROCONTROLEURS}")
