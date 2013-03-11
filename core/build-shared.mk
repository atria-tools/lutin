###############################################################################
## @author Edouard DUPIN
## @date 17-08-2012
## @project standard Build system
## @copyright BSDv3
###############################################################################

LOCAL_MODULE_CLASS := SHARED_LIBRARY

ifeq ("$(LOCAL_DESTDIR)","")
LOCAL_DESTDIR := $(TARGET_OUT_FOLDER_LIBRAIRY)
endif

ifeq ("$(LOCAL_MODULE_FILENAME)","")
LOCAL_MODULE_FILENAME := $(TARGET_OUT_PREFIX_LIBRAIRY)$(LOCAL_MODULE)$(TARGET_SHARED_LIB_SUFFIX)
endif

$(local-add-module)
