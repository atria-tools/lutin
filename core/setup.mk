###############################################################################
## @file config.mk
## @author Y.M. Morgan
## @date 2011/05/14
###############################################################################

###############################################################################
## Make sure that there are no spaces in the absolute path; the build system
## can't deal with them.
###############################################################################

ifneq ("$(words $(shell pwd))","1")
	$(error Top directory contains space characters)
endif

###############################################################################
## Tools for target.
###############################################################################

ifneq ("$(CLANG)","1")
	TARGET_CC := $(TARGET_CROSS)gcc
	TARGET_CXX := $(TARGET_CROSS)g++
else
	TARGET_CC := $(TARGET_CROSS)clang
	TARGET_CXX := $(TARGET_CROSS)clang++
endif
TARGET_AR := $(TARGET_CROSS)ar
TARGET_LD := $(TARGET_CROSS)ld
TARGET_NM := $(TARGET_CROSS)nm
TARGET_STRIP := $(TARGET_CROSS)strip
TARGET_STRIP := $(TARGET_CROSS)strip
TARGET_RANLIB := $(TARGET_CROSS)ranlib
TARGET_DLLTOOL := $(TARGET_CROSS)dlltool

###############################################################################
## Tools for host.
###############################################################################
HOST_GCC ?= gcc
HOST_GXX ?= g++
HOST_AR ?= ar
HOST_LD ?= ld
HOST_NM ?= nm
HOST_STRIP ?= strip

###############################################################################
# Target global variables.
###############################################################################
TARGET_GLOBAL_C_INCLUDES ?=
TARGET_GLOBAL_CFLAGS ?=
TARGET_GLOBAL_CPPFLAGS ?=
TARGET_GLOBAL_ARFLAGS ?= rcs
TARGET_GLOBAL_LDFLAGS ?=
TARGET_GLOBAL_LDFLAGS_SHARED ?=
TARGET_GLOBAL_LDLIBS ?=
TARGET_GLOBAL_LDLIBS_SHARED ?=
TARGET_GLOBAL_CFLAGS_ARM ?=
TARGET_GLOBAL_CFLAGS_THUMB ?=

TARGET_PCH_FLAGS ?=
TARGET_DEFAULT_ARM_MODE ?= THUMB

###############################################################################
## Host/Target OS.
###############################################################################

# Host OS
ifneq ("$(shell echo $$OSTYPE | grep msys)","")
	HOST_OS := Windows
	HOST_EXE_SUFFIX := .exe
	HOST_SHARED_LIB_SUFFIX := .dll
else
	HOST_OS := Linux
	HOST_EXE_SUFFIX :=
	HOST_SHARED_LIB_SUFFIX := .so
endif

# Target OS : default to HOST_OS unless set
ifndef TARGET_OS
	TARGET_OS := $(HOST_OS)
endif

# Exe/dll suffix under mingw
TARGET_STATIC_LIB_SUFFIX := .a
ifeq ("$(TARGET_OS)","Windows")
	TARGET_EXE_SUFFIX := .exe
	TARGET_SHARED_LIB_SUFFIX := .dll
else
	TARGET_EXE_SUFFIX :=
	TARGET_SHARED_LIB_SUFFIX := .so
endif

ifeq ("$(TARGET_OS)","Windows")
	# may be overridden in make command line
	STATIC := 1
	TARGET_GLOBAL_CFLAGS += -D__MINGW_FEATURES__=0
	TARGET_GLOBAL_LDFLAGS += -Wl,--enable-auto-import
	ifeq ("$(STATIC)","1")
		TARGET_GLOBAL_LDFLAGS += -Wl,-Bstatic
	endif
	# remove CLANG if defined
	ifeq ("$(CLANG)","1")
        $(error CLANG is not supported on $(TARGET_OS) platform ==> disable it)
	endif
