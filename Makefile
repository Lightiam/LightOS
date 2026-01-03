# LightOS v0.1 - Master Build System
.PHONY: all kernel userspace libraries fabric-os install clean

all: kernel userspace libraries fabric-os

kernel:
	$(MAKE) -C kernel/modules/lightos-core

userspace:
	$(MAKE) -C userspace/lightos-agent

libraries:
	$(MAKE) -C libraries/liblightos-collectives

fabric-os:
	$(MAKE) -C fabric-os/benchmark-service

install:
	$(MAKE) -C kernel/modules/lightos-core install
	$(MAKE) -C userspace/lightos-agent install
	$(MAKE) -C libraries/liblightos-collectives install

clean:
	$(MAKE) -C kernel/modules/lightos-core clean
	$(MAKE) -C userspace/lightos-agent clean
	$(MAKE) -C libraries/liblightos-collectives clean
	$(MAKE) -C fabric-os/benchmark-service clean
