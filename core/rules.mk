###############################################################################
## @author Edouard DUPIN
## @date 17-08-2012
## @project standard Build system
## @copyright BSDv3
###############################################################################

# Intermediate/Build directory
build_dir := $(TARGET_OUT_BUILD)/$(LOCAL_MODULE)

# Prepend some directories in include list
LOCAL_C_INCLUDES := $(build_dir) $(LOCAL_PATH) $(LOCAL_C_INCLUDES)

###############################################################################
## ARM specific checks.
###############################################################################
ifeq ("$(TARGET_ARCH)","ARM")
	# Make sure LOCAL_ARM_MODE is valid
	# If not set, use default mode
	# Convert to upper case for further use
	LOCAL_ARM_MODE := $(call upcase,$(strip $(LOCAL_ARM_MODE)))
	ifeq ("$(LOCAL_ARM_MODE)","")
		LOCAL_ARM_MODE := $(TARGET_DEFAULT_ARM_MODE)
	endif
	ifneq ("$(LOCAL_ARM_MODE)","ARM")
		ifneq ("$(LOCAL_ARM_MODE)","THUMB")
			$(error $(LOCAL_PATH): LOCAL_ARM_MODE is not valid : $(LOCAL_ARM_MODE))
		endif
	endif
	# for diplay :
	ifeq ("$(LOCAL_ARM_MODE)","")
		DISPLAY_ARM_MODE=
	else
		DISPLAY_ARM_MODE=$(LOCAL_ARM_MODE)_
	endif
	
	## Check that compilation flags do not include forbidden stuff.
	check-flags-arm-mode := -marm -mthumb
	check-flags = \
		$(foreach flags,$1, \
			$(if $(findstring $($3),$(flags)), \
				$(error $(LOCAL_PATH): $3 contains $(flags) : $2) \
			) \
		)
	
	# Check that -marm or -mthumb is not forced in compilation flags
	flags-arm-mode := -marm -mthumb
	check-message := please use LOCAL_ARM_MODE
	check-flags-arm-mode = $(call check-flags,$(flags-arm-mode),$(check-message),$1)
$(call check-flags-arm-mode,LOCAL_CFLAGS)
$(call check-flags-arm-mode,LOCAL_CPPFLAGS)
$(call check-flags-arm-mode,LOCAL_EXPORT_CFLAGS)
$(call check-flags-arm-mode,LOCAL_EXPORT_CPPFLAGS)
endif

###############################################################################
## List of sources, objects and libraries.
###############################################################################

mm_sources := $(filter %.mm,$(LOCAL_SRC_FILES))
mm_objects := $(addprefix $(build_dir)/,$(mm_sources:.mm=.o))

m_sources := $(filter %.m,$(LOCAL_SRC_FILES))
m_objects := $(addprefix $(build_dir)/,$(m_sources:.m=.o))

cpp_sources := $(filter %.cpp,$(LOCAL_SRC_FILES))
cpp_objects := $(addprefix $(build_dir)/,$(cpp_sources:.cpp=.o))

cxx_sources := $(filter %.cxx,$(LOCAL_SRC_FILES))
cxx_objects := $(addprefix $(build_dir)/,$(cxx_sources:.cxx=.o))

c_sources := $(filter %.c,$(LOCAL_SRC_FILES))
c_objects := $(addprefix $(build_dir)/,$(c_sources:.c=.o))

s_sources := $(filter %.s,$(LOCAL_SRC_FILES))
s_objects := $(addprefix $(build_dir)/,$(s_sources:.s=.o))

S_sources := $(filter %.S,$(LOCAL_SRC_FILES))
S_objects := $(addprefix $(build_dir)/,$(S_sources:.S=.o))

all_objects := \
	$(mm_objects) \
	$(m_objects) \
	$(cpp_objects) \
	$(cxx_objects) \
	$(c_objects) \
	$(s_objects) \
	$(S_objects)

# Get all static libraries this module depends on
LOCAL_STATIC_LIBRARIES += \
	$(call module-get-depends,$(LOCAL_STATIC_LIBRARIES),STATIC_LIBRARIES)
LOCAL_WHOLE_STATIC_LIBRARIES += \
	$(call module-get-depends,$(LOCAL_WHOLE_STATIC_LIBRARIES),WHOLE_STATIC_LIBRARIES)

# Also get shared libraries used by static libraries
LOCAL_SHARED_LIBRARIES += \
	$(call module-get-depends,$(LOCAL_STATIC_LIBRARIES),SHARED_LIBRARIES)
