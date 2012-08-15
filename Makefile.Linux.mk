
USER_PACKAGES += $(EWOL_FOLDER)/Sources/

include $(EWOL_FOLDER)/Build/core/main.mk


# http://alp.developpez.com/tutoriels/debian/creer-paquet/
#package: .encadrer
#	@echo 'Create Folders ...'
#	@mkdir -p package/$(PROJECT_NAME)/DEBIAN/
#	@mkdir -p package/$(PROJECT_NAME)/usr/bin/
#	@mkdir -p package/$(PROJECT_NAME)/usr/share/doc/
#	@mkdir -p package/$(PROJECT_NAME)/usr/share/edn/
#	# Create the control file
#	@echo "Package: "$(PROJECT_NAME) > package/$(PROJECT_NAME)/DEBIAN/control
#	@echo "Version: "$(VERSION_TAG_SHORT) >> package/$(PROJECT_NAME)/DEBIAN/control
#	@echo "Section: Development,Editors" >> package/$(PROJECT_NAME)/DEBIAN/control
#	@echo "Priority: optional" >>package/$(PROJECT_NAME)/DEBIAN/control
#	@echo "Architecture: all" >> package/$(PROJECT_NAME)/DEBIAN/control
#	@echo "Depends: bash" >> package/$(PROJECT_NAME)/DEBIAN/control
#	@echo "Maintainer: Mr DUPIN Edouard <yui.heero@gmail.com>" >> package/$(PROJECT_NAME)/DEBIAN/control
#	@echo "Description: Text editor for sources code with ctags management" >> package/$(PROJECT_NAME)/DEBIAN/control
#	@echo "" >> package/$(PROJECT_NAME)/DEBIAN/control
#	# Create the PostRm
#	@echo "#!/bin/bash" > package/$(PROJECT_NAME)/DEBIAN/postrm
#	@echo "rm ~/."$(PROJECT_NAME) >> package/$(PROJECT_NAME)/DEBIAN/postrm
#	@echo "" >> package/$(PROJECT_NAME)/DEBIAN/postrm
#	# Enable Execution in script
#	@chmod 755 package/$(PROJECT_NAME)/DEBIAN/post*
#	@#chmod 755 package/$(PROJECT_NAME)/DEBIAN/pre*
#	# copy licence and information : 
#	@cp README package/$(PROJECT_NAME)/usr/share/doc/README
#	@cp licence.txt package/$(PROJECT_NAME)/usr/share/doc/copyright
#	@echo "First generation in progress" >> package/$(PROJECT_NAME)/usr/share/doc/changelog
#	@cp -vf $(PROJECT_NAME) package/$(PROJECT_NAME)/usr/bin/
#	@cp -vf data/*.xml package/$(PROJECT_NAME)/usr/share/edn/
#	@cd package; dpkg-deb --build $(PROJECT_NAME)
