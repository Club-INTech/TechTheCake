#ifndef COLOR_H
#define COLOR_H

// Java utilise RGB et OpenCV BGR...
#ifdef COMPILE_FOR_ANDROID

#define RED_COLOR Scalar(255, 0, 0, 255)
#define BLUE_COLOR Scalar(0, 0, 255, 255)

#else

#define RED_COLOR Scalar(0, 0, 255, 255)
#define BLUE_COLOR Scalar(255, 0, 0, 255)

#endif

#endif // COLOR_H
