###############################################################################
## @file prebuilt.mk
## @author Y.M. Morgan
## @date 2012/08/08
##
## Register a prebuilt module.
###############################################################################

LOCAL_MODULE_CLASS := PREBUILT

ifeq ("$(LOCAL_MODULE_FILENAME)","")
LOCAL_MODULE_FILENAME := $(LOCAL_MODULE).done
endif

$(local-add-module)
