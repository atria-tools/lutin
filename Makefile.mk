
# get the local dir in a good form :
#BUILD_SYSTEM := $(shell readlink -m -n $(patsubst %/,%,$(dir $(lastword $(MAKEFILE_LIST)))))
BUILD_SYSTEM := $(patsubst %/,%,$(dir $(lastword $(MAKEFILE_LIST))))

###############################################################################
### Platform specificity :                                                  ###
###############################################################################
SUPPORTED_PLATFORM=Linux Windows MacOs IOs Android
DEFAULT_PLATFORM=Linux

# default platform can be overridden
PLATFORM?=$(DEFAULT_PLATFORM)

PROJECT_PATH=$(shell pwd)

PROJECT_MODULE=$(shell readlink -n $(PROJECT_PATH)/../)

ifeq ($(PLATFORM), Linux)
    PROJECT_NDK?=$(shell readlink -n $$(PROJECT_MODULE)/ewol/)
else ifeq ($(PLATFORM), MacOs)
    TARGET_OS=MacOs
    PROJECT_NDK?=$$(PROJECT_MODULE)/ewol/
else ifeq ($(PLATFORM), IOs)
    
else ifeq ($(PLATFORM), Windows)
    
else ifeq ($(PLATFORM), Android)
    PROJECT_NDK:=$(shell readlink -n $(PROJECT_PATH)/../android/ndk/)
    PROJECT_SDK:=$(shell readlink -n $(PROJECT_PATH)/../android/sdk/)
else
    $(error you must specify a corect platform : make PLATFORM=[$(SUPPORTED_PLATFORM)])
endif

include $(BUILD_SYSTEM)/Makefile.$(PLATFORM).mk
