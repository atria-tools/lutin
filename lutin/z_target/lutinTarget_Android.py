#!/usr/bin/python
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##


from lutin import debug
from lutin import target
from lutin import tools
from lutin import image
from lutin import multiprocess
from lutin import host
import os
import sys

class Target(target.Target):
	def __init__(self, config):
		#processor type selection (auto/arm/ppc/x86)
		if config["arch"] == "auto":
			config["arch"] = "arm"
		#bus size selection (auto/32/64)
		if config["bus-size"] == "auto":
			config["bus-size"] = "32"
		
		arch = ""#"ARMv7"
		target.Target.__init__(self, "Android", config, arch)
		
		self.folder_ndk = os.getenv('PROJECT_NDK', "AUTO")
		self.folder_sdk = os.getenv('PROJECT_SDK', "AUTO")
		# auto search NDK
		if self.folder_ndk == "AUTO":
			for folder in os.listdir("."):
				if os.path.isdir(folder)==True:
					if folder=="android":
						self.folder_ndk = folder + "/ndk"
			if self.folder_ndk == "AUTO":
				self.folder_ndk = tools.get_run_folder() + "/../android/ndk"
		# auto search SDK
		if self.folder_sdk == "AUTO":
			for folder in os.listdir("."):
				if os.path.isdir(folder)==True:
					if folder=="android":
						self.folder_sdk = folder + "/sdk"
			if self.folder_sdk == "AUTO":
				self.folder_sdk = tools.get_run_folder() + "/../android/sdk"
		
		if not os.path.isdir(self.folder_ndk):
			debug.error("NDK path not set !!! set env : PROJECT_NDK on the NDK path")
		if not os.path.isdir(self.folder_sdk):
			debug.error("SDK path not set !!! set env : PROJECT_SDK on the SDK path")
		
		
		tmpOsVal = "64"
		gccVersion = "4.9"
		if host.BUS_SIZE==64:
			tmpOsVal = "_64"
		if self.config["compilator"] == "clang":
			self.set_cross_base(self.folder_ndk + "/toolchains/llvm-3.3/prebuilt/linux-x86_64/bin/")
		else:
			baseFolderArm = self.folder_ndk + "/toolchains/arm-linux-androideabi-" + gccVersion + "/prebuilt/linux-x86" + tmpOsVal + "/bin/"
			baseFolderMips = self.folder_ndk + "/toolchains/mipsel-linux-android-" + gccVersion + "/prebuilt/linux-x86" + tmpOsVal + "/bin/"
			baseFolderX86 = self.folder_ndk + "/toolchains/x86-" + gccVersion + "/prebuilt/linux-x86" + tmpOsVal + "/bin/"
			self.set_cross_base(baseFolderArm + "arm-linux-androideabi-")
			if not os.path.isdir(baseFolderArm):
				debug.error("Gcc Arm path does not exist !!!")
			if not os.path.isdir(baseFolderMips):
				debug.info("Gcc Mips path does not exist !!!")
			if not os.path.isdir(baseFolderX86):
				debug.info("Gcc x86 path does not exist !!!")
		
		arch = "ARMv7"
		# for gcc :
		
		# for clang :
		
		
		self.folder_bin="/mustNotCreateBinary"
		self.folder_lib="/data/lib/armeabi"
		self.folder_data="/data/assets"
		self.folder_doc="/doc"
		self.suffix_package='.pkg'
		
		# board id at 14 is for android 4.0 and more ...
		self.boardId = 14
		if arch == "ARMv5" or arch == "ARMv7":
			self.global_include_cc.append("-I" + self.folder_ndk +"/platforms/android-" + str(self.boardId) + "/arch-arm/usr/include/")
		elif arch == "mips":
			self.global_include_cc.append("-I" + self.folder_ndk +"/platforms/android-" + str(self.boardId) + "/arch-mips/usr/include/")
		elif arch == "x86":
			self.global_include_cc.append("-I" + self.folder_ndk +"/platforms/android-" + str(self.boardId) + "/arch-x86/usr/include/")
		
		if True:
			if self.config["compilator"] == "clang":
				self.global_include_cc.append("-I" + self.folder_ndk +"/sources/cxx-stl/llvm-libc++/libcxx/include/")
				if arch == "ARMv5":
					stdCppBasePath = self.folder_ndk +"/sources/cxx-stl/llvm-libc++/libcxx/libs/armeabi/"
					self.global_include_cc.append("-I" + stdCppBasePath + "include/")
					self.global_flags_ld.append(         stdCppBasePath + "libc++_static.a")
				elif arch == "ARMv7":
					stdCppBasePath = self.folder_ndk +"/sources/cxx-stl/llvm-libc++/libcxx/libs/armeabi-v7a/"
					self.global_include_cc.append("-I" + stdCppBasePath + "include/")
					self.global_flags_ld.append(         stdCppBasePath + "libc++_static.a")
				elif arch == "mips":
					stdCppBasePath = self.folder_ndk +"/sources/cxx-stl/llvm-libc++/libcxx/libs/mips/"
					self.global_include_cc.append("-I" + stdCppBasePath + "include/")
					self.global_flags_ld.append(         stdCppBasePath + "libc++_static.a")
				elif arch == "x86":
					stdCppBasePath = self.folder_ndk +"/sources/cxx-stl/llvm-libc++/libcxx/libs/x86/"
					self.global_include_cc.append("-I" + stdCppBasePath + "include/")
					self.global_flags_ld.append(         stdCppBasePath + "libc++_static.a")
			else:
				self.global_include_cc.append("-I" + self.folder_ndk +"/sources/cxx-stl/gnu-libstdc++/" + gccVersion + "/include/")
				if arch == "ARMv5":
					stdCppBasePath = self.folder_ndk +"/sources/cxx-stl/gnu-libstdc++/" + gccVersion + "/libs/armeabi/"
					self.global_include_cc.append("-I" + stdCppBasePath + "include/")
					self.global_flags_ld.append(         stdCppBasePath + "thumb/libgnustl_static.a")
					self.global_flags_ld.append(         stdCppBasePath + "thumb/libsupc++.a")
				elif arch == "ARMv7":
					stdCppBasePath = self.folder_ndk +"/sources/cxx-stl/gnu-libstdc++/" + gccVersion + "/libs/armeabi-v7a/"
					self.global_include_cc.append("-I" + stdCppBasePath + "include/")
					self.global_flags_ld.append(         stdCppBasePath + "thumb/libgnustl_static.a")
					self.global_flags_ld.append(         stdCppBasePath + "thumb/libsupc++.a")
				elif arch == "mips":
					stdCppBasePath = self.folder_ndk +"/sources/cxx-stl/gnu-libstdc++/" + gccVersion + "/libs/mips/"
					self.global_include_cc.append("-I" + stdCppBasePath + "include/")
					self.global_flags_ld.append(         stdCppBasePath + "libgnustl_static.a")
					self.global_flags_ld.append(         stdCppBasePath + "libsupc++.a")
				elif arch == "x86":
					stdCppBasePath = self.folder_ndk +"/sources/cxx-stl/gnu-libstdc++/" + gccVersion + "/libs/x86/"
					self.global_include_cc.append("-I" + stdCppBasePath + "include/")
					self.global_flags_ld.append(         stdCppBasePath + "libgnustl_static.a")
					self.global_flags_ld.append(         stdCppBasePath + "libsupc++.a")
		else :
			self.global_include_cc.append("-I" + self.folder_ndk +"/sources/cxx-stl/system/include/")
			self.global_include_cc.append("-I" + self.folder_ndk +"/sources/cxx-stl/stlport/stlport/")
			self.global_flags_ld.append(self.folder_ndk +"/platforms/android-" + str(self.boardId) + "/arch-arm/usr/lib/libstdc++.a")
		
		self.global_sysroot = "--sysroot=" + self.folder_ndk +"/platforms/android-" + str(self.boardId) + "/arch-arm"
		
		self.global_flags_cc.append("-D__ARM_ARCH_5__")
		self.global_flags_cc.append("-D__ARM_ARCH_5T__")
		self.global_flags_cc.append("-D__ARM_ARCH_5E__")
		self.global_flags_cc.append("-D__ARM_ARCH_5TE__")
		if self.arch == "ARM":
			# -----------------------
			# -- arm V5 :
			# -----------------------
			self.global_flags_cc.append("-march=armv5te")
			self.global_flags_cc.append("-msoft-float")
		else:
			# -----------------------
			# -- arm V7 (Neon) :
			# -----------------------
			self.global_flags_cc.append("-mfpu=neon")
			self.global_flags_cc.append("-mfloat-abi=softfp")
			self.global_flags_ld.append("-mfpu=neon")
			self.global_flags_ld.append("-mfloat-abi=softfp")
			self.global_flags_cc.append("-D__ARM_ARCH_7__")
			self.global_flags_cc.append("-D__ARM_NEON__")
		
		# the -mthumb must be set for all the android produc, some ot the not work coretly without this one ... (all android code is generated with this flags)
		self.global_flags_cc.append("-mthumb")
		# -----------------------
		# -- Common flags :
		# -----------------------
		self.global_flags_cc.append("-fpic")
		self.global_flags_cc.append("-ffunction-sections")
		self.global_flags_cc.append("-funwind-tables")
		self.global_flags_cc.append("-fstack-protector")
		self.global_flags_cc.append("-Wno-psabi")
		self.global_flags_cc.append("-mtune=xscale")
		self.global_flags_cc.append("-fexceptions")
		##self.global_flags_cc.append("-fno-exceptions")
		self.global_flags_cc.append("-fomit-frame-pointer")
		self.global_flags_cc.append("-fno-strict-aliasing")
		
		self.global_flags_xx.append("-frtti")
		self.global_flags_xx.append("-Wa,--noexecstack")
		
		
	
	def check_right_package(self, pkgProperties, value):
		for val in pkgProperties["RIGHT"]:
			if value == val:
				return True
		return False
	
	def get_staging_folder_data(self, binaryName):
		return self.get_staging_folder(binaryName) + self.folder_data
	
	def make_package(self, pkgName, pkgProperties, basePkgPath):
		# http://alp.developpez.com/tutoriels/debian/creer-paquet/
		debug.debug("------------------------------------------------------------------------")
		debug.info("Generate package '" + pkgName + "'")
		debug.debug("------------------------------------------------------------------------")
		pkgNameApplicationName = pkgName
		if self.config["mode"] == "debug":
			pkgNameApplicationName += "debug"
		# FINAL_FOLDER_JAVA_PROJECT
		self.folder_javaProject=   self.get_staging_folder(pkgName) \
		                         + "/src/" \
		                         + pkgProperties["COMPAGNY_TYPE"] \
		                         + "/" + pkgProperties["COMPAGNY_NAME2"] \
		                         + "/" + pkgNameApplicationName + "/"
		#FINAL_FILE_ABSTRACTION
		self.file_finalAbstraction = self.folder_javaProject + "/" + pkgNameApplicationName + ".java"
		
		compleatePackageName = pkgProperties["COMPAGNY_TYPE"]+"."+pkgProperties["COMPAGNY_NAME2"]+"." + pkgNameApplicationName
		
		if "ADMOD_ID" in pkgProperties:
			pkgProperties["RIGHT"].append("INTERNET")
			pkgProperties["RIGHT"].append("ACCESS_NETWORK_STATE")
		
		
		debug.print_element("pkg", "absractionFile", "<==", "dynamic file")
		# Create folder :
		tools.create_directory_of_file(self.file_finalAbstraction)
		# Create file :
		# java ==> done by ewol wrapper ... (and compiled in the normal compilation system ==> must be find in the dependency list of jar ...
		
		tools.create_directory_of_file(self.get_staging_folder(pkgName) + "/res/drawable/icon.png");
		if     "ICON" in pkgProperties.keys() \
		   and pkgProperties["ICON"] != "":
			image.resize(pkgProperties["ICON"], self.get_staging_folder(pkgName) + "/res/drawable/icon.png", 256, 256)
		else:
			# to be sure that we have all time a resource ...
			tmpFile = open(self.get_staging_folder(pkgName) + "/res/drawable/plop.txt", 'w')
			tmpFile.write('plop\n')
			tmpFile.flush()
			tmpFile.close()
		
		if pkgProperties["ANDROID_MANIFEST"]!="":
			debug.print_element("pkg", "AndroidManifest.xml", "<==", pkgProperties["ANDROID_MANIFEST"])
			tools.copy_file(pkgProperties["ANDROID_MANIFEST"], self.get_staging_folder(pkgName) + "/AndroidManifest.xml", force=True)
		else:
			debug.error("missing parameter 'ANDROID_MANIFEST' in the properties ... ")
		
		#add properties on wallpaper : 
		# myModule.pkg_add("ANDROID_WALLPAPER_PROPERTIES", ["list", key, title, summary, [["key","value display"],["key2","value display 2"]])
		# myModule.pkg_add("ANDROID_WALLPAPER_PROPERTIES", ["list", "testpattern", "Select test pattern", "Choose which test pattern to display", [["key","value display"],["key2","value display 2"]]])
		# myModule.pkg_add("ANDROID_WALLPAPER_PROPERTIES", ["bool", key, title, summary, ["enable string", "disable String"])
		# myModule.pkg_add("ANDROID_WALLPAPER_PROPERTIES", ["bool", "movement", "Motion", "Apply movement to test pattern", ["Moving test pattern", "Still test pattern"]
		#copy needed resources :
		for res_source, res_dest in pkgProperties["ANDROID_RESOURCES"]:
			if res_source == "":
				continue
			tools.copy_file(res_source , self.get_staging_folder(pkgName) + "/res/" + res_dest + "/" + os.path.basename(res_source), force=True)
		
		
		# Doc :
		# http://asantoso.wordpress.com/2009/09/15/how-to-build-android-application-package-apk-from-the-command-line-using-the-sdk-tools-continuously-integrated-using-cruisecontrol/
		debug.print_element("pkg", "R.java", "<==", "Resources files")
		tools.create_directory_of_file(self.get_staging_folder(pkgName) + "/src/noFile")
		androidToolPath = self.folder_sdk + "/build-tools/"
		# find android tool version
		dirnames = tools.get_list_sub_folder(androidToolPath)
		if len(dirnames) != 1:
			debug.error("an error occured when getting the tools for android")
		androidToolPath += dirnames[0] + "/"
		
		adModResouceFolder = ""
		if "ADMOD_ID" in pkgProperties:
			adModResouceFolder = " -S " + self.folder_sdk + "/extras/google/google_play_services/libproject/google-play-services_lib/res/ "
		cmdLine = androidToolPath + "aapt p -f " \
		          + "-M " + self.get_staging_folder(pkgName) + "/AndroidManifest.xml " \
		          + "-F " + self.get_staging_folder(pkgName) + "/resources.res " \
		          + "-I " + self.folder_sdk + "/platforms/android-" + str(self.boardId) + "/android.jar "\
		          + "-S " + self.get_staging_folder(pkgName) + "/res/ " \
		          + adModResouceFolder \
		          + "-J " + self.get_staging_folder(pkgName) + "/src/ "
		multiprocess.run_command(cmdLine)
		#aapt  package -f -M ${manifest.file} -F ${packaged.resource.file} -I ${path.to.android-jar.library} 
		#      -S ${android-resource-directory} [-m -J ${folder.to.output.the.R.java}]
		
		tools.create_directory_of_file(self.get_staging_folder(pkgName) + "/build/classes/noFile")
		debug.print_element("pkg", "*.class", "<==", "*.java")
		# more information with : -Xlint
		#          + self.file_finalAbstraction + " "\ # this generate ex: out/Android/debug/staging/tethys/src/com/edouarddupin/tethys/edn.java
		
		#generate android java files:
		filesString=""
		for element in pkgProperties["ANDROID_JAVA_FILES"]:
			if element=="DEFAULT":
				# this is deprecated ...
			else:
				filesString += element + " "
		
		if "ADMOD_ID" in pkgProperties:
			filesString += self.folder_sdk + "/extras/google/google_play_services/libproject/google-play-services_lib/src/android/UnusedStub.java "
			
		if len(pkgProperties["ANDROID_WALLPAPER_PROPERTIES"])!=0:
			filesString += self.folder_javaProject + pkgNameApplicationName + "Settings.java "
		
		adModJarFile = ""
		if "ADMOD_ID" in pkgProperties:
			adModJarFile = ":" + self.folder_sdk + "/extras/google/google_play_services/libproject/google-play-services_lib/libs/google-play-services.jar"
		
		cmdLine = "javac " \
		          + "-d " + self.get_staging_folder(pkgName) + "/build/classes " \
		          + "-classpath " + self.folder_sdk + "/platforms/android-" + str(self.boardId) + "/android.jar" \
		          + adModJarFile + " " \
		          + filesString \
		          + self.file_finalAbstraction + " "  \
		          + self.get_staging_folder(pkgName) + "/src/R.java "
		multiprocess.run_command(cmdLine)
		
		debug.print_element("pkg", ".dex", "<==", "*.class")
		cmdLine = androidToolPath + "dx " \
		          + "--dex --no-strict " \
		          + "--output=" + self.get_staging_folder(pkgName) + "/build/" + pkgNameApplicationName + ".dex " \
		          + self.get_staging_folder(pkgName) + "/build/classes/ "
		
		if "ADMOD_ID" in pkgProperties:
			cmdLine += self.folder_sdk + "/extras/google/google_play_services/libproject/google-play-services_lib/libs/google-play-services.jar "
		
		multiprocess.run_command(cmdLine)
		
		debug.print_element("pkg", ".apk", "<==", ".dex, assets, .so, res")
		#builderDebug="-agentlib:jdwp=transport=dt_socket,server=y,address=8050,suspend=y "
		builderDebug=""
		# note : set -u not signed application...
		#+ ":" + self.folder_sdk + "/extras/google/google_play_services/libproject/google-play-services_lib/libs/google-play-services.jar "
		cmdLine =   "java -Xmx128M " \
		          + " -classpath " + self.folder_sdk + "/tools/lib/sdklib.jar " \
		          + builderDebug \
		          + " com.android.sdklib.build.ApkBuilderMain " \
		          + self.get_staging_folder(pkgName) + "/build/" + pkgNameApplicationName + "-unalligned.apk " \
		          + " -u " \
		          + " -z " + self.get_staging_folder(pkgName) + "/resources.res " \
		          + " -f " + self.get_staging_folder(pkgName) + "/build/" + pkgNameApplicationName + ".dex " \
		          + " -rf " + self.get_staging_folder(pkgName) + "/data "
		multiprocess.run_command(cmdLine)
		
		# doc :
		# http://developer.android.com/tools/publishing/app-signing.html
		# Create a key for signing your application:
		# keytool -genkeypair -v -keystore AndroidKey.jks -storepass Pass__AndroidDebugKey -alias alias__AndroidDebugKey -keypass PassKey__AndroidDebugKey -keyalg RSA -validity 36500
		if self.config["mode"] == "debug":
			debug.print_element("pkg", ".apk(signed debug)", "<==", ".apk (not signed)")
			# verbose mode : 
			#debugOption = "-verbose -certs "
			debugOption = ""
			cmdLine = "jarsigner " \
			    + debugOption \
			    + "-keystore " + tools.get_current_path(__file__) + "/AndroidDebugKey.jks " \
			    + " -sigalg SHA1withRSA -digestalg SHA1 " \
			    + " -storepass Pass__AndroidDebugKey " \
			    + " -keypass PassKey__AndroidDebugKey " \
			    + self.get_staging_folder(pkgName) + "/build/" + pkgNameApplicationName + "-unalligned.apk " \
			    + " alias__AndroidDebugKey"
			multiprocess.run_command(cmdLine)
			tmpFile = open("tmpPass.boo", 'w')
			tmpFile.write("\n")
			tmpFile.flush()
			tmpFile.close()
		else:
			print("On release mode we need the file :  and key an pasword to sign the application ...")
			debug.print_element("pkg", ".apk(signed debug)", "<==", ".apk (not signed)")
			cmdLine = "jarsigner " \
			    + " -keystore " + basePkgPath + "/AndroidKey.jks " \
			    + " -sigalg SHA1withRSA -digestalg SHA1 " \
			    + self.get_staging_folder(pkgName) + "/build/" + pkgNameApplicationName + "-unalligned.apk " \
			    + " " + pkgNameApplicationName
			multiprocess.run_command(cmdLine)
			cmdLine = "jarsigner " \
			    + " -verify -verbose -certs " \
			    + " -sigalg SHA1withRSA -digestalg SHA1 " \
			    + self.get_staging_folder(pkgName) + "/build/" + pkgNameApplicationName + "-unalligned.apk "
			multiprocess.run_command(cmdLine)
		
		debug.print_element("pkg", ".apk(aligned)", "<==", ".apk (not aligned)")
		tools.remove_file(self.get_staging_folder(pkgName) + "/" + pkgNameApplicationName + ".apk")
		# verbose mode : -v
		cmdLine = androidToolPath + "zipalign 4 " \
		          + self.get_staging_folder(pkgName) + "/build/" + pkgNameApplicationName + "-unalligned.apk " \
		          + self.get_staging_folder(pkgName) + "/" + pkgNameApplicationName + ".apk "
		multiprocess.run_command(cmdLine)
		
		# copy file in the final stage :
		tools.copy_file(self.get_staging_folder(pkgName) + "/" + pkgNameApplicationName + ".apk",
		                self.get_final_folder() + "/" + pkgNameApplicationName + ".apk",
		                force=True)
	
	def install_package(self, pkgName):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Install package '" + pkgName + "'")
		debug.debug("------------------------------------------------------------------------")
		pkgNameApplicationName = pkgName
		if self.config["mode"] == "debug":
			pkgNameApplicationName += "debug"
		cmdLine = self.folder_sdk + "/platform-tools/adb install -r " \
		          + self.get_staging_folder(pkgName) + "/" + pkgNameApplicationName + ".apk "
		multiprocess.run_command(cmdLine)
	
	def un_install_package(self, pkgName):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Un-Install package '" + pkgName + "'")
		debug.debug("------------------------------------------------------------------------")
		pkgNameApplicationName = pkgName
		if self.config["mode"] == "debug":
			pkgNameApplicationName += "debug"
		cmdLine = self.folder_sdk + "/platform-tools/adb uninstall " + pkgNameApplicationName
		Rmultiprocess.unCommand(cmdLine)
	
	def Log(self, pkgName):
		debug.debug("------------------------------------------------------------------------")
		debug.info("logcat of android board")
		debug.debug("------------------------------------------------------------------------")
		debug.info("cmd: " + self.folder_sdk + "/platform-tools/adb shell logcat ")
		cmdLine = self.folder_sdk + "/platform-tools/adb shell logcat "
		multiprocess.run_command(cmdLine)


