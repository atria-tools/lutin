

PROJECT_PACKAGE=$(PROJECT_NAME)package

TARGET_OS = Android
TARGET_ARCH = ARM
TARGET_CROSS = $(PROJECT_NDK)/toolchains/arm-linux-androideabi-4.4.3/prebuilt/linux-x86/bin/arm-linux-androideabi-


#Add the basic element abstraction of ewol lib
$(shell cp $(EWOL_FOLDER)/Java/ewolAndroidAbstraction.cpp Sources/)
$(shell sed -i "s|__PROJECT_VENDOR__|$(PROJECT_VENDOR)|" Sources/ewolAndroidAbstraction.cpp)
$(shell sed -i "s|__PROJECT_NAME__|$(PROJECT_NAME)|" Sources/ewolAndroidAbstraction.cpp)
$(shell sed -i "s|__PROJECT_PACKAGE__|$(PROJECT_PACKAGE)|" Sources/ewolAndroidAbstraction.cpp)


ANDROID_BOARD_ID = 14
TARGET_GLOBAL_C_INCLUDES+=-I$(PROJECT_NDK)/platforms/android-$(ANDROID_BOARD_ID)/arch-arm/usr/include
TARGET_GLOBAL_LDLIBS_SHARED = --sysroot=$(PROJECT_NDK)/platforms/android-$(ANDROID_BOARD_ID)/arch-arm

#generic makefile
include $(EWOL_FOLDER)/Build/core/main.mk



FINAL_FOLDER_ANT=$(TARGET_OUT_FINAL)/ant
FINAL_FOLDER_JAVA_PROJECT=$(FINAL_FOLDER_ANT)/src/com/$(PROJECT_VENDOR)/$(PROJECT_NAME)
FINAL_FOLDER_JAVA_EWOL=$(FINAL_FOLDER_ANT)/src/org/ewol

FINAL_FILE_ABSTRACTION = $(FINAL_FOLDER_JAVA_PROJECT)/$(PROJECT_NAME).java

final : all
	@mkdir -p $(FINAL_FOLDER_JAVA_PROJECT)/
	@mkdir -p $(FINAL_FOLDER_JAVA_EWOL)/
	
	@cp $(EWOL_FOLDER)/Java/PROJECT_NAME.java $(FINAL_FILE_ABSTRACTION)
	@sed -i "s|__PROJECT_VENDOR__|$(PROJECT_VENDOR)|" $(FINAL_FILE_ABSTRACTION)
	@sed -i "s|__PROJECT_NAME__|$(PROJECT_NAME)|" $(FINAL_FILE_ABSTRACTION)
	@sed -i "s|__PROJECT_PACKAGE__|$(PROJECT_PACKAGE)|" $(FINAL_FILE_ABSTRACTION)
	@# copy the Ewol java files : 
	@cp $(EWOL_FOLDER)/Java/interfaceJNI.java $(FINAL_FOLDER_JAVA_EWOL)/
	@cp $(EWOL_FOLDER)/Java/interfaceOpenGL.java $(FINAL_FOLDER_JAVA_EWOL)/
	@cp $(EWOL_FOLDER)/Java/interfaceSurfaceView.java $(FINAL_FOLDER_JAVA_EWOL)/
	@cp $(EWOL_FOLDER)/Java/interfaceAudio.java $(FINAL_FOLDER_JAVA_EWOL)/
	
	@# copy android specific data :
	@cp -r os-Android/* $(FINAL_FOLDER_ANT)/
	@# copy user data
	@cp -r share $(FINAL_FOLDER_ANT)/assets
	@mkdir -p $(FINAL_FOLDER_ANT)/libs/armeabi/
	@# note : this change the lib name ...
	@cp $(TARGET_OUT_STAGING)/usr/lib/$(PROJECT_PACKAGE).so $(FINAL_FOLDER_ANT)/libs/armeabi/lib$(PROJECT_PACKAGE).so
	@echo  "    (ant) build java code"
	@cd $(FINAL_FOLDER_ANT) ; PATH=$(PROJECT_SDK)/tools/:$(PROJECT_SDK)/platform-tools/:$(PATH) ant -Dsdk.dir=$(PROJECT_SDK) $(BUILD_DIRECTORY_MODE)
	@# cp the release package in the final folder to facilitate the find
	@cp -f $(FINAL_FOLDER_ANT)/bin/$(PROJECT_NAME)-$(BUILD_DIRECTORY_MODE).apk $(TARGET_OUT_FINAL)/$(PROJECT_NAME)-$(BUILD_DIRECTORY_MODE).apk


install: final
	@echo ------------------------------------------------------------------------
	@echo Install : $(TARGET_OUT_FINAL)/$(PROJECT_NAME)-$(BUILD_DIRECTORY_MODE).apk
	@echo ------------------------------------------------------------------------
	@# $(PROJECT_SDK)/platform-tools/adb kill-server
	@# install application
	sudo $(PROJECT_SDK)/platform-tools/adb install -r $(TARGET_OUT_FINAL)/$(PROJECT_NAME)-$(BUILD_DIRECTORY_MODE).apk

uninstall:
	@echo ------------------------------------------------------------------------
	@echo UnInstall : $(ANDROID_BASIC_FOLDER)bin/$(PROJECT_NAME)-$(BUILD_DIRECTORY_MODE).apk
	@echo ------------------------------------------------------------------------
	@echo  ... TODO ...
	
