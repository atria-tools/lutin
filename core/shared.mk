###############################################################################
## @file shared.mk
## @author Y.M. Morgan
## @date 2011/05/14
##
## Build a shared library.
###############################################################################

LOCAL_MODULE_CLASS := SHARED_LIBRARY
LOCAL_DESTDIR := usr/lib

ifeq ("$(LOCAL_MODULE_FILENAME)","")
LOCAL_MODULE_FILENAME := $(LOCAL_MODULE)$(TARGET_SHARED_LIB_SUFFIX)
endif

$(call module-add,$(LOCAL_MODULE))
