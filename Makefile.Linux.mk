

# Setup macros definitions
include $(BUILD_SYSTEM)/core/defs.mk

# include generic makefile :
include $(BUILD_SYSTEM)/core/check-project-variable.mk


TARGET_OUT_FOLDER_BINARY   := $(PROJECT_NAME2)/usr/bin
TARGET_OUT_FOLDER_LIBRAIRY := $(PROJECT_NAME2)/usr/lib
TARGET_OUT_FOLDER_DATA     := $(PROJECT_NAME2)/usr/share/$(PROJECT_NAME2)
TARGET_OUT_FOLDER_DOC      := $(PROJECT_NAME2)/usr/share/doc
TARGET_OUT_PREFIX_LIBRAIRY := 


# include generic makefile :
include $(BUILD_SYSTEM)/core/main.mk


TARGET_OUT_FOLDER_DEBIAN=$(TARGET_OUT_STAGING)/$(PROJECT_NAME2)/DEBIAN

FINAL_FILE_CONTROL=$(TARGET_OUT_FOLDER_DEBIAN)/control
FINAL_FILE_POST_RM=$(TARGET_OUT_FOLDER_DEBIAN)/postrm

FINAL_VERSION_TAG_SHORT=$(shell git describe --tags --abbrev=0)


# http://alp.developpez.com/tutoriels/debian/creer-paquet/
final: all
	@echo ------------------------------------------------------------------------
	@echo Final
	@echo ------------------------------------------------------------------------
	@echo 'Create Folders ...'
	@mkdir -p $(TARGET_OUT_FOLDER_DEBIAN)
	@mkdir -p $(TARGET_OUT_STAGING)/$(TARGET_OUT_FOLDER_DOC)
	# Create the control file
	@echo "Package: "$(PROJECT_NAME2) > $(FINAL_FILE_CONTROL)
	@echo "Version: "$(FINAL_VERSION_TAG_SHORT) >> $(FINAL_FILE_CONTROL)
	@echo "Section: "$(PROJECT_SECTION) >> $(FINAL_FILE_CONTROL)
	@echo "Priority: "$(PROJECT_PRIORITY) >> $(FINAL_FILE_CONTROL)
	@echo "Architecture: all" >> $(FINAL_FILE_CONTROL)
	@echo "Depends: bash" >> $(FINAL_FILE_CONTROL)
	@echo "Maintainer: "$(PROJECT_MAINTAINER) >> $(FINAL_FILE_CONTROL)
	@echo "Description: "$(PROJECT_DESCRIPTION) >> $(FINAL_FILE_CONTROL)
	@echo "" >> $(FINAL_FILE_CONTROL)
	# Create the PostRm
	@#echo "#!/bin/bash" > $(FINAL_FILE_POST_RM)
	@#echo "rm -r ~/.local/"$(PROJECT_NAME) >> $(FINAL_FILE_POST_RM)
	@#echo "" >> $(FINAL_FILE_POST_RM)
	# Enable Execution in script
	@#chmod 755 $(FINAL_FILE_POST_RM)*
	@#chmod 755 $(PROJECT_NAME)/DEBIAN/pre*
	@# copy licence and information : 
	@cp -f os-Linux/README $(TARGET_OUT_STAGING)/$(TARGET_OUT_FOLDER_DOC)/README
	@cp -f license.txt $(TARGET_OUT_STAGING)/$(TARGET_OUT_FOLDER_DOC)/copyright
	@cp -f changelog $(TARGET_OUT_STAGING)/$(TARGET_OUT_FOLDER_DOC)/changelog
	@echo pachage : $(TARGET_OUT_STAGING)/$(PROJECT_NAME).deb
	@cd $(TARGET_OUT_STAGING)/; dpkg-deb --build $(PROJECT_NAME)
	@mkdir -p $(TARGET_OUT_FINAL)
	@cp $(TARGET_OUT_STAGING)/$(PROJECT_NAME).deb $(TARGET_OUT_FINAL)/

install: final
	@echo ------------------------------------------------------------------------
	@echo Install : $(TARGET_OUT_FINAL)/$(PROJECT_NAME).deb
	@echo ------------------------------------------------------------------------
	sudo dpkg -i $(TARGET_OUT_FINAL)/$(PROJECT_NAME).deb

uninstall:
	@echo ------------------------------------------------------------------------
	@echo UnInstall : $(TARGET_OUT_FINAL)/$(PROJECT_NAME).deb
	@echo ------------------------------------------------------------------------
	sudo dpkg -r $(TARGET_OUT_FINAL)/$(PROJECT_NAME).deb