LOCAL_SHARED_LIBRARIES += \
	$(call module-get-depends,$(LOCAL_WHOLE_STATIC_LIBRARIES),SHARED_LIBRARIES)

# Get path
all_shared_libraries := \
	$(foreach lib,$(LOCAL_SHARED_LIBRARIES), \
		$(call module-get-staging-filename,$(lib)))
all_static_libraries := \
	$(foreach lib,$(LOCAL_STATIC_LIBRARIES), \
		$(call module-get-build-filename,$(lib)))
all_whole_static_libraries := \
	$(foreach lib,$(LOCAL_WHOLE_STATIC_LIBRARIES), \
		$(call module-get-build-filename,$(lib)))
all_external_libraries := \
	$(foreach lib,$(LOCAL_EXTERNAL_LIBRARIES), \
		$(TARGET_OUT_BUILD)/$(lib)/$(lib).done)

# all_libraries is used for the dependencies.
all_libraries := \
	$(all_shared_libraries) \
	$(all_static_libraries) \
	$(all_whole_static_libraries) \
	$(all_external_libraries)

###############################################################################
## Import of dependencies.
###############################################################################

# Get all modules we depend on
all_depends := $(call module-get-all-dependencies,$(LOCAL_MODULE))
all_depends := $(filter-out $(LOCAL_MODULE),$(all_depends))

# Get list of exported stuff by our dependencies
imported_CFLAGS        := $(call module-get-listed-export,$(all_depends),CFLAGS)
imported_CPPFLAGS      := $(call module-get-listed-export,$(all_depends),CPPFLAGS)
imported_C_INCLUDES    := $(call module-get-listed-export,$(all_depends),C_INCLUDES)
imported_LDLIBS        := $(call module-get-listed-export,$(all_depends),LDLIBS)
imported_PREREQUISITES := $(call module-get-listed-export,$(all_depends),PREREQUISITES)

# The imported/exported compiler flags are prepended to their LOCAL_XXXX value
# (this allows the module to override them).
LOCAL_CFLAGS     := $(strip $(imported_CFLAGS) $(LOCAL_EXPORT_CFLAGS) $(LOCAL_CFLAGS))
LOCAL_CPPFLAGS   := $(strip $(imported_CPPFLAGS) $(LOCAL_EXPORT_CPPFLAGS) $(LOCAL_CPPFLAGS))

# The imported/exported include directories are appended to their LOCAL_XXX value
# (this allows the module to override them)
LOCAL_C_INCLUDES := $(sort $(strip $(subst -I-I,-I,$(addprefix -I,$(LOCAL_C_INCLUDES) $(LOCAL_EXPORT_C_INCLUDES) $(imported_C_INCLUDES)))))

# Similarly, you want the imported/exported flags to appear _after_ the LOCAL_LDLIBS
# due to the way Unix linkers work (depending libraries must appear before
# dependees on final link command).
LOCAL_LDLIBS     := $(strip $(LOCAL_LDLIBS) $(LOCAL_EXPORT_LDLIBS) $(imported_LDLIBS))

# Get autoconf files only if we depend oursef or dependent librairies does ...
#TODO
has_autoconf := $(AUTOCONF_FILE)
#	$(call module-get-listed-autoconf,$(all_depends)) \
#	$(call module-get-autoconf,$(LOCAL_MODULE))

# Force their inclusion (space after -include and before comma is important)
LOCAL_CFLAGS += $(addprefix -include ,$(has_autoconf))

# List of all prerequisites (ours + dependencies)
all_prerequisites := \
	$(LOCAL_PREREQUISITES) \
	$(LOCAL_EXPORT_PREREQUISITES) \
	$(imported_PREREQUISITES)

# All autoconf files are prerequisites
all_prerequisites += $(has_autoconf)

# User makefile is also a prerequisite
all_prerequisites += $(LOCAL_PATH)/$(USER_MAKEFILE_NAME)

# External libraries are also prerequisites
all_prerequisites += $(all_external_libraries)

# Notify that we build with dependencies
LOCAL_CFLAGS += $(foreach __mod,$(all_depends), \
	-DBUILD_$(call get-define,$(__mod)))

###############################################################################
## Actual rules.
###############################################################################

# mm files
ifneq ("$(strip $(mm_objects))","")
$(mm_objects): $(build_dir)/%.o: $(LOCAL_PATH)/%.mm
	$(transform-mm-to-o)
-include $(mm_objects:%.o=%.d)
endif

