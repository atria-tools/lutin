###############################################################################
## @file setup.mk
## @author Edouard DUPIN
## @date 17-08-2012
## @project EWOL
###############################################################################

###############################################################################
## Make sure that there are no spaces in the absolute path; the build system
## can't deal with them.
###############################################################################

ifneq ("$(words $(shell pwd))","1")
	$(error Top directory contains space characters)
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
