###############################################################################
## @file defs.mk
## @author Y.M. Morgan
## @date 2011/05/14
##
## This file contains macros used by other makefiles.
###############################################################################

###############################################################################
## Some useful macros.
###############################################################################
empty :=
space := $(empty) $(empty)
space4 := $(space)$(space)$(space)$(space)

# Return the first element of a list.
# $ 1 : input list.
first = $(firstword $1)

# Return the list with the first element removed.
# $ 1 : input list.
rest = $(wordlist 2,$(words $1),$1)

# Get a path relative to top directory.
# $1 : full path to convert.
path-from-top = $(patsubst $(TOP_DIR)%,.%,$1)

# Translate characters.
# $1 : text to convert.
# $2 : characters to convert from.
# $3 : characters to convert to.
tr = $(shell echo $1 | tr $2 $3)

# Convert to upper case.
# $1 : text to convert.
upcase = $(shell echo $1 | tr [:lower:] [:upper:])

# Convert to lower case.
# $1 : text to convert.
locase = $(shell echo $1 | tr [:upper:] [:lower:])

# Replace '-' by '_' and convert to upper case.
# $1 : text to convert.
get-define = $(strip $(call upcase,$(call tr,$1,-,_)))

# Remove quotes from string
remove-quotes = $(strip $(subst ",,$1))
#"

# Check that the current directory is the top directory
check-pwd-is-top-dir = \
	$(if $(patsubst $(TOP_DIR)%,%,$(shell pwd)), \
		$(error Not at the top directory))

###############################################################################
## Modules database.
## For each module 'mod', __modules.mod.<field> is used to store
## module-specific information.
###############################################################################
__modules := $(empty)

###############################################################################
## Clear a list of variables.
###############################################################################
clear-vars = $(foreach __varname,$1,$(eval $(__varname) := $(empty)))

###############################################################################
## List of LOCAL_XXX variables that can be set by makefiles.
###############################################################################
modules-LOCALS :=

# Path of the root of module
modules-LOCALS += PATH

# Name of what's supposed to be generated
modules-LOCALS += MODULE

# Override the name of what will be generated
modules-LOCALS += MODULE_FILENAME

# Source files to compile
# All files are relative to LOCAL_PATH
modules-LOCALS += SRC_FILES

# Static libraries that you want to include in your module
# Names of modules in the build system, without path/prefix/suffix
modules-LOCALS += STATIC_LIBRARIES

# Static libraries that you want to include as a whole in your module
# To generate a .so for ex
# Names of modules in the build system, without path/prefix/suffix
modules-LOCALS += WHOLE_STATIC_LIBRARIES

# Libraries you directly link against
# Names of modules in the build system, without path/prefix/suffix
modules-LOCALS += SHARED_LIBRARIES

# External libraries (not built directly by the build system rules)
# Used as dependencies to trigger indirect build.
modules-LOCALS += EXTERNAL_LIBRARIES

# Additional include directories to pass into the C/C++ compilers
# Format : <fullpath>
modules-LOCALS += C_INCLUDES

# Additional flags to pass into the C or C++ compiler
modules-LOCALS += CFLAGS

# Additional flags to pass into only the C++ compiler
modules-LOCALS += CPPFLAGS

# Additional flags to pass into the static library generator
modules-LOCALS += ARFLAGS

# Additional flags to pass into the linker
modules-LOCALS += LDFLAGS

# Additional libraries to pass into the linker
# Format : -l<name>
modules-LOCALS += LDLIBS

# Precompiled file
# Relative to LOCAL_PATH
modules-LOCALS += PRECOMPILED_FILE

# Arm compilation mode (arm or thumb)
modules-LOCALS += ARM_MODE

# Paths to config.in files to configure the module
# Relative to LOCAL_PATH
modules-LOCALS += CONFIG_FILES

# List of prerequisites for all objects
modules-LOCALS += PREREQUISITES

# Exported stuff (will be added in modules depending on this one)
modules-LOCALS += EXPORT_C_INCLUDES
modules-LOCALS += EXPORT_CFLAGS
modules-LOCALS += EXPORT_CPPFLAGS
modules-LOCALS += EXPORT_LDLIBS
modules-LOCALS += EXPORT_PREREQUISITES

# Module class : STATIC_LIBRARY SHARED_LIBRARY EXECUTABLE
modules-LOCALS += MODULE_CLASS

# Other variables used internally
modules-LOCALS += BUILD_MODULE
modules-LOCALS += STAGING_MODULE
modules-LOCALS += DESTDIR
modules-LOCALS += TARGETS

# the list of managed fields per module
modules-fields := \
	depends \
	$(modules-LOCALS)

###############################################################################
## Dump all module information. Only use this for debugging.
###############################################################################
modules-dump-database = \
    $(info Modules: $(__modules)) \
    $(foreach __mod,$(__modules), \
        $(info $(space4)$(__mod):) \
        $(foreach __field,$(modules-fields), \
            $(eval __fieldval := $(strip $(__modules.$(__mod).$(__field)))) \
            $(if $(__fieldval), \
                $(if $(filter 1,$(words $(__fieldval))), \
                    $(info $(space4)$(space4)$(__field): $(__fieldval)), \
                    $(info $(space4)$(space4)$(__field): ) \
                    $(foreach __fielditem,$(__fieldval), \
                        $(info $(space4)$(space4)$(space4)$(__fielditem)) \
                    ) \
                ) \
            ) \
        ) \
    ) \
    $(info --- end of modules list)

###############################################################################
## Add a module in the build system and save its LOCAL_xxx variables.
## $1 : name of module to add. All LOCAL_xxx variables will be saved in
## module database.
###############################################################################
module-add = \
  $(eval __modules += $1) \
  $(foreach __local,$(modules-LOCALS), \
    $(eval __modules.$1.$(__local) := $(LOCAL_$(__local))) \
  )

###############################################################################
## Restore the recorded LOCAL_XXX definitions for a given module. Called
## for each module once they have all been registered and their dependencies
## have been computed to actually define rules.
## $1 : name of module to restore.
###############################################################################
module-restore-locals = \
    $(foreach __local,$(modules-LOCALS), \
        $(eval LOCAL_$(__local) := $(__modules.$1.$(__local))) \
    )

###############################################################################
## Used to recompute all dependencies once all module information has been
## recorded.
###############################################################################

# Compute dependencies of all modules
modules-compute-dependencies = \
    $(foreach __mod,$(__modules), \
    	$(eval __modules.$(__mod).depends := ) \
        $(call __module-compute-depends,$(__mod)) \
    )

# Compute dependencies of a single module
# $1 : module name.
__module-compute-depends = \
    $(call __module-add-depends,$1,$(__modules.$1.STATIC_LIBRARIES)) \
    $(call __module-add-depends,$1,$(__modules.$1.WHOLE_STATIC_LIBRARIES)) \
    $(call __module-add-depends,$1,$(__modules.$1.SHARED_LIBRARIES)) \
    $(call __module-add-depends,$1,$(__modules.$1.EXTERNAL_LIBRARIES))

# Add dependencies to a module
# $1 : module name.
# $2 : list of modules to add in dependency list.
__module-add-depends = \
    $(eval __modules.$1.depends += $(filter-out $(__modules.$1.depends),$2))

###############################################################################
## Automatic extraction from dependencies of a module.
###############################################################################

# Return the recorded value of LOCAL_EXPORT_$2, if any, for module $1.
# $1 : module name.
# $2 : export variable name without LOCAL_EXPORT_ prefix (e.g. 'CFLAGS').
module-get-export = $(__modules.$1.EXPORT_$2)

# Return the recorded value of LOCAL_EXPORT_$2, if any, for modules listed in $1.
# $1 : list of module names.
# $2 : export variable name without LOCAL_EXPORT_ prefix (e.g. 'CFLAGS').
module-get-listed-export = \
    $(strip $(foreach __mod,$1, \
        $(call module-get-export,$(__mod),$2) \
    ))

# Return the autoconf.h file, if any, for module $1.
# $1 : module name.
module-get-autoconf = \
	$(if $(__modules.$1.CONFIG_FILES),$(TARGET_OUT_BUILD)/$1/autoconf-$1.h)

# Return the autoconf.h files, if any, for modules listed in $1.
# $1 : list of module names.
module-get-listed-autoconf = \
    $(strip $(foreach __mod,$1, \
        $(call module-get-autoconf,$(__mod)) \
    ))

###############################################################################
## Dependecy management
###############################################################################

# Return list all the <local-type> modules $1 depends on transitively.
# $1 : list of module names.
# $2 : local module type (e.g. SHARED_LIBRARIES).
module-get-depends = $(strip $(call __modules-get-closure,$1,$2))

# Return list of all the modules $1 depends on transitively.
# $1: list of module names.
module-get-all-dependencies = \
    $(strip $(call __modules-get-closure,$1,depends))

# Recursively get dependency of a modules
__modules-get-closure = \
	$(eval __closure_deps  := $(strip $1)) \
	$(if $(__closure_deps), \
		$(eval __closure_wq    := $(__closure_deps)) \
		$(eval __closure_field := $(strip $2)) \
		$(call __modules-closure)) \
	$(__closure_deps) \

# Used internally by modules-get-all-dependencies. Note the tricky use of
# conditional recursion to work around the fact that the GNU Make language does
# not have any conditional looping construct like 'while'.
__modules-closure = \
	$(eval __closure_mod := $(call first,$(__closure_wq))) \
	$(eval __closure_wq  := $(call rest,$(__closure_wq))) \
	$(eval __closure_val := $(__modules.$(__closure_mod).$(__closure_field))) \
	$(eval __closure_new := $(filter-out $(__closure_deps),$(__closure_val))) \
	$(eval __closure_deps += $(__closure_new)) \
	$(eval __closure_wq  := $(strip $(__closure_wq) $(__closure_new))) \
	$(if $(__closure_wq),$(call __modules-closure)) \

###############################################################################
## Get path of module main target file (in build or staging directory).
## $1 : module name.
###############################################################################
module-get-build-dir = \
	$(TARGET_OUT_BUILD)/$1

module-get-build-filename = \
	$(if $(__modules.$1.MODULE_FILENAME), $(TARGET_OUT_BUILD)/$1/$(__modules.$1.MODULE_FILENAME) )

module-get-staging-filename = \
	$(if $(__modules.$1.MODULE_FILENAME), $(TARGET_OUT_STAGING)/$(__modules.$1.DESTDIR)/$(__modules.$1.MODULE_FILENAME) )


###############################################################################
## Generate autoconf.h file from config file.
## $1 : input config file.
## $2 : output autoconf.h file.
##
## Remove CONFIG_ prefix.
## Remove CONFIG_ in commented lines.
## Put lines begining with '#' between '/*' '*/'.
## Replace 'key=value' by '#define key value'.
## Replace leading ' y' by ' 1'.
## Remove leading and trailing quotes from string.
## Replace '\"' by '"'.
###############################################################################
define generate-autoconf-file
	echo "Generating $(call path-from-top,$2) from $(call path-from-top,$1)"; \
	mkdir -p $(dir $2); \
	sed \
		-e 's/^CONFIG_//' \
		-e 's/^\# CONFIG_/\# /' \
		-e 's/^\#\(.*\)/\/*\1 *\//' \
		-e 's/\(.*\)=\(.*\)/\#define \1 \2/' \
		-e 's/ y$$/ 1/' \
		-e 's/\"\(.*\)\"/\1/' \
		-e 's/\\\"/\"/g' \
		$1 > $2;
endef

###############################################################################
## Commands for running gcc to generate a precompiled file.
###############################################################################

define transform-h-to-gch
@mkdir -p $(dir $@)
@echo "Precompile: $(PRIVATE_MODULE) <== $(call path-from-top,$<)"
$(call check-pwd-is-top-dir)
$(Q)$(CCACHE) $(GXX) \
	$(TARGET_GLOBAL_C_INCLUDES) $(PRIVATE_C_INCLUDES) \
	$(TARGET_GLOBAL_CFLAGS) $(TARGET_GLOBAL_CPPFLAGS) $(GXX_FLAGS_WARNINGS) \
	$(PRIVATE_CFLAGS) $(PRIVATE_CPPFLAGS) \
	$(TARGET_PCH_FLAGS) -MMD -MP -o $@ \
	$(call path-from-top,$<)
endef

###############################################################################
## Commands for running gcc to compile a C++ file.
###############################################################################

define transform-cpp-to-o
@mkdir -p $(dir $@)
@echo "$(DISPLAY_ARM_MODE)C++: $(PRIVATE_MODULE) <== $(call path-from-top,$<)"
$(call check-pwd-is-top-dir)
$(Q)$(CCACHE) $(GXX) \
	$(TARGET_GLOBAL_C_INCLUDES) $(PRIVATE_C_INCLUDES) \
	$(TARGET_GLOBAL_CFLAGS_$(PRIVATE_ARM_MODE)) \
	$(TARGET_GLOBAL_CFLAGS) $(TARGET_GLOBAL_CPPFLAGS) $(GXX_FLAGS_WARNINGS) \
	$(PRIVATE_CFLAGS) $(PRIVATE_CPPFLAGS) \
	-c -MMD -MP -g -o $@ \
	$(call path-from-top,$<)
endef

###############################################################################
## Commands for running gcc to compile a C file.
###############################################################################

define transform-c-to-o
@echo "$(DISPLAY_ARM_MODE)C: $(PRIVATE_MODULE) <== $(call path-from-top,$<)"
$(call check-pwd-is-top-dir)
@mkdir -p $(dir $@)
$(Q)$(CCACHE) $(GCC) \
	$(TARGET_GLOBAL_C_INCLUDES) $(PRIVATE_C_INCLUDES) \
	$(TARGET_GLOBAL_CFLAGS_$(PRIVATE_ARM_MODE)) \
	$(TARGET_GLOBAL_CFLAGS) $(GCC_FLAGS_WARNINGS) \
	$(PRIVATE_CFLAGS) \
	-c -MMD -MP -g -o $@ \
	$(call path-from-top,$<)
endef

###############################################################################
## Commands for running gcc to compile a S file.
###############################################################################

define transform-s-to-o
@ echo "ASM: $(PRIVATE_MODULE) <== $(call path-from-top,$<)"
$(call check-pwd-is-top-dir)
@mkdir -p $(dir $@)
$(Q)$(CCACHE) $(GCC) \
	$(TARGET_GLOBAL_C_INCLUDES) $(PRIVATE_C_INCLUDES) \
	$(TARGET_GLOBAL_CFLAGS_$(PRIVATE_ARM_MODE)) \
	$(TARGET_GLOBAL_CFLAGS) $(GCC_FLAGS_WARNINGS) \
	$(PRIVATE_CFLAGS) \
	-c -MMD -MP -g -o $@ \
	$(call path-from-top,$<)
endef

###############################################################################
## Commands for running ar.
###############################################################################

# Explicitly delete the archive first so that ar doesn't
# try to add to an existing archive.
define transform-o-to-static-lib
@mkdir -p $(dir $@)
@echo "StaticLib: $(PRIVATE_MODULE) ==> $(call path-from-top,$@)"
$(call check-pwd-is-top-dir)
@rm -f $@
$(Q)$(AR) $(TARGET_GLOBAL_ARFLAGS) $(PRIVATE_ARFLAGS) $@ $(PRIVATE_ALL_OBJECTS)
$(Q)$(RANLIB) $@
endef

###############################################################################
## Commands for running gcc to link a shared library.
###############################################################################

define transform-o-to-shared-lib
@mkdir -p $(dir $@)
@echo "SharedLib: $(PRIVATE_MODULE) ==> $(call path-from-top,$@)"
$(call check-pwd-is-top-dir)
$(Q)$(GXX) \
	$(TARGET_GLOBAL_LDFLAGS_SHARED) \
	-Wl,-Map -Wl,$(basename $@).map \
	-shared \
	-Wl,-soname -Wl,$(notdir $@) \
	-Wl,--no-undefined \
	$(PRIVATE_LDFLAGS) \
	$(PRIVATE_ALL_OBJECTS) \
	-Wl,--whole-archive \
	$(PRIVATE_ALL_WHOLE_STATIC_LIBRARIES) \
	-Wl,--no-whole-archive \
	-Wl,--as-needed \
	$(PRIVATE_ALL_STATIC_LIBRARIES) \
	$(PRIVATE_ALL_SHARED_LIBRARIES) \
	-o $@ \
	$(PRIVATE_LDLIBS) \
	$(TARGET_GLOBAL_LDLIBS_SHARED)
endef

###############################################################################
## Commands for running gcc to link an executable.
###############################################################################

define transform-o-to-executable
@mkdir -p $(dir $@)
@echo "Executable: $(PRIVATE_MODULE) ==> $(call path-from-top,$@)"
$(call check-pwd-is-top-dir)
$(Q)$(GXX) \
	$(TARGET_GLOBAL_LDFLAGS) \
	-Wl,-Map -Wl,$(basename $@).map \
	-Wl,-rpath-link=$(TARGET_OUT_STAGING)/lib \
	-Wl,-rpath-link=$(TARGET_OUT_STAGING)/usr/lib \
	$(PRIVATE_LDFLAGS) \
	$(PRIVATE_ALL_OBJECTS) \
	-Wl,--whole-archive \
	$(PRIVATE_ALL_WHOLE_STATIC_LIBRARIES) \
	-Wl,--no-whole-archive \
	-Wl,--as-needed \
	$(PRIVATE_ALL_STATIC_LIBRARIES) \
	$(PRIVATE_ALL_SHARED_LIBRARIES) \
	-o $@ \
	$(PRIVATE_LDLIBS) \
	$(TARGET_GLOBAL_LDLIBS)
endef

###############################################################################
## Commands for copying files.
###############################################################################

# Copy a single file from one place to another, preserving permissions and
# overwriting any existing file.
define copy-file-to-target
@mkdir -p $(dir $@)
$(Q)cp -fp $< $@
endef

# Define a rule to copy a file.  For use via $(eval).
# $(1) : source file
# $(2) : destination file
define copy-one-file
$(2): $(1)
	@echo "Copy: $$(call path-from-top,$$@)"
	$$(copy-file-to-target)
endef

###############################################################################
## Default rules for a module.
## $1 : module name.
###############################################################################

define def-rules

.PHONY: $1
$1: $(call module-get-build-filename,$1)

.PHONY: clean-$1
clean-$1:
	@rm -f $(call module-get-build-filename,$1)
	@rm -rf $(call module-get-build-dir,$1)

endef

###############################################################################
## Commands callable from user makefiles.
###############################################################################

# Get local path
local-get-path = $(call my-dir)

# Get build directory
local-get-build-dir = $(call module-get-build-dir,$(LOCAL_MODULE))

# Register module
local-add-module = \
	$(call module-add,$(LOCAL_MODULE)) \
	$(eval $(call def-rules,$(LOCAL_MODULE)))

