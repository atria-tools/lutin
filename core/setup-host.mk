###############################################################################
## @author Edouard DUPIN
## @date 17-08-2012
## @project standard Build system
## @copyright BSDv3
###############################################################################

##############################################################################
## Tools for host.
###############################################################################

ifneq ("$(CLANG)","1")
	HOST_CC := gcc
	HOST_CXX := g++
else
	HOST_CC := clang
	HOST_CXX := clang++
endif
HOST_AR := ar
HOST_LD := ld
HOST_NM := nm
HOST_STRIP := strip
HOST_RANLIB := ranlib
HOST_DLLTOOL := dlltool

###############################################################################
# Target global variables.
###############################################################################
HOST_GLOBAL_C_INCLUDES ?=
HOST_GLOBAL_CFLAGS ?=
HOST_GLOBAL_CPPFLAGS ?=
HOST_GLOBAL_ARFLAGS ?= rcs
HOST_GLOBAL_LDFLAGS ?=
HOST_GLOBAL_LDFLAGS_SHARED ?=
HOST_GLOBAL_LDLIBS ?=
HOST_GLOBAL_LDLIBS_SHARED ?=

# Host OS
ifeq ("$(HOST_OS)","Windows")
	HOST_EXE_SUFFIX := .exe
	HOST_SHARED_LIB_SUFFIX := .dll
else ifeq ("$(HOST_OS)","MacOs")
	HOST_EXE_SUFFIX :=
	HOST_SHARED_LIB_SUFFIX := .dylib
else ifeq ("$(HOST_OS)","IOs")
	$(error HOST_OS=$(HOST_OS) ==> not supported for compilation ... )
else ifeq ("$(HOST_OS)","Linux")
	HOST_EXE_SUFFIX :=
	HOST_SHARED_LIB_SUFFIX := .so
else ifeq ("$(HOST_OS)","Android")
	$(error HOST_OS=$(HOST_OS) ==> not supported for compilation ... )
else
	$(error HOST_OS=$(HOST_OS) ==> Unknow OS for compilation ... )
endif

