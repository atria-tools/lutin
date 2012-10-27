###############################################################################
## @file module.mk
## @author Edouard DUPIN
## @date 17-08-2012
## @project EWOL
##
## Build a module.
###############################################################################

# Bring back all LOCAL_XXX variables defined by LOCAL_MODULE
$(call module-restore-locals,$(LOCAL_MODULE))

# Do we need to copy build module to staging dir
copy_to_staging := 0

# Full path to build module
LOCAL_BUILD_MODULE := $(call module-get-build-filename,$(LOCAL_MODULE))

# Full path to staging module
LOCAL_STAGING_MODULE := $(call module-get-staging-filename,$(LOCAL_MODULE))

# Assemble the list of targets to create PRIVATE_ variables for.
LOCAL_TARGETS := $(LOCAL_BUILD_MODULE) clean-$(LOCAL_MODULE)

# Add external libraries used by static libraries
LOCAL_EXTERNAL_LIBRARIES += \
	$(call module-get-depends,$(LOCAL_STATIC_LIBRARIES),EXTERNAL_LIBRARIES)
LOCAL_EXTERNAL_LIBRARIES += \
	$(call module-get-depends,$(LOCAL_WHOLE_STATIC_LIBRARIES),EXTERNAL_LIBRARIES)

# List of external libraries that we need to depend on
all_external_libraries := \
	$(foreach lib,$(LOCAL_EXTERNAL_LIBRARIES), \
		$(call module-get-build-filename,$(lib)))

###############################################################################
## Rule-specific variable definitions.
###############################################################################

$(LOCAL_TARGETS): PRIVATE_PATH := $(LOCAL_PATH)
$(LOCAL_TARGETS): PRIVATE_MODULE := $(LOCAL_MODULE)
$(LOCAL_TARGETS): PRIVATE_CLEAN_FILES := $(LOCAL_BUILD_MODULE)
$(LOCAL_TARGETS): PRIVATE_CLEAN_DIRS :=

###############################################################################
## General rules.
###############################################################################

# Short hand to build module
.PHONY: $(LOCAL_MODULE)
$(LOCAL_MODULE): $(LOCAL_BUILD_MODULE)

# Clean module (several other rules with commands can be added using ::)
.PHONY: clean-$(LOCAL_MODULE)
clean-$(LOCAL_MODULE)::
	@echo "Clean: $(PRIVATE_MODULE)"
	$(Q)$(if $(PRIVATE_CLEAN_FILES),rm -f $(PRIVATE_CLEAN_FILES))
	$(Q)$(if $(PRIVATE_CLEAN_DIRS),rm -rf $(PRIVATE_CLEAN_DIRS))

###############################################################################
## Static library.
###############################################################################

ifeq ("$(LOCAL_MODULE_CLASS)","STATIC_LIBRARY")

include $(BUILD_RULES)

$(LOCAL_BUILD_MODULE): $(all_objects)
	$(transform-o-to-static-lib)

copy_to_staging := 1

endif

###############################################################################
## Shared library.
###############################################################################

ifeq ("$(LOCAL_MODULE_CLASS)","SHARED_LIBRARY")

include $(BUILD_RULES)

$(LOCAL_BUILD_MODULE): $(all_objects) $(all_libraries)
	$(transform-o-to-shared-lib)

copy_to_staging := 1

endif

###############################################################################
## Executable.
###############################################################################

ifeq ("$(LOCAL_MODULE_CLASS)","EXECUTABLE")

include $(BUILD_RULES)

$(LOCAL_BUILD_MODULE): $(all_objects) $(all_libraries)
	$(transform-o-to-executable)

copy_to_staging := 1

endif

###############################################################################
## Prebuilt.
###############################################################################

ifeq ("$(LOCAL_MODULE_CLASS)","PREBUILT")

$(LOCAL_BUILD_MODULE):
	@mkdir -p $(dir $@)
	@touch $@

endif

###############################################################################
## Files to copy.
###############################################################################

ifneq ("$(LOCAL_COPY_FILES)","")

# List of all destination files
all_copy_files :=

# Generate a rule to copy all files
$(foreach __pair,$(LOCAL_COPY_FILES), \
	$(eval __pair2 := $(subst :,$(space),$(__pair))) \
	$(eval __src := $(addprefix $(LOCAL_PATH)/,$(word 1,$(__pair2)))) \
	$(eval __dst := $(TARGET_OUT_STAGING)/usr/share/$(PROJECT_NAME)/$(word 2,$(__pair2))) \
	$(foreach __file_src,$(__src), \
		$(eval all_copy_files += $(__dst)) \
		$(eval $(call copy-one-file,$(__file_src),$(__dst))) \
	) \
)

# Generate a rule to copy all files
$(foreach __pair,$(LOCAL_COPY_FOLDERS), \
	$(eval __pair2 := $(subst :,$(space),$(__pair))) \
	$(eval __folder_src  := $(addprefix $(LOCAL_PATH)/,$(word 1,$(__pair2)))) \
	$(eval __folder_dest := $(TARGET_OUT_STAGING)/usr/share/$(PROJECT_NAME)/$(word 2,$(__pair2))) \
	$(eval __list_file_src := $(wildcard $(__folder_src))) \
	$(foreach __file_src,$(__list_file_src), \
		$(eval __file_dest := $(__folder_dest)/$(notdir $(__file_src))) \
		$(eval all_copy_files += $(__file_dest)) \
		$(eval $(call copy-one-file,$(__file_src),$(__file_dest))) \
	) \
)

# Add files to be copied as pre-requisites
$(LOCAL_BUILD_MODULE): $(all_copy_files)

# Add rule to delete copied files during clean
clean-$(LOCAL_MODULE):: PRIVATE_CLEAN_FILES += $(all_copy_files)

endif

###############################################################################
## Copy to staging dir
###############################################################################

ifeq ("$(copy_to_staging)","1")
$(eval $(call copy-one-file,$(LOCAL_BUILD_MODULE),$(LOCAL_STAGING_MODULE)))
endif

