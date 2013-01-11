#le binding python3.2 nécessite
#python3.2-config : apt-get install python3.2-dev
#et swig2.0 : apt-get install swig2.0
#
#les lignes commentés peuvent faire un binding python2.7

#phony target.
current_target: python

#Compiler flags
CXXFLAGS = -O2
#Linker flags
LDFLAGS = -O2

clean:   
	rm -f *~ *.o *.do *.db *.so *.cxx

.SECONDARY:

python: visilibity.o _visilibity.so

visilibity.o: visilibity.cpp visilibity.hpp
	g++ -fPIC $(CXXFLAGS) -c visilibity.cpp

%_wrap.cxx: %.i $(FILES_H)
	#swig -Wall -python -c++ $<
	swig2.0 -Wall -python -c++ $<

%_wrap.o: %_wrap.cxx
	#$(CXX) -fPIC $(INCLUDE) -c $<  `python2.7-config --cflags`
	$(CXX) -fPIC $(INCLUDE) -c $<  `python3.2-config --cflags`

_%.so: %_wrap.o
ifeq ($(OS), Darwin)
	#$(CXX) -fPIC -Wall -dynamiclib  $< visilibity.o $(LDFLAGS) `python2.7-config --ldflags` -o $@
	$(CXX) -fPIC -Wall -dynamiclib  $< visilibity.o $(LDFLAGS) `python3.2-config --ldflags` -o $@
else
	#$(CXX) -fPIC -Wall -shared  $< visilibity.o $(LDFLAGS) `python2.7-config --ldflags` -o $@
	$(CXX) -fPIC -Wall -shared  $< visilibity.o $(LDFLAGS) `python3.2-config --ldflags` -o $@
endif
