###############################################################################
## @author Edouard DUPIN
## @date 17-08-2012
## @project standard Build system
## @copyright BSDv3
###############################################################################

# for MAcOSX we need to FORCE CLANG
CLANG:=1
$(info =============>CLANG=$(CLANG))
# ewemple of a cross compiler :
# http://biolpc22.york.ac.uk/pub/linux-mac-cross/
# http://devs.openttd.org/~truebrain/compile-farm/apple-darwin9.txt


# include generic makefile :
include $(BUILD_SYSTEM)/main.mk


FINAL_FOLDER=         $(TARGET_OUT_FINAL)/$(PROJECT_NAME).app/Contents
FINAL_FOLDER_BIN=     $(FINAL_FOLDER)/MacOS
FINAL_FOLDER_DATA=    $(FINAL_FOLDER)/Resources

FINAL_FILE_INFO=$(FINAL_FOLDER)/Info.plist

# http://www.sandroid.org/imcross/#Deployment
final:
	@echo ------------------------------------------------------------------------
	@echo Final
	@echo ------------------------------------------------------------------------
	@echo 'Create Folders ...'
	@mkdir -p $(FINAL_FOLDER)
	@mkdir -p $(FINAL_FOLDER_BIN)
	@mkdir -p $(FINAL_FOLDER_DATA)
	# Create the info file
	@echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" > $(FINAL_FILE_INFO)
	@echo "<!DOCTYPE plist PUBLIC \"-//Apple Computer//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">" >> $(FINAL_FILE_INFO)
	@echo "<plist version=\"1.0\">" >> $(FINAL_FILE_INFO)
	@echo "    <dict>" >> $(FINAL_FILE_INFO)
	@echo "        <key>CFBundleExecutableFile</key>" >> $(FINAL_FILE_INFO)
	@echo "        <string>"$(PROJECT_NAME)"</string>" >> $(FINAL_FILE_INFO)
	@echo "        <key>CFBundleName</key>" >> $(FINAL_FILE_INFO)
	@echo "        <string>"$(PROJECT_NAME)"</string>" >> $(FINAL_FILE_INFO)
	@echo "        <key>CFBundleIdentifier</key>" >> $(FINAL_FILE_INFO)
	@echo "        <string>com."$(PROJECT_VENDOR)"."$(PROJECT_NAME)"</string>" >> $(FINAL_FILE_INFO)
	@echo "        <key>CFBundleIconFile</key>" >> $(FINAL_FILE_INFO)
	@echo "        <string>"$(PROJECT_NAME)".icns</string>" >> $(FINAL_FILE_INFO)
	@echo "    </dict>" >> $(FINAL_FILE_INFO)
	@echo "</plist>" >> $(FINAL_FILE_INFO)
	@echo "" >> $(FINAL_FILE_INFO)
	# copy program and data : 
	@cp -f $(TARGET_OUT_STAGING)/usr/bin/* $(FINAL_FOLDER_BIN)
	$(if $(wildcard ./share/*), cp -rf share/* $(FINAL_FOLDER_DATA))
	@echo pachage : TARBALL
	@cd $(TARGET_OUT_FINAL)/; tar -cf $(PROJECT_NAME).tar $(PROJECT_NAME).app
	@cd $(TARGET_OUT_FINAL)/; tar -czf $(PROJECT_NAME).tar.gz $(PROJECT_NAME).app

install: final
	@echo ------------------------------------------------------------------------
	@echo Install : ????
	@echo ------------------------------------------------------------------------
	

uninstall:
	@echo ------------------------------------------------------------------------
	@echo UnInstall : ????
	@echo ------------------------------------------------------------------------
	

