

PROJECT_PACKAGE=$(PROJECT_NAME)package

USER_PACKAGES += $(EWOL_FOLDER)/Sources/
TARGET_OS = Android
TARGET_ARCH = ARM
CROSS = $(PROJECT_NDK)/toolchains/arm-linux-androideabi-4.4.3/prebuilt/linux-x86/bin/arm-linux-androideabi-


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

ANDROID_BASIC_FOLDER=./out/$(TARGET_OS)/$(BUILD_DIRECTORY_MODE)/ant/
JAVA_FOLDER=$(ANDROID_BASIC_FOLDER)src/com/$(PROJECT_VENDOR)/$(PROJECT_NAME)
EWOL_JAVA_FOLDER=$(ANDROID_BASIC_FOLDER)src/org/ewol

java :
	@mkdir -p $(JAVA_FOLDER)/
	@mkdir -p $(EWOL_JAVA_FOLDER)/
	
	@cp $(EWOL_FOLDER)/Java/PROJECT_NAME.java $(JAVA_FOLDER)/$(PROJECT_NAME).java
	@sed -i "s|__PROJECT_VENDOR__|$(PROJECT_VENDOR)|" $(JAVA_FOLDER)/$(PROJECT_NAME).java
	@sed -i "s|__PROJECT_NAME__|$(PROJECT_NAME)|" $(JAVA_FOLDER)/$(PROJECT_NAME).java
	@sed -i "s|__PROJECT_PACKAGE__|$(PROJECT_PACKAGE)|" $(JAVA_FOLDER)/$(PROJECT_NAME).java
	@# copy the Ewol java files : 
	@cp $(EWOL_FOLDER)/Java/interfaceJNI.java $(EWOL_JAVA_FOLDER)/
	@cp $(EWOL_FOLDER)/Java/interfaceOpenGL.java $(EWOL_JAVA_FOLDER)/
	@cp $(EWOL_FOLDER)/Java/interfaceSurfaceView.java $(EWOL_JAVA_FOLDER)/
	@cp $(EWOL_FOLDER)/Java/interfaceAudio.java $(EWOL_JAVA_FOLDER)/
	
	@# copy android specific data :
	@cp -r Android/* $(ANDROID_BASIC_FOLDER)/
	@# copy user data
	@cp -r share $(ANDROID_BASIC_FOLDER)/assets
	@mkdir -p $(ANDROID_BASIC_FOLDER)libs/armeabi/
	@# note : this change the lib name ...
	@cp ./out/$(TARGET_OS)/$(BUILD_DIRECTORY_MODE)/obj/usr/lib/$(PROJECT_PACKAGE).so $(ANDROID_BASIC_FOLDER)libs/armeabi/lib$(PROJECT_PACKAGE).so
	@echo  "    (ant) build java code"
	@cd $(ANDROID_BASIC_FOLDER) ; PATH=$(PROJECT_SDK)/tools/:$(PROJECT_SDK)/platform-tools/:$(PATH) ant -Dsdk.dir=$(PROJECT_SDK) $(BUILD_DIRECTORY_MODE)


install:
	@echo "------------------------------------------------------------------------"
	@echo ' INSTALL : ./bin/$(PROJECT_NAME)-debug.apk'
	@echo "------------------------------------------------------------------------"
	@# $(PROJECT_SDK)/platform-tools/adb kill-server
	@# install application
	sudo $(PROJECT_SDK)/platform-tools/adb install -r $(ANDROID_BASIC_FOLDER)bin/$(PROJECT_NAME)-$(BUILD_DIRECTORY_MODE).apk

