###############################################################################
## @file config.mk
## @author Y.M. Morgan
## @date 2012/07/09
##
## Configuration management.
###############################################################################

# Tools (absolute path)
CONF := KCONFIG_NOTIMESTAMP=1 $(call fullpath,$(BUILD_SYSTEM)/conf)
QCONF := KCONFIG_NOTIMESTAMP=1 $(call fullpath,$(BUILD_SYSTEM)/qconf)

# Directory where original configurations are stored
CONFIG_ORIG_DIR := $(TOP_DIR)/config-ymm

# File where global configuration is stored
CONFIG_GLOBAL_FILE := $(CONFIG_ORIG_DIR)/global.config

###############################################################################
## Begin conf/qconf by copying configuration file to a temp .config file.
## $1 : configuration file.
###############################################################################
__begin-conf = \
	__tmpconfdir=$$(mktemp --directory); \
	__tmpconf=$${__tmpconfdir}/.config; \
	if [ -f $1 ]; then \
		cp -pf $1 $${__tmpconf}; \
	fi;

###############################################################################
## End conf/qconf by copying temp .config file to configuration file.
## $1 : configuration file.
###############################################################################
__end-conf = \
	if [ -f $${__tmpconf} ]; then \
		mv -f $${__tmpconf} $1; \
	fi; \
	rm -rf $${__tmpconfdir};

###############################################################################
## Exceute qconf/conf.
## $1 : Config.in file.
## $2 : options.
###############################################################################
__exec-conf = (cd $$(dirname $${__tmpconf}) && $(CONF) $2 $1);
__exec-qconf = (cd $$(dirname $${__tmpconf}) && $(QCONF) $2 $1);

###############################################################################
## Get the name of the configuration file of a module.
## $1 : module name.
###############################################################################
__get_module-config = $(CONFIG_ORIG_DIR)/$1.config

###############################################################################
## Get the list of path to Config.in files of a module.
## $1 : module name.
## Remark : should be called only after the module database have been built.
###############################################################################
__get_module-config-in-files = \
	$(eval __path := $(__modules.$1.PATH)) \
	$(eval __files := $(__modules.$1.CONFIG_FILES)) \
	$(addprefix $(__path)/,$(__files))

###############################################################################
## Begin the update/check operation by creating a temp diff file.
###############################################################################
__begin-diff = \
	__tmpdiff=$$(mktemp); \

###############################################################################
## End the update/check operation.
## $1 : 1 to exit, 0 or empty to continue.
###############################################################################
__end-diff = \
	if [ "$$(stat -c %s $${__tmpdiff})" != "0" ]; then \
		echo "Configuration diff can be found in $${__tmpdiff}"; \
		if [ "$1" == "1" ]; then exit 1; fi; \
	else \
		rm -f $${__tmpdiff}; \
	fi;

###############################################################################
## Generate Config.in for global configuration.
## $1 : destination file.
###############################################################################
define __generate-config-in-global
	rm -f $1; \
	mkdir -p $(dir $1); \
	touch $1; \
	echo "menu Modules" >> $1; \
	$(foreach __mod,$(__modules), \
		$(eval __build := BUILD_$(call get-define,$(__mod))) \
		echo "config $(__build)" >> $1; \
		echo "  bool 'Build $(__mod)'" >> $1; \
		echo "  default y" >> $1; \
		echo "  help" >> $1; \
		echo "    Build $(__mod)" >> $1; \
	) \
	echo "endmenu" >> $1;
endef

###############################################################################
## Generate Config.in for one module.
## $1 : destination file.
## $2 : module name.
## $3 : list of path to Config.in files.
###############################################################################
define __generate-config-in-module
	rm -f $1; \
	mkdir -p $(dir $1); \
	touch $1; \
	echo "menu $2" >> $1; \
	$(if $(strip $3), \
		$(foreach __f,$3, \
			echo "source $(call fullpath,$(__f))" >> $1; \
		) \
	) \
	echo "endmenu" >> $1;
endef

###############################################################################
## Update a configuration automatically.
## $1 Config.in input file.
## $2 current config file.
## $3 update config file (can be the same as $2).
###############################################################################
define __update-config-internal
	$(call __begin-conf,$2,) \
	(yes "" | $(call __exec-conf,$1,-o)) > /dev/null; \
	$(call __end-conf,$3)
endef

###############################################################################
## Update a configuration automatically.
## $1 Config.in input file.
## $2 current config file.
###############################################################################
define __update-config
	__tmpcheck=$$(mktemp); \
	$(call __update-config-internal,$1,$2,$${__tmpcheck}) \
	if ! cmp -s $2 $${__tmpcheck}; then \
		cp -pf $${__tmpcheck} $2; \
		echo "Configuration file $2 has been updated"; \
	fi; \
	rm -f $${__tmpcheck};
endef

###############################################################################
## Check a configuration.
## $1 Config.in input file.
## $2 current config file.
###############################################################################
define __check-config
	__tmpcheck=$$(mktemp); \
	if [ ! -f $2 ]; then \
		echo "Configuration file $2 does not exist" | tee $${__tmpdiff}; \
	else \
		$(call __update-config-internal,$1,$2,$${__tmpcheck}) \
		if ! cmp -s $2 $${__tmpcheck}; then \
			echo "Configuration file $2 is not up to date"; \
			diff -u $2 $${__tmpcheck} >> $${__tmpdiff}; \
		fi; \
	fi; \
	rm -f $${__tmpcheck};
endef

###############################################################################
## Load configuration of a module.
###############################################################################

# Do NOT check the config if a config is explicitely requested
define __load-config-internal
$(eval __config := $(call __get_module-config,$1))
-include $(__config)
ifeq ("$(findstring config,$(MAKECMDGOALS))","")
$(__config): __config-modules-check-$1
endif
endef

