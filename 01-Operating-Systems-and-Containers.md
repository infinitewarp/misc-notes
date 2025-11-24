# It's all about *layers!*

Disclaimer: I am not an expert authority on these subjects. Do not take my words as gospel! This is just a collection of my thoughts and memories (with a few references) that I used as my outline for an in-person conversation.

## Overview

![13788979-1595881671730.png](https://dz2cdn1.dzone.com/storage/temp/13788979-1595881671730.png)

- Containers run in "user space", and they use the same kernel as its host system.
	- "User space" means it runs without elevated privileges. No root! (unless you ask for it)
	- Since guest containers share the same kernel as the host, it is *possible* for incompatibilities to arise between hosts with different kernels, but this is not common!
- Containers run their own libraries and programs isolated from the host (and other containers).
- Container engines use features of the Linux kernel to run their code in isolated spaces.
	- [Namespaces](https://en.wikipedia.org/wiki/Linux_namespaces) are a feature of the Linux kernel that make this possible.
	- Namespaces restrict a group of programs' access to specific resources.
	- Namespaces can control access to processes, filesystems, and networking.
- Compare with virtual machines (VMs) that use a hypervisor to run _multiple separate_ kernels.
	- [KVM](https://en.wikipedia.org/wiki/Kernel-based_Virtual_Machine) (Kernel-based Virtual Machine) is part of the Linux kernel, allowing it to serve dual purposes, but some hypervisors run on bare metal or are embedded with the machine's hardware/firmware.
	- Each VM's kernel may have its own access to the underlying hardware, which can be very powerful, but may be more powerful than most programs actually need.


## So, what exactly is the kernel? Is the kernel the OS?

- The kernel is the *core* of the operating system.
- The kernel is the code that *starts* the whole system, manages hardware I/O, manages memory access, and creates, manages, and stops all other processes.
- The term "operating system" typically includes a larger collection of command-line programs, shared libraries, desktop environments, and GUI applications.
	- …all of which are optional, but the kernel is _always_ there.
- The kernel has privileged access and can generally tell the CPU to do *anything*.
	- CPUs categorize instructions into different privilege levels.
	- If a program tries to execute a privileged command directly, the CPU may reject that command and tell the kernel decide to handle it.
	- Unprivileged instructions are very limited. They cannot do I/O and have limited access to the memory space.
- The kernel exposes many [system call](https://man7.org/linux/man-pages/man2/syscalls.2.html) APIs for processes to interact with it.
	- Many of these encapulate instructions that a program normally *could not execute* directly.
- The kernel is responsible for starting *all* other programs.
	- If you are writing a program and you want to tell it to run another program, you actually have to *ask the kernel* to start that program for you.


## Not all kernels are the same!

* **Monolithic kernels** typically have *all* functionality that could possibly need privileged access built into the kernel itself.
	* The Linux kernel is a monolithic kernel. Most device drivers are part of the kernel, for example, and the Linux kernel currently has over [*8 million* lines of code](https://docs.kernel.org/process/1.Intro.html#what-this-document-is-about). If you need to add a new driver, you may need to recompile the kernel! (Fortauntely, they have modularized things so you don't have to recompile *everything*.)
* **Microkernels** typically have only the *minimum required* functionality in the kernel.
	* The Nintendo Switch uses a proprietary microkernel where all drivers run in user space.
* **Hybrid kernels** are somewhere in the middle. They typically load device drivers from external binaries only as needed, but they may run with elevated privileges like the kernel itself, and the kernel may already include some common driver functionality.
	* The macOS kernel ([XNU](https://en.wikipedia.org/wiki/XNU)/[Mach](https://en.wikipedia.org/wiki/Mach_(kernel))) started as a microkernel and has become a more hybrid kernel over the years. macOS device drivers are typically loaded from external binaries called "kernel extensions".
	* The Microsoft Windows kernel (Windows NT) is also a hybrid kernel.

For the sake of this discussion, when I'm talking about the kernel, assume it's the Linux kernel!

## How does the kernel manage programs, containers, etc?

- Pause! Let's review how computing hardware actually runs _any_ code...


## CPU hardware basics

- Modern CPUs can:
	- load and move data around in memory (registers, stacks, RAM)
	- perform arithmetic and boolean logic
	- compare values
	- send to and receive signals from other attached hardware
	- That's it! (mostly)
- CPU instructions look like this:
	- [x86 and amd64 instruction reference](https://www.felixcloutier.com/x86/index.html)
	- [Example instructions to draw one pixel](https://github.com/cirosantilli/x86-bare-metal-examples/blob/master/bios_pixel.S)
	- [ELF executable diagram](https://raw.githubusercontent.com/corkami/pics/refs/heads/master/binary/elf101/elf101-64.pdf)
	- (maybe look at an example program in ada64)


## CPU physical connections

![kaby lake CPU](https://www.legitreviews.com/wp-content/uploads/2017/01/Intel-corei7-7700k-cpu.jpg)
![kaby lake CPU pin diagram](https://abload.de/img/kl1bmssz.png)

- Many of these regulate power for the CPU itself (V\*)
	- VCC = high voltage, power supply
	- VCCGT = ground connections
- Many provide connections to system memory/RAM (DDR\*)
- Many provide connections to other motherboard devices (DMI\*)
- Many provice connections for graphics (PEG\*)
- …and more! (Intel provides [many](https://www.intel.com/content/dam/www/public/us/en/documents/datasheets/7th-and-8th-gen-core-family-mobile-u-y-processor-lines-i-o-datasheet-vol-1.pdf) [docs](https://edc.intel.com/content/www/us/en/design/ipla/software-development-platforms/client/platforms/alder-lake-desktop/12th-generation-intel-core-processors-datasheet-volume-1-of-2/003/signal-description/) if you are curious)


## How do you turn voltages into meaningful messages?

* The motherboard has a *system clock* that sends voltage changes to various components.
* The system clock flips voltage high and low at a constant frequency.
	* See also: [crystal oscillator](https://en.wikipedia.org/wiki/Crystal_oscillator), [PLL oscillators (as multipliers)](https://en.wikipedia.org/wiki/Phase-locked_loop), and [TFBARs](https://en.wikipedia.org/wiki/Thin-film_bulk_acoustic_resonator)
* CPU may have its own dedicated clock, but it also has to stay in sync with the system clock.
* Devices encode messages using the clock's timing to represent a binary stream of voltages.

![](https://i.stack.imgur.com/oEfTc.png)

- The CPU hardware *recognizes specific patterns* as instructions to trigger specific actions.
- It's just doing that *billions* of times a second. 🙂


## OK, so what does the CPU *do?*

- Once powered on, a CPU does ***exactly three things*** in a loop forever until powered off:
	- **Fetch** *one* instruction from memory and put it in a register.
	- **Decode** that instruction to determine what needs to happen.
	- **Execute** that instruction by sending voltages to other parts of itself or attached devices.
- This is called the [instruction cycle](https://en.wikipedia.org/wiki/Instruction_cycle).

Modern hardware complicates that simple cycle a bit…
* Multiple cores is very much like having multiple CPUs; each may runs its own cycle in parallel.
* Hyperthreading lets a core stagger and *overlap* multiple cycles at once, fetching the next instruction *while* the first instruction is being executed. It's *almost* like having a second CPU.
…but the kernel still has to juggle issueing all the commands to them.

Physical CPU (Intel "Kaby Lake") die layout with multiple cores and hyperthreading:
![](https://images.hothardware.com/contentimages/article/2567/content/small_kaby-die-map.jpg)

## If a CPU only handles *one* instruction at a time, how can you multi-task more than one process?

- That's the kernel's job!
- Remember: **the kernel manages other processes**.
- The kernel has code that tells the CPU when to run another program's code, but it also tells the CPU when to *stop* running that code and start running some *other* code.
	- See: [preemptive multitasking](https://en.wikipedia.org/wiki/Preemption_(computing)#Preemptive_multitasking) vs [cooperative multitasking](https://en.wikipedia.org/wiki/Cooperative_multitasking) vs [time-sharing](https://en.wikipedia.org/wiki/Time-sharing)
	- (Most modern kernels use implement *preempive* multitasking.)
- Multitasking is partially an illusion. The kernel works as a [scheduler](https://www.kernel.org/doc/html/latest/scheduler/sched-design-CFS.html) for all active processes, and the kernel decides when each process's code can run. CPUs and the kernel scheduler are so fast that you rarely notice when processes are being switched in the CPU.


## How does the CPU actually execute the kernel's code?

- When a system is powered on, it always looks for a specific place for the boot loader.
	- This may be GRUB. There are many different kinds of bootloaders.
	- The boot loader isn't your kernel. It's a simple program that finds your kernel (or lets you choose one), and it tells the CPU to load and execute that kernel. Then it's done!
- Starting the kernel itself is very fast!
- *Most* of what you see during the boot cycle is the kernel starting *other* programs, and you're waiting for those programs to do things like read files, write logs, access disks, communicate with something over the network... mostly lots of waiting on I/O with various devices.
	- These are mostly *other programs* that the kernel starts and manages until you shut down.


## Okay, let's get back to containers...

- We now know that:
	- The kernel is responsible for starting, multitasking, and stopping programs.
	- *Only* the kernel can access other devices through privileged CPU instructions.
	- The Linux kernel has APIs to let a group of processes share access to a restricted set of resources.
	- Programs we want to run inside containers *generally* do not need privileged access to the rest of the system or hardware.


## Enter Docker and Podman!

* Externally, they are very similar in how they operate.
	* They both use the Linux kernel APIs to run their code in isolated namespaces.
	* They use the same format for defining containers and images. (see: [OCI](https://opencontainers.org/about/overview/))
	* They bundle all the files for their container programs into a single flat image file.
		* It's basically a `tar` file that looks like the root of any normal filesystem!
		* See also: [`podman-save`](https://docs.podman.io/en/latest/markdown/podman-save.1.html) and [`podman-import`](https://docs.podman.io/en/latest/markdown/podman-import.1.html)
* Internally, they're a bit different.
	* Docker uses a daemon/service to coordinate all its processes. That daemon runs with elevated privileges, and that may not be desirable due to security risks.
	* Podman is daemon-less and therefore root-less, and it can run entirely in user space.
* Docker is a proprietary commercial product, whereas Podman is free open source.


## Why use a container? Why not just another program?

* **Dependencies.**
	* The container image acts like a whole filesystem. You don't need to install lots of extra libraries or files into your primary filesystem just to run a program.
* **Process isolation.**
	* The container process is entirely isolated by default thanks to the kernel namespace APIs. You can grant additional access to local filesystems and network ports if you want, but that's up to you.
* **Security.**
	* See also: dependencies and process isolation. 🙂 If the container process can't see anything else on your system and if the container process is running in user space (assuming Podman), then it's probably *very* safe to run.



## Bonus: What a CPU is really doing

Because I just wanted to put this picture somewhere in here.

![ball machine](https://i.imgur.com/2uA2GUP.gif)

