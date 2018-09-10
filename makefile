CC=gcc
CFLAGS=-I.
DEPS = flail.h

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

flail: flail.o
	$(CC) -o  flail flail.o

