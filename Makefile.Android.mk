

PROJECT_PACKAGE=$(PROJECT_NAME)package
JAVA_FOLDER=src/com/$(PROJECT_VENDOR)/$(PROJECT_NAME)
EWOL_JAVA_FOLDER=src/org/ewol


USER_PACKAGES += $(EWOL_FOLDER)/Sources/
TARGET_OS = Android
TARGET_ARCH = ARM
CROSS = $(PROJECT_NDK)/toolchains/arm-linux-androideabi-4.4.3/prebuilt/linux-x86/bin/arm-linux-androideabi-


$(info ------------------------------------------------------------------------)
$(info  Project name    : $(PROJECT_NAME))
$(info  Project Vendor  : $(PROJECT_VENDOR))
$(info  Build date      : $(BUILD_TIME) )
$(info  Tag             : $(PROJECT_VERSION_TAG) )
$(info ------------------------------------------------------------------------)

$(info     (sh) Create folder : $(JAVA_FOLDER)/ & $(EWOL_JAVA_FOLDER))
$(shell mkdir -p $(JAVA_FOLDER)/)
$(shell mkdir -p $(EWOL_JAVA_FOLDER)/)

$(info     (sh) copy the java Files & Replace __XXX__ element with project properties)
tmp=$(shell cp -v $(EWOL_FOLDER)/Java/PROJECT_NAME.java $(JAVA_FOLDER)/$(PROJECT_NAME).java)
tmp+=$(shell sed -i "s|__PROJECT_VENDOR__|$(PROJECT_VENDOR)|" $(JAVA_FOLDER)/$(PROJECT_NAME).java)
tmp+=$(shell sed -i "s|__PROJECT_NAME__|$(PROJECT_NAME)|" $(JAVA_FOLDER)/$(PROJECT_NAME).java)
tmp+=$(shell sed -i "s|__PROJECT_PACKAGE__|$(PROJECT_PACKAGE)|" $(JAVA_FOLDER)/$(PROJECT_NAME).java)
# copy the Ewol java files : 
tmp+=$(shell cp $(EWOL_FOLDER)/Java/interfaceJNI.java $(EWOL_JAVA_FOLDER)/)
tmp+=$(shell cp $(EWOL_FOLDER)/Java/interfaceOpenGL.java $(EWOL_JAVA_FOLDER)/)
tmp+=$(shell cp $(EWOL_FOLDER)/Java/interfaceSurfaceView.java $(EWOL_JAVA_FOLDER)/)
tmp+=$(shell cp $(EWOL_FOLDER)/Java/interfaceAudio.java $(EWOL_JAVA_FOLDER)/)
$(info $(tmp))

$(info     (sh) copy the cpp for jni File : $(EWOL_FOLDER)/Java/ewolAndroidAbstraction.cpp)
tmp=$(shell cp -v $(EWOL_FOLDER)/Java/ewolAndroidAbstraction.cpp jni/)
tmp+=$(shell sed -i "s|__PROJECT_VENDOR__|$(PROJECT_VENDOR)|" jni/ewolAndroidAbstraction.cpp)
tmp+=$(shell sed -i "s|__PROJECT_NAME__|$(PROJECT_NAME)|" jni/ewolAndroidAbstraction.cpp)
tmp+=$(shell sed -i "s|__PROJECT_PACKAGE__|$(PROJECT_PACKAGE)|" jni/ewolAndroidAbstraction.cpp)
$(info $(tmp))

TARGET_GLOBAL_C_INCLUDES=-I$(PROJECT_NDK)/sources/cxx-stl/stlport/stlport
TARGET_GLOBAL_C_INCLUDES+=-I$(PROJECT_NDK)/sources/cxx-stl//gabi++/include
TARGET_GLOBAL_C_INCLUDES+=-I$(PROJECT_NDK)/platforms/android-14/arch-arm/usr/include


$(info ------------------------------------------------------------------------)
include $(EWOL_FOLDER)/Build/coreLinux/main.mk

$(info "    (ant) build java code")
PATH:=$(PROJECT_SDK)/tools/:$(PROJECT_SDK)/platform-tools/:$(PATH) ant -Dsdk.dir=$(PROJECT_SDK) debug)
$(info "    (sh) Clear previous sources ")
#$(shell rm -rf src jni/ewolAndroidAbstraction.cpp)

TARGET_GLOBAL_LDLIBS_SHARED = -shared --sysroot=$(PROJECT_NDK)/platforms/android-14/arch-arm \
                        $(PROJECT_NDK)/platforms/android-14/arch-arm/usr/lib/libstdc++.a \
                        $(PROJECT_NDK)/sources/cxx-stl/gnu-libstdc++/libs/armeabi/libsupc++.a \
                        -lstdc++



#install: all
#	@echo "------------------------------------------------------------------------"
#	@echo ' INSTALL : ./bin/$(PROJECT_NAME)-debug.apk'
#	@echo "------------------------------------------------------------------------"
#	@# $(PROJECT_SDK)/platform-tools/adb kill-server
#	@# install application
#	sudo $(PROJECT_SDK)/platform-tools/adb  install -r ./bin/$(PROJECT_NAME)-debug.apk
#
#clean:
#	@echo "------------------------------------------------------------------------"
#	@echo ' CLEANING : bin libs gen obj'
#	@echo "------------------------------------------------------------------------"
#	cd $(PROJECT_NDK) ; NDK_PROJECT_PATH=$(PROJECT_PATH) NDK_MODULE_PATH=$(PROJECT_MODULE) ./ndk-build clean
#
#localclean:
#	@echo "------------------------------------------------------------------------"
#	@echo ' Remove : bin libs gen obj'
#	@echo "------------------------------------------------------------------------"
#	rm -rf bin libs gen obj
