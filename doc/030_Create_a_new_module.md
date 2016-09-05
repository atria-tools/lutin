Create a new Module:
====================

To create a new module you will use a generic naming:

```
	lutin_module-name.py
```

Replace your ``module-name`` with the delivery you want. The name can contain [a-zA-Z0-9\-_] values.

In the module name you must define some values:

```python
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
# @param[in] module_name Name of the module that is extract from the file name (to be generic)
def create(target, module_name):
	my_module = module.Module(__file__, module_name, get_type())
	...
	return my_module
```

Thes it is simple to specify build for:

Create a new Module (LIBRARY):
-----------------------------

What to change:
```python
def get_type():
	return "LIBRARY"
```

By default the library is compile in shared and static. The binary select the mode it prefer...

You can force the library to be compile as a dll/so: ```LIBRARY_DYNAMIC``` or a basic include lib: .a ```LIBRARY_STATIC```


Create a new Module (BINARY):
-----------------------------

Generic Binary:
***************

What to change:
```python
def get_type():
	return "BINARY"
```
The Binay is compile by default target mode (note that the IOs target generate a single .so with all the library inside)

You can force the Binary to be use dynamic library when possible: ```BINARY_SHARED``` or create a single binary with no .so depenency: ```BINARY_STAND_ALONE```

Create a new Module (TEST-BINARY / TOOL-BINARY):
************************************************

Two binary are really usefull in developpement, the tools and the test-unit, This is the reason why we specify for this 2 cases.

Add the subElement description:
```python
def get_type():
	return "BINARY"

def get_sub_type():
	return "TEST"
```
or:
```python
def get_type():
	return "BINARY"

def get_sub_type():
	return "TOOL"
```


Create a new Module (DATA):
---------------------------

This pode permit to only copy data and no dependency with compilling system

What to change:
```python
def get_type():
	return "DATA"
```


Module internal specifications:
===============================

Add file to compile:
--------------------

This is simple: (you just need to specify all the file to compile)

```python
def create(target, module_name):
	...
	
	# add the file to compile:
	my_module.add_src_file([
	    'module-name/file1.cpp',
	    'module-name/file2.cpp',
	    'module-name/file3.S'
	    ])
	
	...
```

Include directory & install header:
-----------------------------------

A big point to understand is that your library will be used by an other module, then it need to use headers.

The developper must isolate the external include and internal include, then lutin "install" the header and add the "install" header path to build the local library.
This permit to check error inclusion directly in developpement and separate the ```#include "XXX.h"``` and the ```#include <lib-xxx/XXX.h>```

Add file to external include:
```python
def create(target, module_name):
	...
	
	my_module.add_header_file([
	    'module-name/file1.h',
	    'module-name/file2.h'
	    ])
	
	...
```

You can add a path to your local include:
```python
def create(target, module_name):
	...
	
	my_module.add_path(os.path.join(tools.get_current_path(__file__), "lib-name"))
	
	...
```


Add Sub-dependency:
-------------------

All library need to add at minimum of a simple library (C lib) and other if needed. To do it jus call:
```python
def create(target, module_name):
	...
	
	# add dependency of the generic C library:
	my_module.add_module_depend('c')
	# add dependency of the generic C++ library:
	my_module.add_module_depend('cxx')
	# add dependency of the generic math library:
	my_module.add_module_depend('m')
	# or other user lib:
	my_module.add_module_depend('lib-name')
	
	...
```

The system can have optinnal sub-library, then if you just want to add an optionnal dependency:
```python
def create(target, module_name):
	...
	
	# Add an optionnal dependency (set flag in CPP build if the subLib exist) ==> flag is locally set
	my_module.add_optionnal_module_depend('z', ["c++", "-DLIB_NAME_BUILD_ZLIB"])
	
	# Add an optionnal dependency (set flag in CPP build if the subLib exist) ==> flag is exported in external upper build
	my_module.add_optionnal_module_depend('z', ["c++", "-DLIB_NAME_BUILD_ZLIB"], export=True)
	
	...
```

Compilation adn link flags/libs:
--------------------------------

It is possible to define local and external flags (external are set internal too):
```python
def create(target, module_name):
	...
	# external flags:
	my_module.add_flag('link-lib', "pthread", export=True)
	my_module.add_flag('c++', "-DHELLO_FLAG=\"kljlkj\"", export=True)
	# internal flags:
	my_module.add_flags('c', "-DMODE_RELEASE")
	
	...
```

build dependency mode and/or target:
------------------------------------

To add somes element dependent of the build mode:
```python
def create(target, module_name):
	...
	
	if target.get_mode() == "release":
		pass
	else:
		pass
	
	...
```

To add somes element dependent of the target type:

```python
def create(target, module_name):
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



Add some data in the install path (share path):
-----------------------------------------------

You can install a simple file:

```python
def create(target, module_name):
	...
	
	# copy file in the share/binanyName/ path (no sub path)
	my_module.copy_path('data/icon.svg')
	
	...
```

Copy multiple files (change path)

```python
def create(target, module_name):
	...
	
	my_module.copy_path('data/*', 'destinationPath')
	
	...
```

display some debug to help writing code:
----------------------------------------


```python
import lutin.debug as debug

def function(...):
	
	debug.error("comment that stop the build")
	debug.warning("comment that print a simple warning")
	debug.info("comment that print a simple information")
	debug.debug("comment that print a simple debug")
	debug.verbose("comment that print a simple verbose")
	
```

A Full template:
================

```
	lutin_module-name.py
```

```python
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

# Version of the library
# Note: this fucntion is optionnal.
def get_version():
	return [0,1,"dev"]

# create the module
# @param[in] target reference on the Target that is currently build
# @param[in] module_name Name of the module that is extract from the file name (to be generic)
def create(target, module_name):
	my_module = module.Module(__file__, module_name, get_type())
	
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
	my_module.add_module_depend('c')
	# add dependency of the generic C++ library:
	my_module.add_module_depend('cxx')
	# add dependency of the generic math library:
	my_module.add_module_depend('m')
	# or other user lib:
	my_module.add_module_depend([
	    'lib-name1',
	    'lib-name2'
	    ])
	
	# Add an optionnal dependency (set flag in CPP build if the subLib exist) ==> flag is locally set
	my_module.add_optionnal_module_depend('z', ["c++", "-DLIB_NAME_BUILD_ZLIB"])
	
	# Add an optionnal dependency (set flag in CPP build if the subLib exist) ==> flag is exported in external upper build
	my_module.add_optionnal_module_depend('z', ["c++", "-DLIB_NAME_BUILD_ZLIB"], export=True)
	
	# external flags:
	my_module.add_flag('link-lib', "pthread", export=True)
	my_module.add_flag('c++', "-DHELLO_FLAG=\"kljlkj\"", export=True)
	# internal flags:
	my_module.add_flags('c', "-DMODE_RELEASE")
	
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
	
	return my_module
```


