###############################################################################
## @file setup-target.mk
## @author Edouard DUPIN
## @date 17-08-2012
## @project EWOL
###############################################################################




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
else ifeq ("$(TARGET_OS)","Linux")
	
else ifeq ("$(TARGET_OS)","MacOs")
	
else ifeq ("$(TARGET_OS)","IOs")
	
endif


# define the target OS type for the compilation system ...
TARGET_GLOBAL_CFLAGS += -D__TARGET_OS__$(TARGET_OS)
# basic define of the build time :
TARGET_GLOBAL_CFLAGS += -DBUILD_TIME="\"$(shell date +%Y-%m-%d_%T)\""


ifeq ($(DEBUG),1)
	TARGET_GLOBAL_CFLAGS += -DDEBUG_LEVEL=3
	TARGET_GLOBAL_CFLAGS += -DDEBUG=1
	ifeq ("$(OPTIMISE)","1")
		TARGET_GLOBAL_CFLAGS += -O2
	endif
else
	TARGET_GLOBAL_CFLAGS += -DDEBUG_LEVEL=1
endif


# Pre-compiled header generation flag
ifneq ("$(CLANG)","1")
  TARGET_PCH_FLAGS := -c
else
  TARGET_PCH_FLAGS := -x c++-header
endif



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


