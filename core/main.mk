###############################################################################
## @file main.mk
## @author Edouard DUPIN
## @date 17-08-2012
## @project EWOL
##
## Main Makefile.
###############################################################################

###############################################################################
## General setup.
###############################################################################

# Make sure SHELL is correctly set
SHELL := /bin/bash

# This is the default target. It must be the first declared target.
all:

# Turns off suffix rules built into make
.SUFFIXES:

# Overridable settings
V := 0
W := 0
# debug mode of the software
DEBUG := 0
# compilation done with Clang system instead of gcc
CLANG := 0

# Quiet command if V is 0
ifeq ("$(V)","0")
  Q := @
endif

###############################################################################
## Build system setup.
###############################################################################

# Directories (full path)
TOP_DIR := $(shell pwd)
BUILD_SYSTEM := $(BUILD_SYSTEM)/core

ifeq ("$(DEBUG)","1")
	BUILD_DIRECTORY_MODE := debug
else
	BUILD_DIRECTORY_MODE := release
endif

# Setup configuration
include $(BUILD_SYSTEM)/setup-host.mk
include $(BUILD_SYSTEM)/setup-target.mk
include $(BUILD_SYSTEM)/setup.mk
# Setup warnings flags
include $(BUILD_SYSTEM)/warnings.mk
# Load configuration
include $(BUILD_SYSTEM)/config.mk

# Names of makefiles that can be included by user Makefiles
CLEAR_VARS := $(BUILD_SYSTEM)/clearvars.mk
BUILD_STATIC_LIBRARY := $(BUILD_SYSTEM)/build-static.mk
BUILD_SHARED_LIBRARY := $(BUILD_SYSTEM)/build-shared.mk
BUILD_EXECUTABLE := $(BUILD_SYSTEM)/build-executable.mk
BUILD_PREBUILT := $(BUILD_SYSTEM)/build-prebuilt.mk
BUILD_RULES := $(BUILD_SYSTEM)/rules.mk



###############################################################################
## Makefile scan and includes.
###############################################################################

TARGET_OUT_BUILD ?= $(shell pwd)/out/$(TARGET_OS)/$(BUILD_DIRECTORY_MODE)/obj
TARGET_OUT_STAGING ?= $(shell pwd)/out/$(TARGET_OS)/$(BUILD_DIRECTORY_MODE)/staging
TARGET_OUT_FINAL ?= $(shell pwd)/out/$(TARGET_OS)/$(BUILD_DIRECTORY_MODE)/final


# Note : Yhis permit to create a recursive search of all the .mk existed ==> but speed is really slow in Windows
ifeq ("$(USE_RECURSIVE_FIND)","1")
# Get the list of all makefiles available and include them this find the TARGET_OS.mk and the Generic.mk
_moduleFolder  = $(shell find $(USER_PACKAGES) -name $(TARGET_OS).mk)
_moduleFolder += $(shell find $(USER_PACKAGES) -name Generic.mk)
# only keep one folder for each makefile found.
_tmpDirectory  = $(sort $(dir $(_moduleFolder)))
else
_tmpDirectory := $(sort $(USER_PACKAGES))
endif
# this section have all the makefile possible for a specific target, 
# this isolate the good makefile for every folder where a makefile present
# for each folder
#    check if TARGET_OS.mk is present 
#        add it
#    otherwise
#        add generic makefile
$(foreach __makefile,$(_tmpDirectory), \
    $(if $(wildcard $(__makefile)/$(TARGET_OS).mk), \
        $(eval makefiles += $(__makefile)/$(TARGET_OS).mk) \
    , \
        $(if $(wildcard $(__makefile)/Generic.mk), \
            $(eval makefiles += $(__makefile)/Generic.mk) \
         ) \
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
$(call modules-compute-depends)

# Check dependencies
$(call modules-check-depends)

# Check variables of modules
$(call modules-check-variables)

###############################################################################
# Rule to merge autoconf.h files.
###############################################################################

# Concatenate all in one
AUTOCONF_FILE := $(TARGET_OUT_BUILD)/autoconf.h
$(AUTOCONF_FILE): $(CONFIG_GLOBAL_FILE)
	@mkdir -p $(dir $@)
	@rm -f $@
	@$(call generate-autoconf-file,$^,$@)


# Now, really generate rules for modules.
# This second pass allows to deal with exported values.
$(foreach __mod,$(__modules), \
    $(eval LOCAL_MODULE := $(__mod)) \
    $(eval include $(BUILD_SYSTEM)/module.mk) \
)

###############################################################################
# Main rules.
###############################################################################

# All modules
ALL_MODULES := \
	$(foreach __mod,$(__modules),$(__mod))

#TODO check this ...

# All module to actually build
ALL_BUILD_MODULES := \
	$(foreach __mod,$(__modules), \
		$(if $(call is-module-in-build-config,$(__mod)),$(__mod)))

ifeq ("$(V)","1")
$(info ALL_BUILD_MODULES=$(ALL_BUILD_MODULES))
endif

# TODO : Set ALL_BUILD_MODULES ==> find the end point module (SHARED/BINARY)
.PHONY: all
all: $(ALL_BUILD_MODULES)

.PHONY: clean
clean: $(foreach __mod,$(ALL_MODULES),clean-$(__mod))
	@rm -f $(AUTOCONF_MERGE_FILE)

# Dump the module database for debuging the build system
.PHONY: dump
dump:
	$(call modules-dump-database)

# Dump the module database for debuging the build system
.PHONY: dump-depends
dump-depends:
	$(call modules-dump-database-depends)

# Dummy target to check internal variables
.PHONY: check
check:

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
$(info TARGET_CC_PATH: $(TARGET_CC_PATH))
$(info TARGET_CC_VERSION: $(TARGET_CC_VERSION))
$(info CLANG: $(CLANG))
$(info ----------------------------------------------------------------------)