###############################################################################
## Load configuration of a module.
## Simply evaluate a call to simplify job of caller.
###############################################################################
load-config = $(eval $(call __load-config-internal,$(LOCAL_MODULE)))

###############################################################################
## Rules.
###############################################################################

# Update everything
.PHONY: config-update
config-update: config-global-update config-modules-update

# Check everything
.PHONY: config-check
config-check: config-global-check config-modules-check

# Display the global configuration
.PHONY: config-global
config-global:
	@( \
		__tmpconfigin=$$(mktemp); \
		$(eval __config := $(CONFIG_GLOBAL_FILE)) \
		$(call __generate-config-in-global,$${__tmpconfigin}) \
		$(call __begin-conf,$(__config)) \
		$(call __exec-qconf,$${__tmpconfigin}) \
		$(call __end-conf,$(__config)) \
		rm -f $${__tmpconfigin}; \
	)

# Update the global configuration by selecting new option at their default value
.PHONY: config-global-update
config-global-update:
	@( \
		__tmpconfigin=$$(mktemp); \
		$(eval __config := $(CONFIG_GLOBAL_FILE)) \
		$(call __generate-config-in-global,$${__tmpconfigin}) \
		$(call __update-config,$${__tmpconfigin},$(__config)) \
		rm -f $${__tmpconfigin}; \
	)

# Check the global configuration
.PHONY: config-global-check
config-global-check:
	@( \
		__tmpconfigin=$$(mktemp); \
		$(eval __config := $(CONFIG_GLOBAL_FILE)) \
		$(call __generate-config-in-global,$${__tmpconfigin}) \
		$(call __check-config,$${__tmpconfigin},$(__config)) \
		rm -f $${__tmpconfigin}; \
	)
	@echo "Global configuration is up to date";

# Update all module configurations by selecting new option at their default value
.PHONY: config-modules-update
config-modules-update:
	@( \
		$(foreach __mod,$(__modules), \
			$(eval __config := $(call __get_module-config,$(__mod))) \
			$(eval __files := $(call __get_module-config-in-files,$(__mod))) \
			if [ "$(__files)" != "" ]; then \
				__tmpconfigin=$$(mktemp); \
				$(call __generate-config-in-module,$${__tmpconfigin},$(__mod),$(__files)) \
				$(call __update-config,$${__tmpconfigin},$(__config)) \
				rm -f $${__tmpconfigin}; \
			fi; \
		) \
	)

# Update a specific module configuration by selecting new option at their default value
.PHONY: config-modules-update-%
config-modules-update-%:
	@( \
		$(eval __mod := $*) \
		$(eval __config := $(call __get_module-config,$(__mod))) \
		$(eval __files := $(call __get_module-config-in-files,$(__mod))) \
		if [ "$(__files)" != "" ]; then \
			__tmpconfigin=$$(mktemp); \
			$(call __generate-config-in-module,$${__tmpconfigin},$(__mod),$(__files)) \
			$(call __update-config,$${__tmpconfigin},$(__config)) \
			rm -f $${__tmpconfigin}; \
		fi; \
	)

# Check if module configurations are OK
.PHONY: config-modules-check
config-modules-check: __config-modules-check
	@echo "Modules configuration are up to date";

# Internal version with no message
.PHONY: __config-modules-check
__config-modules-check:
	@( \
		$(call __begin-diff) \
		$(foreach __mod,$(__modules), \
			$(eval __config := $(call __get_module-config,$(__mod))) \
			$(eval __files := $(call __get_module-config-in-files,$(__mod))) \
			if [ "$(__files)" != "" ]; then \
				__tmpconfigin=$$(mktemp); \
				$(call __generate-config-in-module,$${__tmpconfigin},$(__mod),$(__files)) \
				$(call __check-config,$${__tmpconfigin},$(__config)) \
				rm -f $${__tmpconfigin}; \
			fi; \
		) \
		$(call __end-diff,1) \
	)

# Check if a specific module configuration is OK
.PHONY: config-modules-check-%
config-modules-check-%: __config-modules-check-%
	$(eval __mod := $*)
	@echo "Configuration of $(__mod) is up to date";

# Internal version with no message
.PHONY: __config-modules-check-%
__config-modules-check-%:
	@( \
		$(call __begin-diff) \
		$(eval __mod := $*) \
		$(eval __config := $(call __get_module-config,$(__mod))) \
		$(eval __files := $(call __get_module-config-in-files,$(__mod))) \
		if [ "$(__files)" != "" ]; then \
			__tmpconfigin=$$(mktemp); \
			$(call __generate-config-in-module,$${__tmpconfigin},$(__mod),$(__files)) \
			$(call __check-config,$${__tmpconfigin},$(__config)) \
			rm -f $${__tmpconfigin}; \
		fi; \
		$(call __end-diff,1) \
	)

# Configure a module specifically
.PHONY: config-modules-%
config-modules-%:
	@( \
		$(eval __mod := $*) \
		$(eval __config := $(call __get_module-config,$(__mod))) \
		$(eval __files := $(call __get_module-config-in-files,$(__mod))) \
		if [ "$(__files)" == "" ]; then \
			echo "Nothing to configure for $(__mod)"; \
		else \
			__tmpconfigin=$$(mktemp); \
			$(call __generate-config-in-module,$${__tmpconfigin},$(__mod),$(__files)) \
			$(call __begin-conf,$(__config)) \
			$(call __exec-qconf,$${__tmpconfigin}) \
			$(call __end-conf,$(__config)) \
			rm -f $${__tmpconfigin}; \
			echo "Configuration of $(__mod) saved in $(__config)"; \
		fi; \
	)

