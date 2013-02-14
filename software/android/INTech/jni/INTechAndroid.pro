TEMPLATE = app
CONFIG += console
CONFIG -= qt

SOURCES += main.cpp \
    morpho.cpp \
    processing.cpp \
    ball.cpp \
    ballidentifier.cpp \
    model.cpp

LIBS += -L/usr/include/opencv -lopencv_core -lopencv_imgproc -lopencv_highgui -lopencv_ml -lopencv_video -lopencv_features2d -lopencv_calib3d -lopencv_objdetect -lopencv_contrib -lopencv_legacy -lopencv_flann

HEADERS += \
    morpho.h \
    processing.h \
    ball.h \
    ballidentifier.h \
    model.h \
    color.h


