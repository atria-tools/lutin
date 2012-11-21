###############################################################################
## @file defs.mk
## @author Edouard DUPIN
## @date 17-08-2012
## @project EWOL
##
## This file contains macros used by other makefiles.
###############################################################################

###############################################################################
## Some generic define
###############################################################################

quote := "
#"
simplequote := '
#'
coma := ,
empty :=
space := $(empty) $(empty)
space4 := $(space)$(space)$(space)$(space)
true := T
false :=

###############################################################################
## The folowing 2 macros can NOT be put in defs.mk as it will be included
## only after.
###############################################################################

# Get full path.
# $1 : path to extend.
fullpath = $(shell readlink -m -n $1)

# Figure out where we are
# It returns the full path without trailing '/'
my-dir = $(call fullpath,$(patsubst %/,%,$(dir $(lastword $(MAKEFILE_LIST)))))

###############################################################################
## Some useful macros.
###############################################################################


# Return negation of argument.
# $1 : input boolean argument.
not = $(if $1,$(false),$(true))

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

# remove many special char of a string ...
# Replace '-' by '_'
# Replace ' ' by '_'
# Replace '"' by ''
# Replace ''' by ''
# $1 : text to convert.
convert-special-char = $(call locase,\
                         $(subst $(quote),$(empty),\
                           $(subst $(simplequote),$(empty),\
                             $(subst -,_,\
                               $(subst $(space),_,$1)))))

