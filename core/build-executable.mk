###############################################################################
## @file executable.mk
## @author Edouard DUPIN
## @date 17-08-2012
## @project EWOL
##
## Register an executable (can be build).
###############################################################################

LOCAL_MODULE_CLASS := EXECUTABLE

ifeq ("$(LOCAL_DESTDIR)","")
LOCAL_DESTDIR := usr/bin
endif

ifeq ("$(LOCAL_MODULE_FILENAME)","")
LOCAL_MODULE_FILENAME := $(LOCAL_MODULE)$(TARGET_EXE_SUFFIX)
endif

$(local-add-module)
