
###############################################################################
### Platform specificity :                                                  ###
###############################################################################
SUPPORTED_PLATFORM=Linux CygWin MacOS IOS Android
DEFAULT_PLATFORM=Linux

# default platform can be overridden
PLATFORM?=$(DEFAULT_PLATFORM)

PROJECT_PATH=$(shell pwd)

PROJECT_MODULE=$(PROJECT_PATH)/../

ifeq ($(PLATFORM), Linux)
    PROJECT_NDK?=$(realpath $(PROJECT_MODULE)/ewol/)
else ifeq ($(PLATFORM), MacOS)
    
else ifeq ($(PLATFORM), IOS)
    
else ifeq ($(PLATFORM), CygWin)
    
else ifeq ($(PLATFORM), Android)
    PROJECT_NDK:=$(PROJECT_MODULE)/android/ndk/
    PROJECT_SDK:=$(PROJECT_MODULE)/android/sdk/
else
    $(error you must specify a corect platform : make PLATFORM=$(SUPPORTED_PLATFORM))
endif

# get the compilation date and time :
BUILD_TIME=$(shell date)

EWOL_FOLDER?=$(realpath $(PROJECT_MODULE)/ewol)

include $(EWOL_FOLDER)/Build/Makefile.$(PLATFORM).mk
