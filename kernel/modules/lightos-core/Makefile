# LightOS Core Kernel Module v0.2.0
# Includes: Spiking Neural Network + Mixture of Experts

obj-m += lightos_core.o

# Note: Spiking and MoE are separate modules for now
# To build as single module, would need to restructure source files

KDIR := /lib/modules/$(shell uname -r)/build

all:
	@echo "Building LightOS Neural Compute Engine kernel module..."
	$(MAKE) -C $(KDIR) M=$(PWD) modules
	@echo "Build complete: lightos_core.ko"
	@echo ""
	@echo "Note: Spiking and MoE modules are integrated via headers"
	@echo "      Full integration would require kernel build system changes"

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean

install:
	@echo "Installing LightOS kernel module..."
	$(MAKE) -C $(KDIR) M=$(PWD) modules_install
	depmod -a
	@echo ""
	@echo "Module installed. Load with: sudo modprobe lightos"
	@echo "Verify with: dmesg | grep LightOS"