else ifeq ("$(TARGET_OS)","Android")
	TARGET_GLOBAL_CFLAGS += -D__ARM_ARCH_5__ -D__ARM_ARCH_5T__ -D__ARM_ARCH_5E__ -D__ARM_ARCH_5TE__ \
	                         -fpic -ffunction-sections -funwind-tables -fstack-protector \
	                         -Wno-psabi -march=armv5te -mtune=xscale -msoft-float -fno-exceptions -mthumb \
	                         -fomit-frame-pointer -fno-strict-aliasing -finline-limit=64 
	TARGET_GLOBAL_CPPFLAGS += -fno-rtti -Wa,--noexecstack
	TARGET_GLOBAL_LDFLAGS += 
	# remove CLANG if defined ==> TODO : Support it later ...
	ifeq ("$(CLANG)","1")
        $(error CLANG is not supported on $(TARGET_OS) platform ==> disable it)
	endif
endif

# define the target OS type for the compilation system ...
TARGET_GLOBAL_CFLAGS += -D__TARGET_OS__$(TARGET_OS)
# basic define of the build time :
TARGET_GLOBAL_CFLAGS += -DBUILD_TIME="\"$(shell date)\"" \

ifeq ($(DEBUG),1)
	TARGET_GLOBAL_CFLAGS += -DDEBUG_LEVEL=3
	ifeq ("$(OPTIMISE)","1")
		TARGET_GLOBAL_CFLAGS += -O2
	endif
else
	TARGET_GLOBAL_CFLAGS += -DDEBUG_LEVEL=1
endif


# To be able to use ccache with pre-complied headers, some env variables are required
CCACHE := 
ifeq ("$(CCACHE)","1")
	ifneq ("$(shell which ccache)","")
		CCACHE := CCACHE_SLOPPINESS=time_macros ccache
		TARGET_GLOBAL_CFLAGS += -fpch-preprocess
	endif
else
	CCACHE := 
endif

# Pre-compiled header generation flag
ifneq ("$(CLANG)","1")
  TARGET_PCH_FLAGS := -c
else
  TARGET_PCH_FLAGS := -x c++-header
endif

# Architecture
#ifndef TARGET_ARCH
#  ifneq ("$(shell $(TARGET_CC) -dumpmachine | grep 64)","")
#    TARGET_ARCH := AMD64
#  else
#    TARGET_ARCH := X86
#  endif
#endif

# Update flags based on architecture
# 64-bit requires -fPIC to build shared libraries
#ifeq ("$(TARGET_ARCH)","AMD64")
#  TARGET_GLOBAL_CFLAGS += -m64 -fPIC
#else
#  TARGET_GLOBAL_CFLAGS += -m32
#endif

TARGET_GLOBAL_LDFLAGS += -L$(TARGET_OUT_STAGING)/lib
TARGET_GLOBAL_LDFLAGS += -L$(TARGET_OUT_STAGING)/usr/lib
TARGET_GLOBAL_LDFLAGS_SHARED += -L$(TARGET_OUT_STAGING)/lib
TARGET_GLOBAL_LDFLAGS_SHARED += -L$(TARGET_OUT_STAGING)/usr/lib

###############################################################################
## Determine CC path and version. and check if installed ...
###############################################################################

TARGET_CC_PATH := $(shell which $(CC))

ifeq ("$(TARGET_CC_PATH)","")
    ifeq ("$(TARGET_OS)","Windows")
        $(error Compilator does not exist : $(TARGET_CC) ==> if not installed ... "apt-get install mingw32")
    else ifeq ("$(TARGET_OS)","Android")
        $(error Compilator does not exist : $(TARGET_CC) ==> add and define the android NDK "http://developer.android.com/tools/sdk/ndk/index.html")
    else
        ifneq ("$(CLANG)","1")
            $(error Compilator does not exist : $(TARGET_CC) ==> if not installed ... "apt-get install gcc g++")
        else
            $(error Compilator does not exist : $(TARGET_CC) ==> if not installed ... "apt-get install clang")
        endif
    endif
endif

ifneq ("$(CLANG)","1")
TARGET_CC_VERSION := $(shell $(TARGET_CC) --version | head -1 | sed "s/.*\([0-9]\.[0-9]\.[0-9]\).*/\1/")
else
TARGET_CC_VERSION := $(shell $(TARGET_CC) --version | head -1 | sed "s/.*\([0-9]\.[0-9]-[0-9]\).*/\1/")
endif
