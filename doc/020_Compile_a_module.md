How to use lutin                               {#lutin_use}
================

@tableofcontents

Lutin permit simply to compile applications and library.

To simply understand the use, we will use a simple library:

```{.sh}
	git clone http://github.con/atria-soft/etk.git
```


compile a module:                               {#lutin_use_compile}
=================

It is really simple:

```{.sh}
	lutin yourModuleName
	#example:
	lutin etk
```



Option working:                               {#lutin_use_options}
===============

Lutin have a complex option methodologie. We can consider 3 part of the option:
  - global option
  - target option
  - modules


Global options:                               {#lutin_use_options_global}
---------------

Globals option is parse first and manage global setting of the build (not specific of a target)

this keep the last value config set


Display help:                               {#lutin_use_options_help}
-------------

Availlable everywhere ...

```{.sh}
	lutin -h
	lutin --help
```

You can see in this help that it take a litle time to react.
The first time you run lutin, it parse all the file in your sub-directory.
But the system(OS) keep the data in cash, then the next time it is faster.

At the end of the help you an see an help about the etk librery with the associated help.

Build in color:                               {#lutin_use_options_color}
---------------

```{.sh}
	lutin -C
	lutin --color
```

Display build line in pretty print mode:                               {#lutin_use_options_pretty}
----------------------------------------

when an error apear, the gcc or clang compile line can be really unreadable:
```{.sh}
	g++ -o /home/heero/dev/plop/out/Linux_x86_64/release/build/gcc/etk/obj/etk/Color.cpp.o -I/home/heero/dev/plop/etk -std=c++11 -D__CPP_VERSION__=2011 -D__TARGET_OS__Linux -D__TARGET_ARCH__x86 -D__TARGET_ADDR__64BITS -D_REENTRANT -DNDEBUG -O3 -fpic -D__STDCPP_GNU__ -Wall -Wsign-compare -Wreturn-type -Wno-write-strings -Woverloaded-virtual -Wnon-virtual-dtor -Wno-unused-variable -DMODE_RELEASE -c -MMD -MP /home/heero/dev/plop/etk/etk/Color.cpp
```

whith this option you can transform this not obvious line in a readable line:

```{.sh}
	lutin -P
	lutin --pretty
```

result:
```{.sh}
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
```

lutin log:                               {#lutin_use_options_log}
----------

Lutin have an internal log system. To enable or disable it just select your debug level with the option:

```{.sh}
	lutin -v4
	lutin --verbose 4
```

The level availlables are:
  - 0: None
  - 1: error
  - 2: warning (default)
  - 3: info
  - 4: debug
  - 5: verbose
  - 6: extreme_verbose

Select the number of CPU core used:                               {#lutin_use_options_cpu}
-----------------------------------

By default lutin manage only 1 CPU core (faster to debug) but for speed requirement you can use use multiple core:

```{.sh}
	#for 5 core
	lutin -j5
	lutin --jobs 5
```

Force rebuild all:                               {#lutin_use_options_rebuild_force}
------------------

Sometime it is needed to rebuild all the program, just do:

```{.sh}
	lutin -B
	lutin --force-build
	# or remove the build directory
	rm -rf out/
```

Force strip all library and programs:                               {#lutin_use_options_strip}
-------------------------------------

Force strip of output binary (remove symboles)

```{.sh}
	lutin -s
	lutin --force-strip
```

Manage Cross compilation:                               {#lutin_use_options_cross_compile}
=========================

The main objective of lutin is managing the cross compilation to build from linux to other platform:

For android you can use:

```{.sh}
	lutin -t Android your-module
	lutin -t Windows your-module
```

Build in debug mode:                               {#lutin_use_options_debug_release}
====================

To developp it is fasted with debug tools

```{.sh}
	lutin -m debug your-module
	lutin -m release your-module
```

You can desire to have compilation optimisation when you build in debug mode:

```{.sh}
	lutin -m debug --force-optimisation your-module
```

Execute your program after building it:                               {#lutin_use_options_execute}
=======================================

You can execute some action in a single line for a module:

```bash
	lutin -m debug your-module?clean?build?run:--run-option1:--run-option2
```

Why use ```?run``` istead of direct calling the binary?

This is simple: you does nok knoww where the binary is installed... when you build for linux in debug it will be set in ```out/Linux_x86_64/debug/staging/clang/edn/edn.app/``` for edn application. 
Note that the path is distinct for gcc/clang, debug/release, Linux/windows/Android/..., 64/32 bits, and for every applications ...

Then it is really easy to run the wrong binary.


Install your program after building it:                               {#lutin_use_options_install}
=======================================

You can install your build module:

```{.sh}
	lutin -m debug your-module?build?install
```

This option is not availlablke on all platform ...




**Index:**
  - @ref mainpage
  - @ref lutin_concept
  - @ref lutin_use
  - @ref lutin_module

