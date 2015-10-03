=?= [center]Basic concept[/center] =?=
___________________________________________

Lutin permit simply to compile applications and library.

To simply understand the use, we will use a simple library:

[code style=bash]
	git clone http://github.con/atria-soft/etk.git
[/code]

etk is a basic library that have drive the lutin project.


== compile a module ==

It is really simple:

[code style=bash]
	lutin yourModuleName
	#example:
	lutin etk
[/code]



== Option working ==

Lutin have a complex option methodologie. We can consider 3 part of the option:
:** Global option
:** target option
:** modules




== Generic options ==

=== Display help ===

Availlable everywhere ...

[code style=bash]
	lutin -h
	lutin --help
[/code]

You can see in this help that it take a litle time to react.
The first time you run lutin, it parse all the file in your sub-directory.
But the system keep the data in cash, then the next time it is faster.

At the end of the help you an see an help about the etk librery with the associated help.

=== Build in color ===

[code style=bash]
	lutin -C
	lutin --color
[/code]

=== Display build line in pretty print mode ===

when an error apear, the gcc or clang compile line can be really unreadable:
[code]
	g++ -o /home/heero/dev/plop/out/Linux_x86_64/release/build/gcc/etk/obj/etk/Color.cpp.o -I/home/heero/dev/plop/etk -std=c++11 -D__CPP_VERSION__=2011 -D__TARGET_OS__Linux -D__TARGET_ARCH__x86 -D__TARGET_ADDR__64BITS -D_REENTRANT -DNDEBUG -O3 -fpic -D__STDCPP_GNU__ -Wall -Wsign-compare -Wreturn-type -Wno-write-strings -Woverloaded-virtual -Wnon-virtual-dtor -Wno-unused-variable -DMODE_RELEASE -c -MMD -MP /home/heero/dev/plop/etk/etk/Color.cpp
[/code]

whith this option you can transform this not obvious line in a readable line:

[code style=bash]
	lutin -P
	lutin --pretty
[/code]

result:
[code]
	g++ \
		-o /home/XXX/dev/out/Linux_x86_64/release/build/gcc/etk/obj/etk/Color.cpp.o \
		-I/home/XXX/dev/etk \
		-std=c++11 \
		-D__CPP_VERSION__=2011 \
		-D__TARGET_OS__Linux \
		-D__TARGET_ARCH__x86 \
		-D__TARGET_ADDR__64BITS \
		-D_REENTRANT \
		-DNDEBUG \
		-O3 \
		-fpic \
		-D__STDCPP_GNU__ \
		-Wall \
		-Wsign-compare \
		-Wreturn-type \
		-Wno-write-strings \
		-Woverloaded-virtual \
		-Wnon-virtual-dtor \
		-Wno-unused-variable \
		-DMODE_RELEASE \
		-c \
		-MMD \
		-MP \
		/home/XXX/dev/etk/etk/Color.cpp
[/code]

=== lutin log ===

Lutin have an internal log system. To enable or disable it just select your debug level with the option:

[code style=bash]
	lutin -v4
	lutin --verbose 4
[/code]

The level availlables are:
:** 0: None
:** 1: error
:** 2: warning (default)
:** 3: info
:** 4: debug
:** 5: verbose
:** 6: extreme_verbose

=== select the number of CPU core used ===

By default lutin manage only 1 CPU core (faster to debug) but for speed requirement you can use use multiple core:

[code style=bash]
	#for 5 core
	lutin -j5
	lutin --jobs 5
[/code]

=== Force rebuild all ===

Sometime it is needed to rebuild all the program, just do :

[code style=bash]
	lutin -B
	lutin --force-build
[/code]

=== Force rebuild all ===

Force strip of output binary (remove symboles)

[code style=bash]
	lutin -s
	lutin --force-strip
[/code]



		-w / --warning
			Store warning in a file build file
