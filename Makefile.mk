###############################################################################
## @author Edouard DUPIN
## @date 17-08-2012
## @project standard Build system
## @copyright BSDv3
###############################################################################

###############################################################################
## General setup.
###############################################################################

# show for windows : http://benjamin.smedbergs.us/pymake/


# Make sure SHELL is correctly set
SHELL := /bin/bash

# This is the default target. It must be the first declared target.
all:

# Turns off suffix rules built into make
.SUFFIXES:

# Quiet command if V is 0
ifneq ("$(V)","1")
  Q := @
endif

###############################################################################
## Basic PATHS.
###############################################################################

# Directories (full path)
TOP_DIR := $(shell pwd)
#BUILD_SYSTEM := $(shell readlink -m -n $(patsubst %/,%,$(dir $(lastword $(MAKEFILE_LIST)))))
BUILD_SYSTEM_BASE := $(patsubst %/,%,$(dir $(lastword $(MAKEFILE_LIST))))
BUILD_SYSTEM := $(BUILD_SYSTEM_BASE)/core

###############################################################################
## Basic configurations.
###############################################################################

# Determine the Host-Os type :
include $(BUILD_SYSTEM)/setup-host-define-type.mk

# Setup macros definitions :
include $(BUILD_SYSTEM)/defs.mk

# include generic makefile :
include $(BUILD_SYSTEM)/check-project-variable.mk

###############################################################################
## Platform specificity :
##     - Linux 
##     - Windows
##     - MacOs
##     - IOs
##     - Android
##     - ... 
###############################################################################
SUPPORTED_PLATFORM=Linux Windows MacOs IOs Android
# By default we build for the current platform
DEFAULT_PLATFORM=$(HOST_OS)

# default platform can be overridden
PLATFORM?=$(DEFAULT_PLATFORM)

PROJECT_PATH=$(shell pwd)

PROJECT_MODULE=$(call fullpath,$(PROJECT_PATH)/../)

ifeq ($(filter $(PLATFORM), $(SUPPORTED_PLATFORM)), )
    OTHER_BORAD=true
    ifeq ("$(shell ls ./Makefile.$(PLATFORM).mk)","")
        $(error you must specify a corect platform : make PLATFORM=[$(SUPPORTED_PLATFORM) ...])
    endif
endif

# define the target OS of this system
TARGET_OS:=$(PLATFORM)



###############################################################################
## Build system setup.
###############################################################################

ifeq ("$(DEBUG)","1")
	BUILD_DIRECTORY_MODE := debug
else
	BUILD_DIRECTORY_MODE := release
endif

ifeq ("$(OTHER_BORAD)","true")
    include ./Makefile.$(PLATFORM).mk
else
    include $(BUILD_SYSTEM_BASE)/Makefile.$(PLATFORM).mk
endif
