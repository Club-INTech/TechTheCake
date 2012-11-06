include(atmega328p.cmake)
set(MICROCONTROLEURS actionneurs_arduino asservissement compteur balise_adverse table_maker print_serial mesure_impulsion infrarouges capteur_vieux jumper ntp ping blink capteurs)
add_microcontrolers(m328p "${MICROCONTROLEURS}")
