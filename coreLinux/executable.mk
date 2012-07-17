###############################################################################
## @file executable.mk
## @author Y.M. Morgan
## @date 2011/05/14
##
## Build an executable.
###############################################################################

LOCAL_MODULE_CLASS := EXECUTABLE
LOCAL_DESTDIR := usr/bin

ifndef LOCAL_MODULE_FILENAME
LOCAL_MODULE_FILENAME := $(LOCAL_MODULE)$(TARGET_EXE_SUFFIX)
endif

$(call module-add,$(LOCAL_MODULE))
