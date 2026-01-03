CC = gcc
CFLAGS = -Wall -Wextra -O2 -I include
TARGET = build/lightos-agent

all: $(TARGET)

build:
	mkdir -p build

$(TARGET): build src/agent.c
	$(CC) $(CFLAGS) src/agent.c -o $(TARGET) -lpthread

install: $(TARGET)
	install -m 755 $(TARGET) /usr/local/bin/

clean:
	rm -rf build
