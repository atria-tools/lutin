

PROJECT_PACKAGE=$(PROJECT_NAME)package

TARGET_OS = Android
TARGET_ARCH = ARM
TARGET_CROSS = $(PROJECT_NDK)/toolchains/arm-linux-androideabi-4.4.3/prebuilt/linux-x86/bin/arm-linux-androideabi-

ANDROID_BOARD_ID = 14
TARGET_GLOBAL_C_INCLUDES+=-I$(PROJECT_NDK)/platforms/android-$(ANDROID_BOARD_ID)/arch-arm/usr/include
TARGET_GLOBAL_LDLIBS_SHARED = --sysroot=$(PROJECT_NDK)/platforms/android-$(ANDROID_BOARD_ID)/arch-arm

#generic makefile
include $(EWOL_FOLDER)/Build/core/main.mk

FINAL_FOLDER_JAVA=$(TARGET_OUT_FINAL)
FINAL_FOLDER_JAVA_PROJECT=$(FINAL_FOLDER_JAVA)/src/com/$(PROJECT_VENDOR)/$(PROJECT_NAME)

FINAL_FILE_ABSTRACTION = $(FINAL_FOLDER_JAVA_PROJECT)/$(PROJECT_NAME).java

final :
	@rm -rf $(FINAL_FOLDER_JAVA)/
	@mkdir -p $(FINAL_FOLDER_JAVA_PROJECT)/
	
	@cp $(EWOL_FOLDER)/Java/PROJECT_NAME.java $(FINAL_FILE_ABSTRACTION)
	@sed -i "s|__PROJECT_VENDOR__|$(PROJECT_VENDOR)|" $(FINAL_FILE_ABSTRACTION)
	@sed -i "s|__PROJECT_NAME__|$(PROJECT_NAME)|" $(FINAL_FILE_ABSTRACTION)
	@sed -i "s|__PROJECT_PACKAGE__|$(PROJECT_PACKAGE)|" $(FINAL_FILE_ABSTRACTION)
	
	@echo "AndroidManifest.xml <== os-Android/AndroidManifest.xml"
	@cp os-Android/AndroidManifest.xml $(FINAL_FOLDER_JAVA)/
	@cp -r os-Android/res $(FINAL_FOLDER_JAVA)/res
	
	@echo ".apk/assets/ <== assets"
	@mkdir -p $(FINAL_FOLDER_JAVA)/data/assets/
	@cp -r $(EWOL_FOLDER)/share/* $(FINAL_FOLDER_JAVA)/data/assets/
	@cp -r share/* $(FINAL_FOLDER_JAVA)/data/assets/
	
	@echo ".apk/lib/armeabi/ <== *.so"
	@mkdir -p $(FINAL_FOLDER_JAVA)/data/lib/armeabi/
	@cp $(TARGET_OUT_STAGING)/usr/lib/$(PROJECT_PACKAGE).so $(FINAL_FOLDER_JAVA)/data/lib/armeabi/lib$(PROJECT_PACKAGE).so
	
	@# Doc :
	@# http://asantoso.wordpress.com/2009/09/15/how-to-build-android-application-package-apk-from-the-command-line-using-the-sdk-tools-continuously-integrated-using-cruisecontrol/
	
	@echo "R.java <== Resources files"
	@$(PROJECT_SDK)/platform-tools/aapt p -f \
	     -M $(FINAL_FOLDER_JAVA)/AndroidManifest.xml \
	     -F $(FINAL_FOLDER_JAVA)/resources.res \
	     -I $(PROJECT_SDK)/platforms/android-15/android.jar\
	     -S $(FINAL_FOLDER_JAVA)/res/ \
	     -J $(FINAL_FOLDER_JAVA)/src
	
	@mkdir -p $(FINAL_FOLDER_JAVA)/build/classes/
	@echo ".class <== .java"
	@# more information with : -Xlint
	@javac \
	    -d $(FINAL_FOLDER_JAVA)/build/classes \
	    -classpath $(PROJECT_SDK)/platforms/android-15/android.jar \
	    $(FINAL_FILE_ABSTRACTION) \
	    $(EWOL_FOLDER)/Java/src/org/ewol/interfaceJNI.java \
	    $(EWOL_FOLDER)/Java/src/org/ewol/interfaceOpenGL.java \
	    $(EWOL_FOLDER)/Java/src/org/ewol/interfaceSurfaceView.java \
	    $(EWOL_FOLDER)/Java/src/org/ewol/interfaceAudio.java \
	    $(FINAL_FOLDER_JAVA)/src/R.java
	
	@echo ".dex <== .class"
	@$(PROJECT_SDK)/platform-tools/dx \
	    --dex --no-strict \
	    --output=$(FINAL_FOLDER_JAVA)/build/$(PROJECT_PACKAGE).dex \
	    $(FINAL_FOLDER_JAVA)/build/classes/
	
	@echo ".apk <== .dex, assets, .so, res"
	@$(PROJECT_SDK)/tools/apkbuilder \
	    $(FINAL_FOLDER_JAVA)/build/$(PROJECT_PACKAGE)-unalligned.apk \
	    -u \
	    -z $(FINAL_FOLDER_JAVA)/resources.res \
	    -f $(FINAL_FOLDER_JAVA)/build/$(PROJECT_PACKAGE).dex \
	    -rf $(FINAL_FOLDER_JAVA)/data
	
	@# doc :
	@# http://developer.android.com/tools/publishing/app-signing.html
	
	@# keytool is situated in $(JAVA_HOME)/bin ...
	$(if $(wildcard ./$(PROJECT_NAME)-$(BUILD_DIRECTORY_MODE).jks),$(empty), \
		@echo "./$(PROJECT_NAME).jks <== dynamic key (NOTE : It might ask some question to generate the key for android)" ; \
		keytool -genkeypair -v \
		    -keystore ./$(PROJECT_NAME)-$(BUILD_DIRECTORY_MODE).jks \
		    -storepass Pass$(PROJECT_NAME) \
		    -alias alias$(PROJECT_NAME) \
		    -keypass PassK$(PROJECT_NAME) \
		    -keyalg RSA \
		    -validity 365 \
	)
	
	@# Question poser a ce moment, les automatiser ...
	@# Quels sont vos prénom et nom ?
	@# Edouard DUPIN
	@#   [Unknown] :  Quel est le nom de votre unité organisationnelle ?
	@# org
	@#   [Unknown] :  Quelle est le nom de votre organisation ?
	@# EWOL
	@#   [Unknown] :  Quel est le nom de votre ville de résidence ?
	@# Paris
	@#   [Unknown] :  Quel est le nom de votre état ou province ?
	@# France
	@#   [Unknown] :  Quel est le code de pays à deux lettres pour cette unité ?
	@# FR
	@#   [Unknown] :  Est-ce CN=Edouard DUPIN, OU=org, O=EWOL, L=Paris, ST=France, C=FR ?
	@# oui
	@#   [non] :  
	@# Génération d'une paire de clés RSA de 1 024 bits et d'un certificat autosigné (SHA1withRSA) d'une validité de 365 jours
	@# 	pour : CN=Edouard DUPIN, OU=org, O=EWOL, L=Paris, ST=France, C=FR
	
	@# keytool is situated in $(JAVA_HOME)/bin ...
	@echo "apk(Signed) <== apk"
	@#generate the pass file :
	@echo "Pass$(PROJECT_NAME)" > tmpPass.boo
	@echo "PassK$(PROJECT_NAME)" >> tmpPass.boo
	@# verbose mode : -verbose
	@jarsigner \
	    -sigalg MD5withRSA \
	    -digestalg SHA1 \
	    -keystore ./$(PROJECT_NAME)-$(BUILD_DIRECTORY_MODE).jks \
	    $(FINAL_FOLDER_JAVA)/build/$(PROJECT_PACKAGE)-unalligned.apk \
	    alias$(PROJECT_NAME) \
	    < tmpPass.boo
	
	@rm tmpPass.boo
	@echo "apk(aligned) <== apk"
	@# verbose mode : -v
	@zipalign 4 \
	    $(FINAL_FOLDER_JAVA)/build/$(PROJECT_PACKAGE)-unalligned.apk \
	    $(FINAL_FOLDER_JAVA)/$(PROJECT_PACKAGE).apk


FINAL_FOLDER_ANT=$(TARGET_OUT_FINAL)/ant
FINAL_FOLDER_ANT_PROJECT=$(FINAL_FOLDER_ANT)/src/com/$(PROJECT_VENDOR)/$(PROJECT_NAME)
FINAL_FILE_ANT_ABSTRACTION = $(FINAL_FOLDER_JAVA_PROJECT)/$(PROJECT_NAME).java


with_ant:
	@mkdir -p $(FINAL_FOLDER_ANT_PROJECT)/
	@cp $(EWOL_FOLDER)/Java/PROJECT_NAME.java $(FINAL_FILE_ANT_ABSTRACTION)
	@sed -i "s|__PROJECT_VENDOR__|$(PROJECT_VENDOR)|" $(FINAL_FILE_ANT_ABSTRACTION)
	@sed -i "s|__PROJECT_NAME__|$(PROJECT_NAME)|" $(FINAL_FILE_ANT_ABSTRACTION)
	@sed -i "s|__PROJECT_PACKAGE__|$(PROJECT_PACKAGE)|" $(FINAL_FILE_ANT_ABSTRACTION)
	@# copy the Ewol java files : 
	@mkdir -p $(FINAL_FOLDER_ANT)/src/org/ewol
	@cp $(EWOL_FOLDER)/Java/src/org/ewol/interfaceJNI.java $(FINAL_FOLDER_ANT)/src/org/ewol
	@cp $(EWOL_FOLDER)/Java/src/org/ewol/interfaceOpenGL.java $(FINAL_FOLDER_ANT)/src/org/ewol/
	@cp $(EWOL_FOLDER)/Java/src/org/ewol/interfaceSurfaceView.java $(FINAL_FOLDER_ANT)/src/org/ewol/
	@cp $(EWOL_FOLDER)/Java/src/org/ewol/interfaceAudio.java $(FINAL_FOLDER_ANT)/src/org/ewol/
	
	@# copy android specific data :
	@cp -r os-Android/* $(FINAL_FOLDER_ANT)/
	@# copy user data
	@mkdir -p $(FINAL_FOLDER_ANT)/assets/
	@cp -r share/* $(FINAL_FOLDER_ANT)/assets/
	@mkdir -p $(FINAL_FOLDER_ANT)/libs/armeabi/
	@# note : this change the lib name ...
	@cp $(TARGET_OUT_STAGING)/usr/lib/$(PROJECT_PACKAGE).so $(FINAL_FOLDER_ANT)/libs/armeabi/lib$(PROJECT_PACKAGE).so
	@echo  "    (ant) build java code"
	@cd $(FINAL_FOLDER_ANT) ; PATH=$(PROJECT_SDK)/tools/:$(PROJECT_SDK)/platform-tools/:$(PATH) ant -Dsdk.dir=$(PROJECT_SDK) $(BUILD_DIRECTORY_MODE)
	@# cp the release package in the final folder to facilitate the find
	@cp -f $(FINAL_FOLDER_ANT)/bin/$(PROJECT_NAME)-$(BUILD_DIRECTORY_MODE).apk $(FINAL_FOLDER_JAVA)/$(PROJECT_PACKAGE).apk



install: 
	@echo ------------------------------------------------------------------------
	@echo Install : $(TARGET_OUT_FINAL)/$(PROJECT_NAME)-$(BUILD_DIRECTORY_MODE).apk
	@echo ------------------------------------------------------------------------
	@# $(PROJECT_SDK)/platform-tools/adb kill-server
	@# install application
	sudo $(PROJECT_SDK)/platform-tools/adb install -r $(FINAL_FOLDER_JAVA)/$(PROJECT_PACKAGE)-$(BUILD_DIRECTORY_MODE).apk

uninstall:
	@echo ------------------------------------------------------------------------
	@echo UnInstall : $(ANDROID_BASIC_FOLDER)bin/$(PROJECT_NAME)-$(BUILD_DIRECTORY_MODE).apk
	@echo ------------------------------------------------------------------------
	@echo  ... TODO ...
	
