#!/usr/bin/python


TARGET_CC='gcc'
TARGET_CXX='g++'
TARGET_AR='ar'
TARGET_LD='ld'
TARGET_NM='nm'
TARGET_STRIP='strip'
TARGET_RANLIB='ranlib'
TARGET_DLLTOOL='dlltool'


###############################################################################
# Target global variables.
###############################################################################
TARGET_GLOBAL_C_INCLUDES=''
TARGET_GLOBAL_CFLAGS=''
TARGET_GLOBAL_CPPFLAGS=''
TARGET_GLOBAL_ARFLAGS='rcs'
TARGET_GLOBAL_LDFLAGS=''
TARGET_GLOBAL_LDFLAGS_SHARED=''
TARGET_GLOBAL_LDLIBS=''
TARGET_GLOBAL_LDLIBS_SHARED=''
TARGET_GLOBAL_CFLAGS_ARM=''
TARGET_GLOBAL_CFLAGS_THUMB=''

TARGET_STATIC_LIB_SUFFIX='.a'
TARGET_EXE_SUFFIX=''
TARGET_SHARED_LIB_SUFFIX='.so'
TARGET_OUT_FOLDER_BINARY='/usr/bin'
TARGET_OUT_FOLDER_LIBRAIRY='/usr/lib'
TARGET_OUT_FOLDER_DATA='/usr/share/'
TARGET_OUT_FOLDER_DOC='/usr/share/doc'
TARGET_OUT_PREFIX_LIBRAIRY=''
# define the target OS type for the compilation system ...
TARGET_GLOBAL_CFLAGS=' -D__TARGET_OS__Linux'
# basic define of the build time :
TARGET_GLOBAL_CFLAGS += ' -DBUILD_TIME="\"lkjlkjlkjlkjlkj\""'

"""
TARGET_GLOBAL_LDFLAGS = "-L$(TARGET_OUT_STAGING)/lib
TARGET_GLOBAL_LDFLAGS += -L$(TARGET_OUT_STAGING)/usr/lib
TARGET_GLOBAL_LDFLAGS_SHARED += -L$(TARGET_OUT_STAGING)/lib
TARGET_GLOBAL_LDFLAGS_SHARED += -L$(TARGET_OUT_STAGING)/usr/lib
"""