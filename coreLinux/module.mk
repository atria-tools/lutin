###############################################################################
## @file module.mk
## @author Y.M. Morgan
## @date 2012/04/17
##
## Build a module.
###############################################################################

# Bring back all LOCAL_XXX variables defined by LOCAL_MODULE
$(call module-restore-locals,$(LOCAL_MODULE))

copy_to_staging := 0

###############################################################################
## Static library.
###############################################################################

ifeq ("$(LOCAL_MODULE_CLASS)","STATIC_LIBRARY")

include $(RULES)

$(LOCAL_BUILD_MODULE): $(all_objects)
	$(transform-o-to-static-lib)

copy_to_staging := 1

endif

###############################################################################
## Shared library.
###############################################################################

ifeq ("$(LOCAL_MODULE_CLASS)","SHARED_LIBRARY")

include $(RULES)

$(LOCAL_BUILD_MODULE): $(all_objects) $(all_libraries)
	$(transform-o-to-shared-lib)

copy_to_staging := 1

endif

###############################################################################
## Executable.
###############################################################################

ifeq ("$(LOCAL_MODULE_CLASS)","EXECUTABLE")

include $(RULES)

$(LOCAL_BUILD_MODULE): $(all_objects) $(all_libraries)
	$(transform-o-to-executable)

copy_to_staging := 1

endif

###############################################################################
## Copy to staging dir
###############################################################################

ifeq ("$(copy_to_staging)","1")
$(eval $(call copy-one-file,$(LOCAL_BUILD_MODULE),$(LOCAL_STAGING_MODULE)))
endif

