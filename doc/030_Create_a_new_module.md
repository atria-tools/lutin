Create a new Module:                                   {#lutin_module}
====================

@tableofcontents


Base of the module file:                               {#lutin_module_base_file}
========================

To create a new module you will use a generic naming:

```{.sh}
	lutin_module-name.py
```

Replace your ``module-name`` with the delivery you want. The name can contain [a-zA-Z0-9\-_] values.

In the module name you must define some values:

```{.py}
#!/usr/bin/python
import lutin.module as module
import lutin.tools as tools

# A simple list of type:
#    - BINARY
#    - BINARY_SHARED
#    - BINARY_STAND_ALONE
#    - LIBRARY
#    - LIBRARY_DYNAMIC
#    - LIBRARY_STATIC
#    - PACKAGE
#    - PREBUILD
#    - DATA
def get_type():
	return "LIBRARY"

# simple description of the module that appear in the 'lutin -h'
# Note: this fucntion is optionnal.
def get_desc():
	return "Ewol tool kit"

# type of licence:
#    "APACHE-2"
#    "BSD-1" / "BSD-2" / "BSD-3" / "BSD-4"
#    "GPL-1" / "GPL-2" / "GPL-3"
#    "LGPL-1" / "LGPL-2" / "LGPL-3"
#    PROPRIETARY
#    ...
# Note: this fucntion is optionnal.
def get_licence():
	return "APACHE-2"

# type of compagny that provide the software:
#    com : Commercial
#    net : Network??
#    org : Organisation
#    gov : Governement
#    mil : Military
#    edu : Education
#    pri : Private
#    museum : ...
#    ...
# Note: this fucntion is optionnal.
def get_compagny_type():
	return "com"

# Name of the compagny
# Note: this fucntion is optionnal.
def get_compagny_name():
	return "hello-compagny"

# People to contact if a problem appear in the build system / library
# Note: this fucntion is optionnal.
def get_maintainer():
	return ["Mr NAME SurName <my-email@group.com>"]

# Version of the library
# Note: this fucntion is optionnal.
def get_version():
	return [0,9,"dev"]

# create the module
# @param[in] target reference on the Target that is currently build
# @param[in] my_module Module handle that migh be configured
# @return True The module is welled configure
# @return False The module is Not availlable (for this target or ...)
def configure(target, my_module):
	...
	return True
```

Thes it is simple to specify build for:

Create a new Module (LIBRARY):                               {#lutin_module_library}
==============================

What to change:
```{.py}
def get_type():
	return "LIBRARY"
```

By default the library is compile in shared and static. The binary select the mode it prefer...

You can force the library to be compile as a dll/so: ```LIBRARY_DYNAMIC``` or a basic include lib: .a ```LIBRARY_STATIC```


Create a new Module (BINARY):                               {#lutin_module_binary}
=============================

Generic Binary:                                             {#lutin_module_binary_base}
---------------

What to change:
```{.py}
def get_type():
	return "BINARY"
```
The Binay is compile by default target mode (note that the IOs target generate a single .so with all the library inside)

You can force the Binary to be use dynamic library when possible: ```BINARY_SHARED``` or create a single binary with no .so depenency: ```BINARY_STAND_ALONE```

Create a new Module (TEST-BINARY / TOOL-BINARY):            {#lutin_module_binary_tools}
------------------------------------------------

Two binary are really usefull in developpement, the tools and the test-unit, This is the reason why we specify for this 2 cases.

Add the subElement description:
```{.py}
def get_type():
	return "BINARY"

def get_sub_type():
	return "TEST"
```
or:
```{.py}
def get_type():
	return "BINARY"

def get_sub_type():
	return "TOOL"
```


Create a new Module (DATA):                                  {#lutin_module_data}
===========================

This pode permit to only copy data and no dependency with compilling system

What to change:
```{.py}
def get_type():
	return "DATA"
```


Module internal specifications:                               {#lutin_module_internal}
===============================

Add file to compile:                                          {#lutin_module_internal_compile}
--------------------

This is simple: (you just need to specify all the file to compile)

```{.py}
def configure(target, my_module):
	...
	
	# add the file to compile:
	my_module.add_src_file([
	    'module-name/file1.cpp',
	    'module-name/file2.cpp',
	    'module-name/file3.S'
	    ])
	
	...
```

Include directory & install header:                           {#lutin_module_internal_header}
-----------------------------------

A big point to understand is that your library will be used by an other module, then it need to use headers.

The developper must isolate the external include and internal include, then lutin "install" the header and add the "install" header path to build the local library.
This permit to check error inclusion directly in developpement and separate the ```#include "XXX.h"``` and the ```#include <lib-xxx/XXX.h>```

Add file to external include:
```{.py}
def configure(target, my_module):
	...
	
	my_module.add_header_file([
	    'module-name/file1.h',
	    'module-name/file2.h'
	    ])
	
	...
```

You can add a path to your local include:
```{.py}
def configure(target, my_module):
	...
	
	my_module.add_path(os.path.join(tools.get_current_path(__file__), "lib-name"))
	
	...
```


Add Sub-dependency:                                           {#lutin_module_internal_depend}
-------------------

All library need to add at minimum of a simple library (C lib) and other if needed. To do it jus call:
```{.py}
def configure(target, my_module):
	...
	
	# add dependency of the generic C library:
	my_module.add_depend('c')
	# add dependency of the generic C++ library:
	my_module.add_depend('cxx')
	# add dependency of the generic math library:
	my_module.add_depend('m')
	# or other user lib:
	my_module.add_depend('lib-name')
	
	...
```

The system can have optinnal sub-library, then if you just want to add an optionnal dependency:
```{.py}
def configure(target, my_module):
	...
	
	# Add an optionnal dependency (set flag in CPP build if the subLib exist) ==> flag is locally set
	my_module.add_optionnal_depend('z', ["c++", "-DLIB_NAME_BUILD_ZLIB"])
	
	# Add an optionnal dependency (set flag in CPP build if the subLib exist) ==> flag is exported in external upper build
	my_module.add_optionnal_depend('z', ["c++", "-DLIB_NAME_BUILD_ZLIB"], export=True)
	
	...
```

Compilation adn link flags/libs:                              {#lutin_module_internal_flag}
--------------------------------

It is possible to define local and external flags (external are set internal too):
```{.py}
def configure(target, my_module):
	...
	# external flags:
	my_module.add_flag('link-lib', "pthread", export=True)
	my_module.add_flag('c++', "-DHELLO_FLAG=\"kljlkj\"", export=True)
	# internal flags:
	my_module.add_flag('c', "-DMODE_RELEASE")
	
	...
```

build mode (release/debug):                                   {#lutin_module_internal_target_mode}
---------------------------

To add somes element dependent of the build mode:
```{.py}
def configure(target, my_module):
	...
	
	if target.get_mode() == "release":
		pass
	else:
		pass
	
	...
```

build type target:                                            {#lutin_module_internal_target_type}
------------------

To add somes element dependent of the target type:

```{.py}
def configure(target, my_module):
	...
	
	if "Windows" in target.get_type():
		pass
	elif "MacOs" in target.get_type():
		pass
	elif "IOs" in target.get_type():
		pass
	elif "Linux" in target.get_type():
		pass
	elif "Android" in target.get_type():
		pass
	...
```

The target get_type return a list of type that represent the hiararchy dependency, a simple example:

A "Debian" herited of a "Linux" then it will return ["Linux", "Debian"]



Add some data in the install path (share path):                {#lutin_module_internal_data}
-----------------------------------------------

You can install a simple file:

```{.py}
def configure(target, my_module):
	...
	
	# copy file in the share/binanyName/ path (no sub path)
	my_module.copy_path('data/icon.svg')
	
	...
```

Copy multiple files (change path)

```{.py}
def configure(target, my_module):
	...
	
	my_module.copy_path('data/*', 'destinationPath')
	
	...
```

display some debug to help writing code:                       {#lutin_module_internal_write_log}
----------------------------------------


```{.py}
import lutin.debug as debug

def function(...):
	
	debug.error("comment that stop the build")
	debug.warning("comment that print a simple warning")
	debug.info("comment that print a simple information")
	debug.debug("comment that print a simple debug")
	debug.verbose("comment that print a simple verbose")
	
```

A Full template:                                               {#lutin_module_full_template}
================

Create the file:
```{.sh}
	lutin_module-name.py
```

With:
```{.py}
#!/usr/bin/python
import lutin.module as module
import lutin.tools as tools
import lutin.debug as debug
import os

# A simple list of type:
#    - BINARY
#    - BINARY_SHARED
#    - BINARY_STAND_ALONE
#    - LIBRARY
#    - LIBRARY_DYNAMIC
#    - LIBRARY_STATIC
#    - PACKAGE
#    - PREBUILD
#    - DATA
def get_type():
	return "LIBRARY"

# simple description of the module that appear in the 'lutin -h'
# Note: this fucntion is optionnal.
def get_desc():
	return "Descriptiuon of the PROGRAMM"

# type of licence:
#    "APACHE-2"
#    "BSD-1" / "BSD-2" / "BSD-3" / "BSD-4"
#    "GPL-1" / "GPL-2" / "GPL-3"
#    "LGPL-1" / "LGPL-2" / "LGPL-3"
#    PROPRIETARY
#    ...
# Note: this fucntion is optionnal.
def get_licence():
	return "PROPRIETARY"

# type of compagny that provide the software:
#    com : Commercial
#    net : Network??
#    org : Organisation
#    gov : Governement
#    mil : Military
#    edu : Education
#    pri : Private
#    museum : ...
#    ...
# Note: this fucntion is optionnal.
def get_compagny_type():
	return "com"

# Name of the compagny
# Note: this fucntion is optionnal.
def get_compagny_name():
	return "hello-compagny"

# People to contact if a problem appear in the build system / library
# Note: this fucntion is optionnal.
def get_maintainer():
	return ["Mr NAME SurName <my-email@group.com>"]
	# return "authors.txt"

# Version of the library
# Note: this fucntion is optionnal.
def get_version():
	return [0,1,"dev"]
	# return "version.txt"

# create the module
# @param[in] target reference on the Target that is currently build
# @param[in] my_module Module handle that migh be configured
# @return True The module is welled configure
# @return False The module is Not availlable (for this target or ...)
def configure(target, my_module):
	
	# add the file to compile:
	my_module.add_src_file([
	    'module-name/file1.cpp',
	    'module-name/file2.cpp',
	    'module-name/file3.S'
	    ])
	
	my_module.add_header_file([
	    'module-name/file1.h',
	    'module-name/file2.h'
	    ])
	
	my_module.add_path(os.path.join(tools.get_current_path(__file__), "lib-name"))
	
	# add dependency of the generic C library:
	my_module.add_depend('c')
	# add dependency of the generic C++ library:
	my_module.add_depend('cxx')
	# add dependency of the generic math library:
	my_module.add_depend('m')
	# or other user lib:
	my_module.add_depend([
	    'lib-name1',
	    'lib-name2'
	    ])
	
	# Add an optionnal dependency (set flag in CPP build if the subLib exist) ==> flag is locally set
	my_module.add_optionnal_depend('z', ["c++", "-DLIB_NAME_BUILD_ZLIB"])
	
	# Add an optionnal dependency (set flag in CPP build if the subLib exist) ==> flag is exported in external upper build
	my_module.add_optionnal_depend('z', ["c++", "-DLIB_NAME_BUILD_ZLIB"], export=True)
	
	# external flags:
	my_module.add_flag('link-lib', "pthread", export=True)
	my_module.add_flag('c++', "-DHELLO_FLAG=\"kljlkj\"", export=True)
	# internal flags:
	my_module.add_flag('c', "-DMODE_RELEASE")
	
	if target.get_mode() == "release":
		pass
	else:
		pass
	
	if "Windows" in target.get_type():
		pass
	elif "MacOs" in target.get_type():
		pass
	elif "IOs" in target.get_type():
		pass
	elif "Linux" in target.get_type():
		pass
	elif "Android" in target.get_type():
		pass
	
	# copy file in the share/binanyName/ path (no sub path)
	my_module.copy_path('data/icon.svg')
	
	my_module.copy_path('data/*', 'destinationPath')
	
	# Return True if the module is compatible with the target or ...
	return True
```


**Index:**
  - @ref mainpage
  - @ref lutin_concept
  - @ref lutin_use
  - @ref lutin_module

