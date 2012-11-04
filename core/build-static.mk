###############################################################################
## @file static.mk
## @author Edouard DUPIN
## @date 17-08-2012
## @project EWOL
##
## Register a static library (can be build).
###############################################################################

LOCAL_MODULE_CLASS := STATIC_LIBRARY

ifeq ("$(LOCAL_DESTDIR)","")
LOCAL_DESTDIR := $(TARGET_OUT_FOLDER_LIBRAIRY)
endif

ifeq ("$(LOCAL_MODULE_FILENAME)","")
LOCAL_MODULE_FILENAME := $(LOCAL_MODULE)$(TARGET_STATIC_LIB_SUFFIX)
endif

$(local-add-module)
