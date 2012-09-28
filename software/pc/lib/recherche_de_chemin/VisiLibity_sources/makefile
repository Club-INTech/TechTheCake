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
	g++ -fPIC -c visilibity.cpp

%_wrap.cxx: %.i $(FILES_H)
	swig -Wall -python -c++ $<

%_wrap.o: %_wrap.cxx
	$(CXX) -fPIC $(INCLUDE) -c $<  `python2.7-config --cflags`

_%.so: %_wrap.o
ifeq ($(OS), Darwin)
	$(CXX) -fPIC -Wall -dynamiclib  $< visilibity.o $(LDFLAGS) `python2.7-config --ldflags` -o $@
else
	$(CXX) -fPIC -Wall -shared  $< visilibity.o $(LDFLAGS) `python2.7-config --ldflags` -o $@
endif
