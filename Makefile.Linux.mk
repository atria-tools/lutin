
APPL_DATA_FOLDER=/usr/share/$(PROJECT_NAME)

# include generic makefile :
include $(EWOL_FOLDER)/Build/core/main.mk


FINAL_FOLDER_DEBIAN=     $(TARGET_OUT_FINAL)/$(PROJECT_NAME)/DEBIAN
FINAL_FOLDER_BIN=        $(TARGET_OUT_FINAL)/$(PROJECT_NAME)/usr/bin
FINAL_FOLDER_LIB=        $(TARGET_OUT_FINAL)/$(PROJECT_NAME)/usr/lib
FINAL_FOLDER_SHARED_DOC= $(TARGET_OUT_FINAL)/$(PROJECT_NAME)/share/doc
FINAL_FOLDER_SHARED_DATA=$(TARGET_OUT_FINAL)/$(PROJECT_NAME)/share/$(PROJECT_NAME)

FINAL_FILE_CONTROL=$(FINAL_FOLDER_DEBIAN)/control
FINAL_FILE_POST_RM=$(FINAL_FOLDER_DEBIAN)/postrm

FINAL_VERSION_TAG_SHORT=$(shell git describe --tags --abbrev=0)

# http://alp.developpez.com/tutoriels/debian/creer-paquet/
final: all
	@echo ------------------------------------------------------------------------
	@echo Final
	@echo ------------------------------------------------------------------------
	@echo 'Create Folders ...'
	@mkdir -p $(FINAL_FOLDER_DEBIAN)
	@mkdir -p $(FINAL_FOLDER_BIN)
	@mkdir -p $(FINAL_FOLDER_SHARED_DOC)
	@mkdir -p $(FINAL_FOLDER_SHARED_DATA)
	# Create the control file
	@echo "Package: "$(PROJECT_NAME) > $(FINAL_FILE_CONTROL)
	@echo "Version: "$(FINAL_VERSION_TAG_SHORT) >> $(FINAL_FILE_CONTROL)
	@echo "Section: Development,Editors" >> $(FINAL_FILE_CONTROL)
	@echo "Priority: optional" >> $(FINAL_FILE_CONTROL)
	@echo "Architecture: all" >> $(FINAL_FILE_CONTROL)
	@echo "Depends: bash" >> $(FINAL_FILE_CONTROL)
	@echo "Maintainer: Mr DUPIN Edouard <yui.heero@gmail.com>" >> $(FINAL_FILE_CONTROL)
	@echo "Description: Text editor for sources code with ctags management" >> $(FINAL_FILE_CONTROL)
	@echo "" >> $(FINAL_FILE_CONTROL)
	# Create the PostRm
	@echo "#!/bin/bash" > $(FINAL_FILE_POST_RM)
	@echo "rm ~/."$(PROJECT_NAME) >> $(FINAL_FILE_POST_RM)
	@echo "" >> $(FINAL_FILE_POST_RM)
	# Enable Execution in script
	@chmod 755 $(FINAL_FILE_POST_RM)*
	@#chmod 755 $(PROJECT_NAME)/DEBIAN/pre*
	# copy licence and information : 
	@cp -f os-Linux/README $(FINAL_FOLDER_SHARED_DOC)/README
	@cp -f licence.txt $(FINAL_FOLDER_SHARED_DOC)/copyright
	@cp -f changelog $(FINAL_FOLDER_SHARED_DOC)/changelog
	@cp -f $(TARGET_OUT_STAGING)/usr/bin/* $(FINAL_FOLDER_BIN)
	$(if $(wildcard $(TARGET_OUT_STAGING)/usr/lib/*.so), cp -f $(TARGET_OUT_STAGING)/usr/lib/*.so $(FINAL_FOLDER_LIB))
	$(if $(wildcard ./share/*), cp -rf share/* $(FINAL_FOLDER_SHARED_DATA))
	@echo pachage <== $(TARGET_OUT_FINAL)/$(PROJECT_NAME).deb
	@cd $(TARGET_OUT_FINAL)/; dpkg-deb --build $(PROJECT_NAME)

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

