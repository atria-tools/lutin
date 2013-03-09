###############################################################################
## @file setup-host.mk
## @author Edouard DUPIN
## @date 17-08-2012
## @project EWOL
###############################################################################

# check if the user does not decide to force an other HOST_OS
ifneq ("$(HOST_OS)","")
	$(error User must not define $(HOST_OS))
endif

###############################################################################
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
ifneq ("$(shell echo $$OSTYPE | grep msys)","")
	HOST_OS := Windows
	HOST_EXE_SUFFIX := .exe
	HOST_SHARED_LIB_SUFFIX := .dll
	HOST_HAS_READLINK := true
else
	ifneq ("$(shell echo $$OSTYPE | grep darwin)","")
		HOST_OS := MacOs
		HOST_SHARED_LIB_SUFFIX := .dylib
		HOST_HAS_READLINK := false
	else
		HOST_OS := Linux
		HOST_SHARED_LIB_SUFFIX := .so
		HOST_HAS_READLINK := true
	endif
	HOST_EXE_SUFFIX :=
endif

