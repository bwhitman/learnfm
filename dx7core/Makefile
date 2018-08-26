CC := g++
CFLAGS := -Wall -O 
TARGET := dx7

SRCS := dx7note.cc env.cc exp2.cc fir.cc fm_core.cc fm_op_kernel.cc freqlut.cc lfo.cc log2.cc main.cc patch.cc pitchenv.cc resofilter.cc ringbuffer.cc sawtooth.cc sin.cc synth_unit.cc wavout.cc

OBJS := $(patsubst %.cc,%.o,$(SRCS))

all: $(TARGET)
#	$(shell python setup.py install)

$(TARGET): $(OBJS)
	$(CC) -o $@ $^
%.o: %.cc
	$(CC) $(CFLAGS) -c $<
clean:
	rm -rf $(TARGET) *.o
	
.PHONY: all clean
