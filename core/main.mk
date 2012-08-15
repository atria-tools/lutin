###############################################################################
## @file main.mk
## @author Y.M. Morgan
## @date 2011/05/14
##
## Main Makefile.
###############################################################################

###############################################################################
## General setup.
###############################################################################

# Make sure SHELL is correctly set
SHELL := /bin/bash

# Turns off suffix rules built into make
.SUFFIXES:

# Overridable settings
V := 0
W := 0
DEBUG := 0
CLANG := 0

# Quiet command if V is 0
ifeq ("$(V)","0")
  Q := @
endif

# Tools for host
HOST_GCC ?= gcc
HOST_GXX ?= g++
HOST_AR ?= ar
HOST_LD ?= ld
HOST_STRIP ?= strip

# Tools for target
ifneq ("$(CLANG)","1")
	GCC ?= $(CROSS)gcc
	GXX ?= $(CROSS)g++
else
	GCC ?= $(CROSS)clang
	GXX ?= $(CROSS)clang++
endif
AR ?= $(CROSS)ar
LD ?= $(CROSS)ld
AS ?= $(CROSS)as
NM ?= $(CROSS)nm
STRIP ?= $(CROSS)strip
RANLIB ?= $(CROSS)ranlib
DLLTOOL ?= $(CROSS)dlltool
OBJDUMP ?= $(CROSS)objdump

# This is the default target. It must be the first declared target.
all:

# Target global variables
TARGET_GLOBAL_C_INCLUDES ?=
TARGET_GLOBAL_CFLAGS ?=
TARGET_GLOBAL_CPPFLAGS ?=
TARGET_GLOBAL_RCFLAGS ?=
TARGET_GLOBAL_ARFLAGS ?= rcs
TARGET_GLOBAL_LDFLAGS ?=
TARGET_GLOBAL_LDFLAGS_SHARED ?=
TARGET_GLOBAL_LDLIBS ?=
TARGET_GLOBAL_LDLIBS_SHARED ?=
TARGET_PCH_FLAGS ?=
TARGET_DEFAULT_ARM_MODE ?= THUMB
TARGET_GLOBAL_CFLAGS_ARM ?=
TARGET_GLOBAL_CFLAGS_THUMB ?=

###############################################################################
## The folowing 2 macros can NOT be put in defs.mk as it will be included
## only after.
###############################################################################

# Get full path.
# $1 : path to extend.
fullpath = $(shell readlink -m -n $1)

# Figure out where we are
# It returns the full path without trailing '/'
my-dir = $(call fullpath,$(patsubst %/,%,$(dir $(lastword $(MAKEFILE_LIST)))))

###############################################################################
## Build system setup.
###############################################################################

# Directories (full path)
TOP_DIR := $(shell pwd)
BUILD_SYSTEM := $(call my-dir)

# Setup configuration
include $(BUILD_SYSTEM)/setup.mk

# Setup macros definitions
include $(BUILD_SYSTEM)/defs.mk

# Setup warnings flags
include $(BUILD_SYSTEM)/warnings.mk

# Load configuration
include $(BUILD_SYSTEM)/config.mk

# Names of makefiles that can be included by user Makefiles
CLEAR_VARS := $(BUILD_SYSTEM)/clearvars.mk
BUILD_STATIC_LIBRARY := $(BUILD_SYSTEM)/static.mk
BUILD_SHARED_LIBRARY := $(BUILD_SYSTEM)/shared.mk
BUILD_EXECUTABLE := $(BUILD_SYSTEM)/executable.mk
RULES := $(BUILD_SYSTEM)/rules.mk

###############################################################################
## Makefile scan and includes.
###############################################################################
ifeq ("$(DEBUG)","1")
	BUILD_DIRECTORY_MODE := debug
else
	BUILD_DIRECTORY_MODE := release
endif

