Lutin Build system                               {#mainpage}
==================

@tableofcontents

`lutin` is a generic builder and package maker is a FREE software tool.


![Py package](https://badge.fury.io/py/lutin.png) https://pypi.python.org/pypi/lutin


Release (master)                                 {#lutin_mainpage_build_master}
================

![Build Status](https://travis-ci.org/HeeroYui/lutin.svg?branch=master) https://travis-ci.org/HeeroYui/lutin


Developement (dev)                               {#lutin_mainpage_build_dev}
==================

![Build Status](https://travis-ci.org/HeeroYui/lutin.svg?branch=dev) https://travis-ci.org/HeeroYui/lutin


What is Lutin?                                   {#lutin_mainpage_intro}
==============

Lutin is an application/library builder, it is designed to concurence CMake, Makefile, Ant, graddle ...

Lutin is deveopped in Python 2.x and 3.x to permit many user to play with it.

Python permit to Lutin to be used in many environement in a fast way.

Lutin support can compile every thing you want, just add a builder that you need (not in the common way). Basicly Lutin support languages:
  - C (ainsi/89/99) ==> .o;
  - C++ (98/99/03/11/14/...) ==> .o;
  - .S (assembleur) ==> .o;
  - .java ==> .class;
  - .class ==> jar;
  - .o ==> .a;
  - .o ==> .so;
  - .o/.a ==> binary.

Some packege can be generate for some platform:
  - debian package;
  - windows application zip;
  - MacOs application .app;
  - iOs package;
  - Android Package .apk.

Compilation is availlable for:
  - gcc/g++;
  - clang/clang++.

Manage **workspace build** (in oposition of CMake/make/...)


Install:                                         {#lutin_mainpage_installation}
========

Requirements: ``Python >= 2.7`` and ``pip``

Install lutin:
--------------

Just run:
```{.sh}
	pip install lutin
```

Install pip:
------------

Install pip on debian/ubuntu:
```{.sh}
	sudo apt-get install pip
```

Install pip on ARCH-linux:
```{.sh}
	sudo pacman -S pip
```

Install pip on MacOs:
```{.sh}
	sudo easy_install pip
```

Install from sources:
---------------------

```{.sh}
	git clone http://github.com/HeeroYui/lutin.git
	cd lutin
	sudo ./setup.py install
```

git repository                                   {#lutin_mainpage_repository}
==============

http://github.com/HeeroYui/lutin/

Tutorals:                                        {#lutin_mainpage_tutorial}
=========

  - @ref lutin_concept
  - @ref lutin_use
  - @ref lutin_module


License (APACHE v2.0)                            {#lutin_mainpage_licence}
=====================

Copyright lutin Edouard DUPIN

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


History:                                         {#lutin_mainpage_history}
========

I work with some builder, Every one have theire own adventages, and their problems.
The main point I see, is that the polimorphisme of the worktree is really hard.
The second point is the generation on different platforms is hard too.

Some other problem example:
  - Makefile is too slow on windows mingw;
  - Cmake does not create end point package;
  - none is really simple to write.

Then I create a simple interface that manage all I need. and written in python to permit to be faster on every platform.
