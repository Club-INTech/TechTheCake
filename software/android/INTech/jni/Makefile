TARGET=detection
CC=g++
LIBS=-lopencv_core -lopencv_imgproc -lopencv_highgui
CFLAGS = -g -Wall

.PHONY: default all clean

default: $(TARGET)
all: default

#OBJECTS = $(patsubst %.cpp, %.o, $(wildcard *.cpp))
OBJECTS = ball.o ballidentifier.o model.o morpho.o processing.o main.o
HEADERS = $(wildcard *.h)

%.o: %.c $(HEADERS)
	$(CC) $(CFLAGS) -c $< -o $@

.PRECIOUS: $(TARGET) $(OBJECTS)

$(TARGET): $(OBJECTS)
	$(CC) $(OBJECTS) -Wall $(LIBS) -o $@

clean:
	-rm -f *.o
	-rm -f $(TARGET)
