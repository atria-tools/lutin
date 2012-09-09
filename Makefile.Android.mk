

PROJECT_PACKAGE=$(PROJECT_NAME)package

TARGET_OS = Android
TARGET_ARCH = ARM
TARGET_CROSS = $(PROJECT_NDK)/toolchains/arm-linux-androideabi-4.4.3/prebuilt/linux-x86/bin/arm-linux-androideabi-

ANDROID_BOARD_ID = 14
TARGET_GLOBAL_C_INCLUDES+=-I$(PROJECT_NDK)/platforms/android-$(ANDROID_BOARD_ID)/arch-arm/usr/include
TARGET_GLOBAL_LDLIBS_SHARED = --sysroot=$(PROJECT_NDK)/platforms/android-$(ANDROID_BOARD_ID)/arch-arm

#generic makefile
include $(EWOL_FOLDER)/Build/core/main.mk


#FINAL_FOLDER_ANT=$(TARGET_OUT_FINAL)/ant
#FINAL_FOLDER_JAVA_PROJECT=$(FINAL_FOLDER_ANT)/src/com/$(PROJECT_VENDOR)/$(PROJECT_NAME)
#FINAL_FOLDER_JAVA_EWOL=$(FINAL_FOLDER_ANT)/src/org/ewol

FINAL_FOLDER_JAVA=$(TARGET_OUT_FINAL)/java
FINAL_FOLDER_JAVA_PROJECT=$(FINAL_FOLDER_JAVA)/src/com/$(PROJECT_VENDOR)/$(PROJECT_NAME)
FINAL_FOLDER_JAVA_EWOL=$(FINAL_FOLDER_JAVA)/src/org/ewol

FINAL_FILE_ABSTRACTION = $(FINAL_FOLDER_JAVA_PROJECT)/$(PROJECT_NAME).java

final :
	@rm -rf $(FINAL_FOLDER_JAVA)/
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
	
	@#Rmove the R.java file as will be created by aapt
	@#rm -rf $(FINAL_FOLDER_JAVA)/src/com/simple/search/R.java 
	@# copy android specific data :
	@cp os-Android/AndroidManifest.xml $(FINAL_FOLDER_JAVA)/
	@cp -r os-Android/res $(FINAL_FOLDER_JAVA)/res
	@# copy user data
	@mkdir -p $(FINAL_FOLDER_JAVA)/assets/
	@# remove this when move in the EWOL lib ...
	@cp -r $(EWOL_FOLDER)/share/* $(FINAL_FOLDER_JAVA)/assets/
	@#copy use data
	@cp -r share/* $(FINAL_FOLDER_JAVA)/assets/
	@mkdir -p $(FINAL_FOLDER_JAVA)/libs/armeabi/
	@# note : this change the lib name ...
	@cp $(TARGET_OUT_STAGING)/usr/lib/$(PROJECT_PACKAGE).so $(FINAL_FOLDER_JAVA)/libs/armeabi/lib$(PROJECT_PACKAGE).so
	@echo  "    (...) "
	mkdir -p $(FINAL_FOLDER_JAVA)/gen
	@echo "out <== Create the R.java and resource file"
	@#-v to have information ...
	@aapt p -f \
	     -M $(FINAL_FOLDER_JAVA)/AndroidManifest.xml \
	     -F $(FINAL_FOLDER_JAVA)/resources.res \
	     -I $(PROJECT_SDK)/platforms/android-15/android.jar\
	     -S $(FINAL_FOLDER_JAVA)/res/ \
	     -J $(FINAL_FOLDER_JAVA)/gen
	
	@mkdir -p $(FINAL_FOLDER_JAVA)/libs/
	@mkdir -p $(FINAL_FOLDER_JAVA)/build/classes/
	@echo "java <== input"
	@#Now compile - note the use of a seperate lib (in non-dex format!)
	@#CLASSPATH=$(PROJECT_SDK)/sources/android-15/java
	@#PATH=$(PROJECT_SDK)/tools/:$(PROJECT_SDK)/platform-tools/:$(PATH)
	@#JAVA_HOME=$(PROJECT_SDK)/sources/android-15/java
	@# more information with : -Xlint
	@# more more information : -verbose
	@javac \
	    -d $(FINAL_FOLDER_JAVA)/build/classes \
	    -classpath $(PROJECT_SDK)/platforms/android-15/android.jar \
	    $(FINAL_FILE_ABSTRACTION) \
	    $(FINAL_FOLDER_JAVA_EWOL)/interfaceJNI.java \
	    $(FINAL_FOLDER_JAVA_EWOL)/interfaceOpenGL.java \
	    $(FINAL_FOLDER_JAVA_EWOL)/interfaceSurfaceView.java \
	    $(FINAL_FOLDER_JAVA_EWOL)/interfaceAudio.java \
	    $(FINAL_FOLDER_JAVA)/gen/R.java
	
	@echo "dex <== input classes : "
	@$(PROJECT_SDK)/platform-tools/dx \
	    --dex --verbose --no-strict \
	    --output=$(FINAL_FOLDER_JAVA)/build/out.dex \
	    $(FINAL_FOLDER_JAVA)/build/classes/
	
	@echo "apk <== dex file"
	@$(PROJECT_SDK)/tools/apkbuilder \
	    $(FINAL_FOLDER_JAVA)/out.apk \
	    -v -u \
	    -z $(FINAL_FOLDER_JAVA)/resources.res \
	    -f $(FINAL_FOLDER_JAVA)/build/out.dex 
	
	@echo "apk(Signed) <== apk"
	@#$(PROJECT_SDK)/tools/signer $(FINAL_FOLDER_JAVA)/out.apk $(FINAL_FOLDER_JAVA)/outSigned.apk
	@#jarsigner $(FINAL_FOLDER_JAVA)/out.apk $(TARGET_OUT_FINAL)/$(PROJECT_NAME)-$(BUILD_DIRECTORY_MODE).apk

plop:
	@# copy android specific data :
	@#cp -r os-Android/* $(FINAL_FOLDER_ANT)/
	@# copy user data
	@#mkdir -p $(FINAL_FOLDER_ANT)/assets/
	@#cp -r share/* $(FINAL_FOLDER_ANT)/assets/
	@#mkdir -p $(FINAL_FOLDER_ANT)/libs/armeabi/
	@# note : this change the lib name ...
	@#cp $(TARGET_OUT_STAGING)/usr/lib/$(PROJECT_PACKAGE).so $(FINAL_FOLDER_ANT)/libs/armeabi/lib$(PROJECT_PACKAGE).so
	@#echo  "    (ant) build java code"
	@#cd $(FINAL_FOLDER_ANT) ; PATH=$(PROJECT_SDK)/tools/:$(PROJECT_SDK)/platform-tools/:$(PATH) ant -Dsdk.dir=$(PROJECT_SDK) $(BUILD_DIRECTORY_MODE)
	@# cp the release package in the final folder to facilitate the find
	@#cp -f $(FINAL_FOLDER_ANT)/bin/$(PROJECT_NAME)-$(BUILD_DIRECTORY_MODE).apk $(TARGET_OUT_FINAL)/$(PROJECT_NAME)-$(BUILD_DIRECTORY_MODE).apk
	


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
	
