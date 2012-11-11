###############################################################################
## @file config.mk
## @author Edouard DUPIN
## @date 17-08-2012
## @project EWOL
##
## Configuration management.
###############################################################################

# Tools (absolute path)
CONF := KCONFIG_NOTIMESTAMP=1 $(call fullpath,$(BUILD_SYSTEM)/conf)
QCONF := KCONFIG_NOTIMESTAMP=1 $(call fullpath,$(BUILD_SYSTEM)/qconf)


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


#TODO : REMOVED
#__get_module-config = $(CONFIG_ORIG_DIR)/$1.config

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
## Generate Config configuration for all librairies.
## $1 : destination file.
###############################################################################
define __generate-config
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
		echo "    Force build of module $(__mod)" >> $1; \
		echo "    or copy data in the staging area (.a too)" >> $1; \
	) \
	echo "endmenu" >> $1; \
	$(foreach __mod,$(__modules), \
		$(eval __build := BUILD_$(call get-define,$(__mod))) \
		$(eval __files := $(call __get_module-config-in-files,$(__mod))) \
		if [ "$(__files)" != "" ]; then \
			echo "menu $(__mod)" >> $1; \
			$(foreach __f,$(__files), \
				echo "    source $(call fullpath,$(__f))" >> $1; \
			) \
			echo "endmenu" >> $1; \
		fi; \
	)
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
	echo "conf: $(call path-from-top,$2) <== $(call path-from-top,$1)"; \
	mkdir -p $(dir $2); \
	sed \
		-e 's/^CONFIG_//' \
		-e 's/^\# CONFIG_/\# /' \
		-e 's/^\#\(.*\)/\/*\1 *\//' \
		-e 's/\(.*\)=\(.*\)/\#define \1 \2/' \
		-e 's/ y$$/ 1/' \
		-e 's/\\\"/\"/g' \
		$1 > $2;
endef

###############################################################################
## Rules.
###############################################################################
# File where global configuration is stored
CONFIG_GLOBAL_FOLDER := $(shell pwd)/config
CONFIG_GLOBAL_FILE := $(CONFIG_GLOBAL_FOLDER)/$(TARGET_OS).config

# Display the global configuration
.PHONY: config
config:
	@( \
		__tmpconfigin=$$(mktemp); \
		$(eval __config := $(CONFIG_GLOBAL_FILE)) \
		$(call __generate-config,$${__tmpconfigin}) \
		$(call __begin-conf,$(__config)) \
		$(call __exec-qconf,$${__tmpconfigin}) \
		$(call __end-conf,$(__config)) \
		rm -f $${__tmpconfigin}; \
	)

# Update the global configuration by selecting new option at their default value
.PHONY: config-update
config-update:
	@( \
		__tmpconfigin=$$(mktemp); \
		$(eval __config := $(CONFIG_GLOBAL_FILE)) \
		$(call __generate-config,$${__tmpconfigin}) \
		$(call __update-config,$${__tmpconfigin},$(__config)) \
		rm -f $${__tmpconfigin}; \
	)

# Check the global configuration
.PHONY: config-check
config-check:
	@( \
		__tmpconfigin=$$(mktemp); \
		$(eval __config := $(CONFIG_GLOBAL_FILE)) \
		$(call __generate-config,$${__tmpconfigin}) \
		$(call __check-config,$${__tmpconfigin},$(__config)) \
		rm -f $${__tmpconfigin}; \
	)
	@echo "Global configuration is up to date";

# create basic folder :
$(shell mkdir -p $(CONFIG_GLOBAL_FOLDER))
# check if config exist :
# TODO ...
-include $(CONFIG_GLOBAL_FILE)

#automatic generation of the config file when not existed (default case):
#.PHONY: $(CONFIG_GLOBAL_FILE)
#$(CONFIG_GLOBAL_FILE): config-update
#	echo "generating basic confing .. please restart"

$(CONFIG_GLOBAL_FILE):
	@#$(e rror "need to generate config : make ... config")