TARGET_OUT_BUILD ?= $(shell pwd)/out/$(TARGET_OS)/$(BUILD_DIRECTORY_MODE)/obj
TARGET_OUT_STAGING ?= $(shell pwd)/out/$(TARGET_OS)/$(BUILD_DIRECTORY_MODE)/obj
TARGET_OUT_FINAL ?= $(shell pwd)/out/$(TARGET_OS)/$(BUILD_DIRECTORY_MODE)/bin

# Makefile with the list of all makefiles available and include them
SCAN_TARGET := scan

#display the properties of the currend building folder ...
ifeq ("$(V)","1")
    $(info mydir="$(my-dir)")
    $(info pwd="$(shell pwd)")
    $(info TOP_DIR="$(TOP_DIR)")
    $(info USER_PACKAGES="$(USER_PACKAGES)")
    $(info list packet=$(shell find $(USER_PACKAGES) -name $(TARGET_OS).mk))
endif

# Get the list of all makefiles available and include them this find the TARGET_OS.mk and the Generic.mk
_moduleFolder  = $(shell find $(USER_PACKAGES) -name $(TARGET_OS).mk)
_moduleFolder += $(shell find $(USER_PACKAGES) -name Generic.mk)
# only keep one folder for each makefile found.
_tmpDirectory  = $(sort $(dir $(_moduleFolder)))
# this section have all the makefile possible for a specific target, 
# this isolate the good makefile for every folder where a makefile present
# for each folder
#    check if TARGET_OS.mk is present 
#        add it
#    otherwise
#        add generic makefile
$(foreach __makefile,$(_tmpDirectory), \
    $(if $(wildcard $(__makefile)$(TARGET_OS).mk), \
        $(eval makefiles += $(__makefile)$(TARGET_OS).mk) , \
        $(eval makefiles += $(__makefile)Generic.mk) \
    ) \
)
ifeq ("$(V)","1")
	$(info makefiles="$(makefiles)")
endif
# import all the makefiles
include $(makefiles)


###############################################################################
# Module dependencies generation.
###############################################################################

# Recompute all dependencies between modules
$(call modules-compute-dependencies)

# Now, really build the modules, the second pass allows to deal with exported values
$(foreach __mod,$(__modules), \
    $(eval LOCAL_MODULE := $(__mod)) \
    $(eval include $(BUILD_SYSTEM)/module.mk) \
)

###############################################################################
# Rule to merge autoconf.h files.
###############################################################################

# List of all available autoconf.h files
__autoconf-list := $(foreach __mod,$(__modules),$(call module-get-autoconf,$(__mod)))

# Concatenate all in one
AUTOCONF_MERGE_FILE := $(TARGET_OUT_BUILD)/autoconf-merge.h
$(AUTOCONF_MERGE_FILE): $(__autoconf-list)
	@echo "Generating autoconf-merge.h"
	@mkdir -p $(dir $@)
	@rm -f $@
	@for f in $^; do cat $$f >> $@; done

###############################################################################
# Main rules.
###############################################################################

.PHONY: all
all: $(foreach __mod,$(__modules),$(__mod)) $(AUTOCONF_MERGE_FILE)

.PHONY: clean
clean: $(foreach __mod,$(__modules),clean-$(__mod))
	@rm -f $(AUTOCONF_MERGE_FILE)

# Dump the module database for debuging the build system
.PHONY: dump
dump:
	$(call modules-dump-database)

###############################################################################
# Display configuration.
###############################################################################
$(info ----------------------------------------------------------------------)
$(info HOST_OS: $(HOST_OS))
$(info TARGET_OS: $(TARGET_OS))
$(info TARGET_ARCH: $(TARGET_ARCH))
$(info TARGET_OUT_BUILD: $(TARGET_OUT_BUILD))
$(info TARGET_OUT_STAGING: $(TARGET_OUT_STAGING))
$(info TARGET_OUT_FINAL: $(TARGET_OUT_FINAL))
$(info GCC_PATH: $(GCC_PATH))
$(info GCC_VERSION: $(GCC_VERSION))
$(info ----------------------------------------------------------------------)
