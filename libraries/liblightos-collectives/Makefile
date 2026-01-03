CC = gcc
CFLAGS = -Wall -Wextra -O2 -fPIC -I include
TARGET = build/liblightos-collectives.so.0.1.0

all: $(TARGET)

build:
	mkdir -p build

$(TARGET): build src/collectives.c
	$(CC) $(CFLAGS) -shared src/collectives.c -o $(TARGET)
	ln -sf liblightos-collectives.so.0.1.0 build/liblightos-collectives.so

install: $(TARGET)
	install -m 755 $(TARGET) /usr/local/lib/
	ldconfig

clean:
	rm -rf build
