

PROJECT_PACKAGE=$(PROJECT_NAME)package
JAVA_FOLDER=src/com/$(PROJECT_VENDOR)/$(PROJECT_NAME)
EWOL_JAVA_FOLDER=src/org/ewol


all:
	@echo "------------------------------------------------------------------------"
	@echo ' Project name    : $(PROJECT_NAME)'
	@echo ' Project Vendor  : $(PROJECT_VENDOR)'
	@echo ' Build date      : $(BUILD_TIME) '
	@echo ' Tag             : $(PROJECT_VERSION_TAG) '
	@echo "------------------------------------------------------------------------"
	
	@rm -rf bin
	
	@echo "    (sh) Clear previous sources "
	@rm -rf src jni/ewolAndroidAbstraction.cpp
	@echo "    (sh) Create folder : $(JAVA_FOLDER)/ & $(EWOL_JAVA_FOLDER)"
	@mkdir -p $(JAVA_FOLDER)/
	@mkdir -p $(EWOL_JAVA_FOLDER)/
	
	@echo "    (sh) copy the java Files & Replace __XXX__ element with project properties"
	@cp $(EWOL_FOLDER)/Java/PROJECT_NAME.java $(JAVA_FOLDER)/$(PROJECT_NAME).java
	@sed -i "s|__PROJECT_VENDOR__|$(PROJECT_VENDOR)|" $(JAVA_FOLDER)/$(PROJECT_NAME).java
	@sed -i "s|__PROJECT_NAME__|$(PROJECT_NAME)|" $(JAVA_FOLDER)/$(PROJECT_NAME).java
	@sed -i "s|__PROJECT_PACKAGE__|$(PROJECT_PACKAGE)|" $(JAVA_FOLDER)/$(PROJECT_NAME).java
	# copy the Ewol java files : 
	@cp $(EWOL_FOLDER)/Java/interfaceJNI.java $(EWOL_JAVA_FOLDER)/
	@cp $(EWOL_FOLDER)/Java/interfaceOpenGL.java $(EWOL_JAVA_FOLDER)/
	@cp $(EWOL_FOLDER)/Java/interfaceSurfaceView.java $(EWOL_JAVA_FOLDER)/
	@cp $(EWOL_FOLDER)/Java/interfaceAudio.java $(EWOL_JAVA_FOLDER)/
	
	@echo "    (sh) copy the cpp for jni File : $(EWOL_FOLDER)/SourcesJava/ewolAndroidAbstraction.cpp"
	@cp $(EWOL_FOLDER)/Java/ewolAndroidAbstraction.cpp jni/
	@sed -i "s|__PROJECT_VENDOR__|$(PROJECT_VENDOR)|" jni/ewolAndroidAbstraction.cpp
	@sed -i "s|__PROJECT_NAME__|$(PROJECT_NAME)|" jni/ewolAndroidAbstraction.cpp
	@sed -i "s|__PROJECT_PACKAGE__|$(PROJECT_PACKAGE)|" jni/ewolAndroidAbstraction.cpp
	
	@echo "    (ndk-build) build native code"
	cd $(PROJECT_NDK) ; NDK_PROJECT_PATH=$(PROJECT_PATH) NDK_MODULE_PATH=$(PROJECT_MODULE) ./ndk-build
	@echo "    (ant) build java code"
	PATH=$(PROJECT_SDK)/tools/:$(PROJECT_SDK)/platform-tools/:$(PATH) ant -Dsdk.dir=$(PROJECT_SDK) debug
	@echo "    (sh) Clear previous sources "
	@rm -rf src jni/ewolAndroidAbstraction.cpp

install: all
	@echo "------------------------------------------------------------------------"
	@echo ' INSTALL : ./bin/$(PROJECT_NAME)-debug.apk'
	@echo "------------------------------------------------------------------------"
	@# $(PROJECT_SDK)/platform-tools/adb kill-server
	@# install application
	sudo $(PROJECT_SDK)/platform-tools/adb  install -r ./bin/$(PROJECT_NAME)-debug.apk

clean:
	@echo "------------------------------------------------------------------------"
	@echo ' CLEANING : bin libs gen obj'
	@echo "------------------------------------------------------------------------"
	cd $(PROJECT_NDK) ; NDK_PROJECT_PATH=$(PROJECT_PATH) NDK_MODULE_PATH=$(PROJECT_MODULE) ./ndk-build clean

localclean:
	@echo "------------------------------------------------------------------------"
	@echo ' Remove : bin libs gen obj'
	@echo "------------------------------------------------------------------------"
	rm -rf bin libs gen obj
