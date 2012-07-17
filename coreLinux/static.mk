###############################################################################
## @file static.mk
## @author Y.M. Morgan
## @date 2011/05/14
##
## Build a static library.
###############################################################################

LOCAL_MODULE_CLASS := STATIC_LIBRARY
LOCAL_DESTDIR := usr/lib

ifndef LOCAL_MODULE_FILENAME
LOCAL_MODULE_FILENAME := $(LOCAL_MODULE)$(TARGET_STATIC_LIB_SUFFIX)
endif

$(call module-add,$(LOCAL_MODULE))
