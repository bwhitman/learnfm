CC := g++
CFLAGS := -Wall -O
TARGET := dx7

SRCS := $(wildcard *.cc)
OBJS := $(patsubst %.cc,%.o,$(SRCS))

all: $(TARGET)
$(TARGET): $(OBJS)
	$(CC) -o $@ $^
%.o: %.cc
	$(CC) $(CFLAGS) -c $<
clean:
	rm -rf $(TARGET) *.o
	
.PHONY: all clean
