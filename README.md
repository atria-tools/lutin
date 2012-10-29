build
=====

`build` this is not a name ... but it is a FREE software tool.

Instructions
============

this is a makefile chain to generate the binary, shared lib and static lib independently of the OS

Create a makefile for all librairies
====================================

the makefile must be set directly in the root folder of the lib and named :
  * Generic.mk ==> if it was no special platform difined
  * Linux.mk ==> only for linux
  * Windows.mk ==> only for windows
  * Android.mk ==> only for android
  * Mac.mk ==> only for mac
  * Ios.mk ==> only for ios

==> if the platform specific file was not found, the system search the Generic.mk file


a minimal makefile for static lib :

	# requested for all makefile
	LOCAL_PATH := $(call my-dir)
	# remove previous variable of a module (remove all LOCAL_*** variable)
	include $(CLEAR_VARS)
	# librairie or program name
	LOCAL_MODULE    := exemple
	# list of sources files
	LOCAL_SRC_FILES := plop.cpp plop2.c
	# request the type of generation
	include $(BUILD_STATIC_LIBRARY)

you can have some other :

	# prebuild librairie ==> no comilation needed
	include $(BUILD_PREBUILT)
	# binary file generation (automatic add .exe at the end when windows binary)
	include $(BUILD_EXECUTABLE)
	# shared librairie (automatic .so or .dll when needed)
	include $(BUILD_SHARED_LIBRARY)


define include folder:

	# inside module
	LOCAL_C_INCLUDES := $(LOCAL_PATH)/monPath/
	# outside module >> automaticly added to LOCAL_C_INCLUDES
	LOCAL_EXPORT_C_INCLUDES := $(LOCAL_PATH)/mon/path/export

define c compilation flags : CFLAGS

	# inside module
	LOCAL_CFLAGS := -DEXEMPLE_TAG="\"SuperPlop\""
	# outside module
	LOCAL_EXPORT_CFLAGS := -DEXEMPLE_EXTERN_DEFINE

define linker flags:

	# local
	LOCAL_LDLIBS := -lm
	# expoerted
	LOCAL_EXPORT_LDLIBS := -lm

define dependency between librairies (note : automaticly include sub dependence of adependence

	LOCAL_LIBRARIES := etk tinyxml

copy files and folder :

	# use the makefile folder as reference and output is in the application data directory
	# copy secyfy file in the destination : folder/SRC.xxx:folderPLOP/folder/dst.yyy
	LOCAL_COPY_FILES := ../share/Font/freefont/FreeSerif.ttf:Font/freefont/FreeSerif.ttf
	# copy multiple file in a folder : (wildcard search) : folder/src*.txt:dstFolder
	LOCAL_COPY_FOLDERS := ../share/*.xml:/
	# note : the destination name is not needed ...


Copyright (c)
=============

2011, Edouard DUPIN

License (DSB)
=============

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

  1. Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.

  2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in
     the documentation and/or other materials provided with the
     distribution.

  3. The name of the author may not be used to endorse or promote
     products derived from this software without specific prior
     written permission.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT,
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
