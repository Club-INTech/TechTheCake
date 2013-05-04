include(atmega328p.cmake)
set(MICROCONTROLEURS compteur asservissement compteur_robot2 asservissement_robot2 codeuse capteurs balise_adverse table_maker print_serial mesure_impulsion infrarouges capteur_vieux jumper ntp ping pont_h formation-ex1 formation-ex2 formation-ex3 formation-ex4 capteur_couleur test_moteur ascenseur compteur_ascenseurs suiveur)
add_microcontrolers(m328p "${MICROCONTROLEURS}")
