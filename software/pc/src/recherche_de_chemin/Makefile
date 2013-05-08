CC=g++
DISPLAY_DEBUG_WINDOWS=0
CXXFLAGS=-fPIC -O2 -I/usr/include/python3.2mu/ -DDISPLAY_DEBUG_WINDOWS=${DISPLAY_DEBUG_WINDOWS}
LIBS=-lopencv_core -lopencv_imgproc -lopencv_highgui

all: swig recherche_chemin

recherche_chemin_wrap.o:
	$(CC) $(CXXFLAGS) -c recherche_chemin_wrap.cxx
	
recherche_chemin: table.o visilibity_wrapper.o visilibity.o recherche_chemin_wrap.o
	$(CC) -shared $(CXXFLAGS) -o _recherche_chemin.so $^ $(LIBS)
	
swig:
	swig2.0 -c++ -python -py3 recherche_chemin.swig

clean:
	rm -f *.o *.so *.cxx
