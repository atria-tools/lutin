###############################################################################
## @author Edouard DUPIN
## @date 17-08-2012
## @project standard Build system
## @copyright BSDv3
###############################################################################

LOCAL_MODULE_CLASS := EXECUTABLE

ifeq ("$(LOCAL_DESTDIR)","")
LOCAL_DESTDIR := $(TARGET_OUT_FOLDER_BINARY)
endif

ifeq ("$(LOCAL_MODULE_FILENAME)","")
LOCAL_MODULE_FILENAME := $(LOCAL_MODULE)$(TARGET_EXE_SUFFIX)
endif

$(local-add-module)
