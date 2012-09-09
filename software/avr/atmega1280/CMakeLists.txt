include(atmega1280.cmake)
set(MICROCONTROLEURS balise_robot balise_robot_with_ntp ntp_Serveur)
add_microcontrolers(m1280 "${MICROCONTROLEURS}")
