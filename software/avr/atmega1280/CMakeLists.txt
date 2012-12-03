include(atmega1280.cmake)
set(MICROCONTROLEURS balise_robot balise_robot_with_ntp actionneurs_arduino actionneurs_cadeaux actionneurs_bougies)
add_microcontrolers(m1280 "${MICROCONTROLEURS}")