# Remove quotes from string
remove-quotes = $(strip $(subst ",,$1))
#"

# Check that the current directory is the top directory
check-pwd-is-top-dir = \
	$(if $(patsubst $(TOP_DIR)%,%,$(shell pwd)), \
		$(error Not at the top directory))

# Compare 2 strings for equality.
# $1 : first string.
# $2 : second string.
streq = $(if $(filter-out xx,x$(subst $1,,$2)$(subst $2,,$1)x),$(false),$(true))

# Compare 2 strings for inequality.
# $1 : first string.
# $2 : second string.
strneq = $(call not,$(call streq,$1,$2))

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

# General libraries to add in dependency based on their actual class (STATIC/SHARED/EXTERNAL).
modules-LOCALS += LIBRARIES

# Additional include directories to pass into the C/C++ compilers
# Format : <fullpath> (-I will be prepended automatically)
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

# List of files to copy
# Format <src>:<dst>
# src : source (relative to module path)
# dst : destination (relative to staging dir)
modules-LOCALS += COPY_FILES
modules-LOCALS += COPY_FOLDERS

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

# This will only dump dependencies
modules-dump-database-depends = \
	$(foreach __mod,$(__modules), \
		$(info $(__mod):) \
		$(info $(space4)$(strip $(__modules.$(__mod).depends))) \
	)

###############################################################################
## Add a module in the build system and save its LOCAL_xxx variables.
## All LOCAL_xxx variables will be saved in module database.
###############################################################################
module-add = \
	$(eval LOCAL_MODULE := $(strip $(LOCAL_MODULE))) \
	$(if $(LOCAL_MODULE),$(empty), \
		$(error $(LOCAL_PATH): LOCAL_MODULE is not defined)) \
	$(eval __mod := $(LOCAL_MODULE)) \
	$(if $(call is-module-registered,$(__mod)), \
		$(eval __path := $(__modules.$(__mod).PATH)) \
		$(error $(LOCAL_PATH): module '$(__mod)' already registered at $(__path)) \
	) \
	$(eval __modules += $(__mod)) \
  $(foreach __local,$(modules-LOCALS), \
		$(eval __modules.$(__mod).$(__local) := $(LOCAL_$(__local))) \
  )

###############################################################################
## Check that a module is registered.
## $1 : module to check.
###############################################################################
is-module-registered = \
	$(strip $(foreach __mod,$(__modules), \
		$(if $(call streq,$(__mod),$1),$(true)) \
	))

###############################################################################
## Check that a module wil be built.
## $1 : module to check.
###############################################################################
is-module-in-build-config = \
	$(if $(BUILD_$(call get-define,$1)),$(true))


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
## Used to check all dependencies once all module information has been
## recorded.
###############################################################################

# Check dependencies of all modules
modules-check-depends = \
	$(foreach __mod,$(__modules), \
		$(call __module-check-depends,$(__mod)) \
	)

# Check dependency of a module
# $1 : module name.
__module-check-depends = \
	$(foreach __lib,$(__modules.$1.depends), \
		$(if $(call is-module-registered,$(__lib)),$(empty), \
			$(eval __path := $(__modules.$1.PATH)) \
			$(if $(call is-module-in-build-config,$1), \
				$(error $(__path): module '$1' depends on unknown module '$(__lib)'), \
				$(warning $(__path): module '$1' depends on unknown module '$(__lib)') \
			) \
		) \
	) \
	$(call __module-check-libs-class,$1,WHOLE_STATIC_LIBRARIES,STATIC_LIBRARY) \
	$(call __module-check-libs-class,$1,STATIC_LIBRARIES,STATIC_LIBRARY) \
	$(call __module-check-libs-class,$1,SHARED_LIBRARIES,SHARED_LIBRARY) \

# $1 : module name of owner.
# $2 : dependency to check (WHOLE_STATIC_LIBRARIES,STATIC_LIBRARIES,SHARED_LIBRARIES).
# $3 : class to check (STATIC_LIBRARY,SHARED_LIBRARY)
__module-check-libs-class = \
	$(foreach __lib,$(__modules.$1.$2), \
		$(call __module-check-lib-class,$1,$(__lib),$3) \
	)

# Check that a dependency is of the correct class
# $1 : module name of owner.
# $2 : library to check.
# $3 : class to check (STATIC_LIBRARY,SHARED_LIBRARY)
__module-check-lib-class = \
	$(if $(call strneq,$(__modules.$2.MODULE_CLASS),$3), \
		$(eval __path := $(__modules.$1.PATH)) \
		$(if $(call is-module-in-build-config,$1), \
			$(error $(__path): module '$1' depends on module '$2' which is not of class '$3'), \
			$(warning $(__path): module '$1' depends on module '$2' which is not of class '$3') \
		) \
	)

###############################################################################
## Used to make some internal checks.
###############################################################################

# Check variables of all modules
modules-check-variables = \
	$(foreach __mod,$(__modules), \
		$(call __module-check-variables,$(__mod)) \
	)

# Check variables of a module
# $1 : module name.
__module-check-variables = \
	$(call __module-check-src-files,$1) \
	$(call __module-check-c-includes,$1)

# Check that all files listed in LOCAL_SRC_FILES exist
# $1 : module name.
__module-check-src-files = \
	$(eval __path := $(__modules.$1.PATH)) \
	$(foreach __file,$(__modules.$1.SRC_FILES), \
		$(if $(wildcard $(__path)/$(__file)),$(empty), \
			$(warning $(__path): module '$1' uses missing source file '$(__file)') \
		) \
	)

# Check that all directory listed in LOCAL_C_INCLUDES exist
__module-check-c-includes = \
	$(eval __path := $(__modules.$1.PATH)) \
	$(foreach __inc,$(__modules.$1.C_INCLUDES), \
		$(eval __inc2 := $(patsubst -I%,%,$(__inc))) \
		$(if $(wildcard $(__inc2)),$(empty), \
			$(warning $(__path): module '$1' uses missing include '$(__inc2)') \
		) \
	)

###############################################################################
## Used to compute all dependencies once all module information has been
## recorded.
###############################################################################

# Compute dependencies of all modules
modules-compute-depends = \
    $(foreach __mod,$(__modules), \
		$(eval __modules.$(__mod).depends := $(empty)) \
		$(call __module-update-depends,$(__mod)) \
        $(call __module-compute-depends,$(__mod)) \
	)

# Update dependecies of a single module.
# It updates XXX_LIBRARIES based on LIBRARIES and actual dependency class.
# $1 : module name.
__module-update-depends = \
	$(foreach __lib,$(__modules.$1.LIBRARIES), \
		$(eval __class := $(__modules.$(__lib).MODULE_CLASS)) \
		$(if $(call streq,$(__class),STATIC_LIBRARY), \
			$(eval __modules.$1.STATIC_LIBRARIES += $(__lib)), \
			$(if $(call streq,$(__class),SHARED_LIBRARY), \
				$(eval __modules.$1.SHARED_LIBRARIES += $(__lib)), \
				$(eval __modules.$1.EXTERNAL_LIBRARIES += $(__lib)) \
			) \
		) \
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

###############################################################################
## Dependency management
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
		$(eval __closure_deps_uniq := $(empty)) \
		$(eval __closure_deps_full := $(empty)) \
		$(eval __closure_wq := $(strip $1)) \
		$(eval __closure_field := $(strip $2)) \
		$(if $(__closure_wq), $(call __modules-closure)) \
		$(strip $(call __modules-closure-finish,$(filter-out $1,$(__closure_deps_full))))

# Used internally by modules-get-all-dependencies. Note the tricky use of
# conditional recursion to work around the fact that the GNU Make language does
# not have any conditional looping construct like 'while'.
__modules-closure = \
		$(eval __closure_mod := $(call first,$(__closure_wq))) \
		$(eval __closure_wq  := $(call rest,$(__closure_wq))) \
		$(eval __closure_val := $(__modules.$(__closure_mod).$(__closure_field))) \
		$(eval __closure_new := $(filter-out $(__closure_deps_uniq),$(__closure_val))) \
		$(eval __closure_deps_uniq += $(__closure_new)) \
		$(eval __closure_deps_full += $(__closure_mod) $(__closure_val)) \
		$(eval __closure_wq  := $(strip $(__closure_wq) $(__closure_new))) \
		$(if $(__closure_wq),$(call __modules-closure))

# Finish dependency list by removing duplicates (keeping the last occurence)
__modules-closure-finish = $(strip \
		$(if $1, \
			$(eval __f := $(call first,$1)) \
			$(eval __r := $(call rest,$1)) \
			$(if $(filter $(__f),$(__r)),$(empty),$(__f)) \
			$(call __modules-closure-finish,$(__r)) \
		))

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
## Normalize a list of includes. It adds -I if needed.
## $1 : list of includes
###############################################################################
normalize-c-includes = \
	$(strip $(foreach __inc,$1, \
		$(addprefix -I,$(patsubst -I%,%,$(__inc))) \
	))

###############################################################################
## Commands for running gcc to generate a precompiled file.
###############################################################################

define transform-h-to-gch
@mkdir -p $(dir $@)
@echo "Precompile: $(PRIVATE_MODULE) <== $(call path-from-top,$<)"
$(call check-pwd-is-top-dir)
$(Q)$(CCACHE) $(TARGET_CXX) \
	-o $@ \
	$(TARGET_GLOBAL_C_INCLUDES) \
	$(PRIVATE_C_INCLUDES) \
	$(TARGET_GLOBAL_CFLAGS) $(TARGET_GLOBAL_CPPFLAGS) $(CXX_FLAGS_WARNINGS) \
	$(PRIVATE_CFLAGS) $(PRIVATE_CPPFLAGS) \
	$(TARGET_PCH_FLAGS) -MMD -MP \
	$(call path-from-top,$<)
endef

###############################################################################
## Commands for running gcc to compile a C++ file.
###############################################################################

define transform-cpp-to-o
@mkdir -p $(dir $@)
@echo "$(DISPLAY_ARM_MODE)C++: $(PRIVATE_MODULE) <== $(call path-from-top,$<)"
$(call check-pwd-is-top-dir)
$(Q)$(CCACHE) $(TARGET_CXX) \
	-o $@ \
	$(TARGET_GLOBAL_C_INCLUDES) \
	$(PRIVATE_C_INCLUDES) \
	$(TARGET_GLOBAL_CFLAGS_$(PRIVATE_ARM_MODE)) \
	$(TARGET_GLOBAL_CFLAGS) $(TARGET_GLOBAL_CPPFLAGS) $(CXX_FLAGS_WARNINGS) \
	$(PRIVATE_CFLAGS) $(PRIVATE_CPPFLAGS) \
	-D__EWOL_APPL_NAME__="$(PROJECT_NAME2)" \
	-c -MMD -MP -g \
	$(call path-from-top,$<)
endef

###############################################################################
## Commands for running gcc to compile a C file.
###############################################################################

define transform-c-to-o
@echo "$(DISPLAY_ARM_MODE)C: $(PRIVATE_MODULE) <== $(call path-from-top,$<)"
$(call check-pwd-is-top-dir)
@mkdir -p $(dir $@)
$(Q)$(CCACHE) $(TARGET_CC) \
	-o $@ \
	$(TARGET_GLOBAL_C_INCLUDES) \
	$(PRIVATE_C_INCLUDES) \
	$(TARGET_GLOBAL_CFLAGS_$(PRIVATE_ARM_MODE)) \
	$(TARGET_GLOBAL_CFLAGS) $(CC_FLAGS_WARNINGS) \
	$(PRIVATE_CFLAGS) \
	-D__EWOL_APPL_NAME__="$(PROJECT_NAME2)" \
	-c -MMD -MP -g \
	$(call path-from-top,$<)
endef

###############################################################################
## Commands for running gcc to compile a S file.
###############################################################################

define transform-s-to-o
@ echo "ASM: $(PRIVATE_MODULE) <== $(call path-from-top,$<)"
$(call check-pwd-is-top-dir)
@mkdir -p $(dir $@)
$(Q)$(CCACHE) $(TARGET_CC) \
	-o $@ \
	$(TARGET_GLOBAL_C_INCLUDES) \
	$(PRIVATE_C_INCLUDES) \
	$(TARGET_GLOBAL_CFLAGS_$(PRIVATE_ARM_MODE)) \
	$(TARGET_GLOBAL_CFLAGS) $(CC_FLAGS_WARNINGS) \
	$(PRIVATE_CFLAGS) \
	-c -MMD -MP -g \
	-D__EWOL_APPL_NAME__="$(PROJECT_NAME2)" \
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
$(Q)$(TARGET_AR) $(TARGET_GLOBAL_ARFLAGS) $(PRIVATE_ARFLAGS) $@ $(PRIVATE_ALL_OBJECTS)
$(Q)$(TARGET_RANLIB) $@
endef

###############################################################################
## Commands for running gcc to link a shared library.
###############################################################################

define transform-o-to-shared-lib
@mkdir -p $(dir $@)
@echo "SharedLib: $(PRIVATE_MODULE) ==> $(call path-from-top,$@)"
$(call check-pwd-is-top-dir)
$(Q)$(TARGET_CXX) \
	-o $@ \
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
@# TODO : Set LD ...
$(Q)$(TARGET_CXX) \
	-o $@ \
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
	$(PRIVATE_LDLIBS) \
	$(TARGET_GLOBAL_LDLIBS)
endef

###############################################################################
## Commands for copying files.
###############################################################################

# Copy a single file from one place to another, preserving permissions and
# overwriting any existing file.
define do-copy-file
@mkdir -p $(dir $@)
$(Q)cp -fp $< $@
endef

# Define a rule to copy a file.  For use via $(eval).
# $(1) : source file
# $(2) : destination file
define copy-one-file
$(2): $(1)
	@echo "Copy: $$(call path-from-top,$$<) => $$(call path-from-top,$$@)"
	$$(do-copy-file)
endef

###############################################################################
## Commands callable from user makefiles.
###############################################################################

# Get local path
local-get-path = $(call my-dir)

# Get build directory
local-get-build-dir = $(call module-get-build-dir,$(LOCAL_MODULE))

# Register module
local-add-module = $(module-add)

