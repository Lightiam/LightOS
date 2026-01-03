CC = gcc
CFLAGS = -Wall -Wextra -O2 -I include
TARGET = build/benchmark-service

all: $(TARGET)

build:
	mkdir -p build

$(TARGET): build src/benchmark.c
	$(CC) $(CFLAGS) src/benchmark.c -o $(TARGET)

clean:
	rm -rf build