# m files
ifneq ("$(strip $(m_objects))","")
$(m_objects): $(build_dir)/%.o: $(LOCAL_PATH)/%.m
	$(transform-m-to-o)
-include $(m_objects:%.o=%.d)
endif

# cpp files
ifneq ("$(strip $(cpp_objects))","")
$(cpp_objects): $(build_dir)/%.o: $(LOCAL_PATH)/%.cpp
	$(transform-cpp-to-o)
-include $(cpp_objects:%.o=%.d)
endif

# cxx files
ifneq ("$(strip $(cxx_objects))","")
$(cxx_objects): $(build_dir)/%.o: $(LOCAL_PATH)/%.cxx
	$(transform-cpp-to-o)
-include $(cxx_objects:%.o=%.d)
endif

# c files
ifneq ("$(strip $(c_objects))","")
$(c_objects): $(build_dir)/%.o: $(LOCAL_PATH)/%.c
	$(transform-c-to-o)
-include $(c_objects:%.o=%.d)
endif

# s files
# There is NO dependency files for raw asm code...
ifneq ("$(strip $(s_objects))","")
$(s_objects): $(build_dir)/%.o: $(LOCAL_PATH)/%.s
	$(transform-s-to-o)
endif

# S files
# There is dependency files for asm code...
ifneq ("$(strip $(S_objects))","")
$(S_objects): $(build_dir)/%.o: $(LOCAL_PATH)/%.S
	$(transform-s-to-o)
-include $(S_objects:%.o=%.d)
endif

# Additionnal clean
clean-$(LOCAL_MODULE):: PRIVATE_CLEAN_FILES += $(LOCAL_STAGING_MODULE)
clean-$(LOCAL_MODULE):: PRIVATE_CLEAN_DIRS += $(build_dir)

# Additional module dependencies
$(LOCAL_MODULE): $(LOCAL_BUILD_MODULE) $(LOCAL_STAGING_MODULE)

# Make sure all prerequisites files are generated first
ifneq ("$(all_prerequisites)","")
$(all_objects): $(all_prerequisites)
endif

###############################################################################
## Precompiled headers.
###############################################################################

LOCAL_PRECOMPILED_FILE := $(strip $(LOCAL_PRECOMPILED_FILE))
ifneq ("$(LOCAL_PRECOMPILED_FILE)","")

gch_file := $(build_dir)/$(LOCAL_PRECOMPILED_FILE).gch

# All objects will depends on the precompiled file
$(all_objects): $(gch_file)

# Make sure all prerequisites files are generated first
ifneq ("$(all_prerequisites)","")
$(gch_file): $(all_prerequisites)
endif

# Generate the precompiled file
$(gch_file): $(LOCAL_PATH)/$(LOCAL_PRECOMPILED_FILE)
	$(transform-h-to-gch)
-include $(gch_file:%.gch=%.d)

endif

###############################################################################
## Rule-specific variable definitions.
###############################################################################

$(LOCAL_TARGETS): PRIVATE_PATH := $(LOCAL_PATH)
$(LOCAL_TARGETS): PRIVATE_MODULE := $(LOCAL_MODULE)
$(LOCAL_TARGETS): PRIVATE_CFLAGS := $(LOCAL_CFLAGS)
$(LOCAL_TARGETS): PRIVATE_C_INCLUDES := $(LOCAL_C_INCLUDES)
$(LOCAL_TARGETS): PRIVATE_CPPFLAGS := $(LOCAL_CPPFLAGS)
$(LOCAL_TARGETS): PRIVATE_ARFLAGS := $(LOCAL_ARFLAGS)
$(LOCAL_TARGETS): PRIVATE_LDFLAGS := $(LOCAL_LDFLAGS)
$(LOCAL_TARGETS): PRIVATE_LDLIBS := $(LOCAL_LDLIBS)
$(LOCAL_TARGETS): PRIVATE_ARM_MODE := $(LOCAL_ARM_MODE)
$(LOCAL_TARGETS): PRIVATE_ALL_SHARED_LIBRARIES := $(all_shared_libraries)
$(LOCAL_TARGETS): PRIVATE_ALL_STATIC_LIBRARIES := $(all_static_libraries)
$(LOCAL_TARGETS): PRIVATE_ALL_WHOLE_STATIC_LIBRARIES := $(all_whole_static_libraries)
$(LOCAL_TARGETS): PRIVATE_ALL_EXTERNAL_LIBRARIES := $(all_external_libraries)
$(LOCAL_TARGETS): PRIVATE_ALL_OBJECTS := $(all_objects)

