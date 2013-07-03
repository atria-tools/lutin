#!/usr/bin/python

import lutinDebug as debug
import lutinTarget
import lutinTools
import os

def RunCommand(cmdLine):
	debug.debug(cmdLine)
	ret = os.system(cmdLine)
	# TODO : Use "subprocess" instead ==> permit to pipline the renderings ...
	if ret != 0:
		if ret == 2:
			debug.error("can not execute cmdLine ... [keyboard interrrupt]")
		else:
			debug.error("can not execute cmdLine ... ret : " + str(ret))


class Target(lutinTarget.Target):
	def __init__(self, typeCompilator, debugMode, generatePackage):
		
		self.folder_ndk = os.getenv('PROJECT_NDK', lutinTools.GetRunFolder() + "/../android/ndk")
		self.folder_sdk = os.getenv('PROJECT_SDK', lutinTools.GetRunFolder() + "/../android/sdk")
		arch = "ARMv7"
		cross = self.folder_ndk + "/toolchains/arm-linux-androideabi-4.4.3/prebuilt/linux-x86/bin/arm-linux-androideabi-"
		
		if typeCompilator!="gcc":
			debug.error("Android does not support '" + typeCompilator + "' compilator ... availlable : [gcc]")
		
		lutinTarget.Target.__init__(self, "Android", "gcc", debugMode, generatePackage, arch, cross)
		
		
		self.folder_bin="/mustNotCreateBinary"
		self.folder_lib="/data/lib/armeabi"
		self.folder_data="/data/assets"
		self.folder_doc="/doc"
		self.suffix_package='.pkg'
		
		# board id at 14 is for android 4.0 and more ...
		self.boardId = 14
		self.global_include_cc.append("-I" + self.folder_ndk +"/platforms/android-" + str(self.boardId) + "/arch-arm/usr/include")
		self.global_include_cc.append("-I" + self.folder_ndk +"/sources/cxx-stl/system/include/")
		
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
		self.global_flags_cc.append("-fno-exceptions")
		self.global_flags_cc.append("-fomit-frame-pointer")
		self.global_flags_cc.append("-fno-strict-aliasing")
		
		self.global_flags_xx.append("-fno-rtti")
		self.global_flags_xx.append("-Wa,--noexecstack")
		
		
	
	def CheckRightPackage(self, pkgProperties, value):
		for val in pkgProperties["RIGHT"]:
			if value == val:
				return True
		return False
	
	def MakePackage(self, pkgName, pkgProperties):
		# http://alp.developpez.com/tutoriels/debian/creer-paquet/
		debug.debug("------------------------------------------------------------------------")
		debug.info("Generate package '" + pkgName + "'")
		debug.debug("------------------------------------------------------------------------")
		# FINAL_FOLDER_JAVA_PROJECT
		self.folder_javaProject=   self.GetStagingFolder(pkgName) \
		                         + "/src/" \
		                         + pkgProperties["COMPAGNY_TYPE"] \
		                         + "/" + pkgProperties["COMPAGNY_NAME2"] \
		                         + "/" + pkgName + "/"
		#FINAL_FILE_ABSTRACTION
		self.file_finalAbstraction = self.folder_javaProject + "/" + pkgName + ".java"
		
		#lutinTools.CopyFile(self.folder_ewol + "/sources/android/PROJECT_NAME.java", self.file_finalAbstraction, True)
		
		#os.system("sed -i \"s|__PROJECT_ORG_TYPE__|"+pkgProperties["COMPAGNY_TYPE"]+"|\" " + self.file_finalAbstraction)
		#os.system("sed -i \"s|__PROJECT_VENDOR__|"+pkgProperties["COMPAGNY_NAME2"]+"|\" " + self.file_finalAbstraction)
		#os.system("sed -i \"s|__PROJECT_NAME__|" + pkgName + "|\" "+ self.file_finalAbstraction)
		#os.system("sed -i \"s|__PROJECT_PACKAGE__|" + pkgName + "|\" " + self.file_finalAbstraction)
		#os.system("sed -i \"s|__CONF_OGL_ES_V__|2|\" " + self.file_finalAbstraction)
		
		lutinTools.CopyFile(pkgProperties["ICON"], self.GetStagingFolder(pkgName) + "/res/drawable/icon.png", True)
		
		debug.printElement("pkg", "AndroidManifest.xml", "<==", "package configurations")
		tmpFile = open(self.GetStagingFolder(pkgName) + "/AndroidManifest.xml", 'w')
		tmpFile.write( "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
		tmpFile.write( "<!-- Manifest is autoGenerated with Ewol ... do not patch it-->\n")
		tmpFile.write( "<manifest xmlns:android=\"http://schemas.android.com/apk/res/android\" \n")
		tmpFile.write( "          package=\""+pkgProperties["COMPAGNY_TYPE"]+"."+pkgProperties["COMPAGNY_NAME2"]+"." + pkgName + "\" \n")
		tmpFile.write( "          android:versionCode=\"1\" \n")
		tmpFile.write( "          android:versionName=\""+pkgProperties["VERSION"]+"\"> \n")
		tmpFile.write( "    <uses-feature android:glEsVersion=\"0x00020000\" android:required=\"true\" />\n")
		tmpFile.write( "    <uses-sdk android:minSdkVersion=\"" + str(self.boardId) + "\" /> \n")
		tmpFile.write( "	\n")
		tmpFile.write( "	<application android:label=\"" + pkgName + "\" \n")
		tmpFile.write( "	             android:icon=\"@drawable/icon\" >\n")
		tmpFile.write( "		<activity android:name=\"." + pkgName + "\" \n")
		if "debug"==self.buildMode:
			tmpFile.write( "		          android:label=\"" + pkgProperties["NAME"] + "-debug\" \n")
		else:
			tmpFile.write( "		          android:label=\"" + pkgProperties["NAME"] + "\" \n")
		tmpFile.write( "		          android:icon=\"@drawable/icon\" \n")
		tmpFile.write( "		          android:hardwareAccelerated=\"true\" \n")
		tmpFile.write( "		          android:configChanges=\"orientation\"> \n")
		tmpFile.write( "			<intent-filter> \n")
		tmpFile.write( "				<action android:name=\"android.intent.action.MAIN\" /> \n")
		tmpFile.write( "				<category android:name=\"android.intent.category.LAUNCHER\" /> \n")
		tmpFile.write( "			</intent-filter> \n")
		tmpFile.write( "		</activity> \n")
		tmpFile.write( "	</application> \n")
		if True==self.CheckRightPackage(pkgProperties, "WRITE_EXTERNAL_STORAGE"):
			tmpFile.write( "	<uses-permission android:name=\"android.permission.WRITE_EXTERNAL_STORAGE\" /> \n")
		if True==self.CheckRightPackage(pkgProperties, "CAMERA"):
			tmpFile.write( "	<uses-permission android:name=\"android.permission.CAMERA\" /> \n")
		if True==self.CheckRightPackage(pkgProperties, "INTERNET"):
			tmpFile.write( "	<uses-permission android:name=\"android.permission.INTERNET\" /> \n")
		if True==self.CheckRightPackage(pkgProperties, "MODIFY_AUDIO_SETTINGS"):
			tmpFile.write( "	<uses-permission android:name=\"android.permission.MODIFY_AUDIO_SETTINGS\" /> \n")
		if True==self.CheckRightPackage(pkgProperties, "READ_CALENDAR"):
			tmpFile.write( "	<uses-permission android:name=\"android.permission.READ_CALENDAR\" /> \n")
		if True==self.CheckRightPackage(pkgProperties, "READ_CONTACTS"):
			tmpFile.write( "	<uses-permission android:name=\"android.permission.READ_CONTACTS\" /> \n")
		if True==self.CheckRightPackage(pkgProperties, "READ_FRAME_BUFFER"):
			tmpFile.write( "	<uses-permission android:name=\"android.permission.READ_FRAME_BUFFER\" /> \n")
		if True==self.CheckRightPackage(pkgProperties, "READ_PROFILE"):
			tmpFile.write( "	<uses-permission android:name=\"android.permission.READ_PROFILE\" /> \n")
		if True==self.CheckRightPackage(pkgProperties, "RECORD_AUDIO"):
			tmpFile.write( "	<uses-permission android:name=\"android.permission.RECORD_AUDIO\" /> \n")
		if True==self.CheckRightPackage(pkgProperties, "SET_ORIENTATION"):
			tmpFile.write( "	<uses-permission android:name=\"android.permission.SET_ORIENTATION\" /> \n")
		if True==self.CheckRightPackage(pkgProperties, "VIBRATE"):
			tmpFile.write( "	<uses-permission android:name=\"android.permission.VIBRATE\" /> \n")
		if True==self.CheckRightPackage(pkgProperties, "ACCESS_COARSE_LOCATION"):
			tmpFile.write( "	<uses-permission android:name=\"android.permission.ACCESS_COARSE_LOCATION\" /> \n")
		if True==self.CheckRightPackage(pkgProperties, "ACCESS_FINE_LOCATION"):
			tmpFile.write( "	<uses-permission android:name=\"android.permission.ACCESS_FINE_LOCATION\" /> \n")
		tmpFile.write( "</manifest>\n\n")
		tmpFile.flush()
		tmpFile.close()
		
		# Doc :
		# http://asantoso.wordpress.com/2009/09/15/how-to-build-android-application-package-apk-from-the-command-line-using-the-sdk-tools-continuously-integrated-using-cruisecontrol/
		debug.printElement("pkg", "R.java", "<==", "Resources files")
		lutinTools.CreateDirectoryOfFile(self.GetStagingFolder(pkgName) + "/src/noFile")
		cmdLine = self.folder_sdk + "/platform-tools/aapt p -f " \
		          + "-M " + self.GetStagingFolder(pkgName) + "/AndroidManifest.xml " \
		          + "-F " + self.GetStagingFolder(pkgName) + "/resources.res " \
		          + "-I " + self.folder_sdk + "/platforms/android-" + str(self.boardId) + "/android.jar "\
		          + "-S " + self.GetStagingFolder(pkgName) + "/res/ " \
		          + "-J " + self.GetStagingFolder(pkgName) + "/src "
		RunCommand(cmdLine)
		#aapt  package -f -M ${manifest.file} -F ${packaged.resource.file} -I ${path.to.android-jar.library} 
		#      -S ${android-resource-directory} [-m -J ${folder.to.output.the.R.java}]
		
		lutinTools.CreateDirectoryOfFile(self.GetStagingFolder(pkgName) + "/build/classes/noFile")
		debug.printElement("pkg", "*.class", "<==", "*.java")
		# more information with : -Xlint
		#          + self.file_finalAbstraction + " "\ # this generate ex: out/Android/debug/staging/tethys/src/com/edouarddupin/tethys/edn.java
		cmdLine = "javac " \
		          + "-d " + self.GetStagingFolder(pkgName) + "/build/classes " \
		          + "-classpath " + self.folder_sdk + "/platforms/android-" + str(self.boardId) + "/android.jar " \
		          + self.folder_ewol + "/sources/android/src/org/ewol/EwolAudioTask.java " \
		          + self.folder_ewol + "/sources/android/src/org/ewol/EwolCallback.java " \
		          + self.folder_ewol + "/sources/android/src/org/ewol/EwolConstants.java " \
		          + self.folder_ewol + "/sources/android/src/org/ewol/Ewol.java " \
		          + self.folder_ewol + "/sources/android/src/org/ewol/EwolRendererGL.java " \
		          + self.folder_ewol + "/sources/android/src/org/ewol/EwolSurfaceViewGL.java " \
		          + self.GetStagingFolder(pkgName) + "/src/R.java "
		RunCommand(cmdLine)
		
		debug.printElement("pkg", ".dex", "<==", "*.class")
		cmdLine = self.folder_sdk + "/platform-tools/dx " \
		          + "--dex --no-strict " \
		          + "--output=" + self.GetStagingFolder(pkgName) + "/build/" + pkgName + ".dex " \
		          + self.GetStagingFolder(pkgName) + "/build/classes/ "
		RunCommand(cmdLine)
		
		debug.printElement("pkg", ".apk", "<==", ".dex, assets, .so, res")
		cmdLine = self.folder_sdk + "/tools/apkbuilder " \
		    + self.GetStagingFolder(pkgName) + "/build/" + pkgName + "-unalligned.apk " \
		    + "-u " \
		    + "-z " + self.GetStagingFolder(pkgName) + "/resources.res " \
		    + "-f " + self.GetStagingFolder(pkgName) + "/build/" + pkgName + ".dex " \
		    + "-rf " + self.GetStagingFolder(pkgName) + "/data "
		RunCommand(cmdLine)
		
		# doc :
		# http://developer.android.com/tools/publishing/app-signing.html
		if "debug"==self.buildMode:
			# To create the debug Key ==> for all ...
			#keytool -genkeypair -v -keystore $(BUILD_SYSTEM)/AndroidDebugKey.jks -storepass Pass__AndroidDebugKey -alias alias__AndroidDebugKey -keypass PassKey__AndroidDebugKey -keyalg RSA -validity 36500
			# use default common generic debug key:
			# generate the pass file (debug mode does not request to have a complicated key) :
			tmpFile = open("tmpPass.boo", 'w')
			tmpFile.write("Pass__AndroidDebugKey\n")
			tmpFile.write("PassKey__AndroidDebugKey\n")
			tmpFile.flush()
			tmpFile.close()
			# verbose mode : -verbose
			cmdLine = "jarsigner " \
			    + "-keystore " + lutinTools.GetCurrentPath(__file__) + "/AndroidDebugKey.jks " \
			    + self.GetStagingFolder(pkgName) + "/build/" + pkgName + "-unalligned.apk " \
			    + " alias__AndroidDebugKey " \
			    + " < tmpPass.boo"
			RunCommand(cmdLine)
			print("")
		else:
			# keytool is situated in $(JAVA_HOME)/bin ...
			#TODO : call the user the pass and the loggin he want ...
			#$(if $(wildcard ./config/AndroidKey_$(PROJECT_NAME2).jks),$(empty), \
			#	$(Q)echo "./config/$(PROJECT_NAME2).jks <== dynamic key (NOTE : It might ask some question to generate the key for android)" ; \
			#	$(Q)keytool -genkeypair -v \
			#	    -keystore ./config/$(PROJECT_NAME2).jks \
			#	    -alias alias_$(PROJECT_NAME2) \
			#	    -keyalg RSA \
			#	    -validity 365 \
			#)
			# note we can add : -storepass Pass$(PROJECT_NAME2)
			# note we can add : -keypass PassK$(PROJECT_NAME2)
			
			# Question poser a ce moment, les automatiser ...
			# Quels sont vos prenom et nom ?
			# EdoGetRunFolderuard DUPIN
			#   [Unknown] :  Quel est le nom de votre unite organisationnelle ?
			# org
			#   [Unknown] :  Quelle est le nom de votre organisation ?
			# EWOL
			#   [Unknown] :  Quel est le nom de votre ville de residence ?
			# Paris
			#   [Unknown] :  Quel est le nom de votre etat ou province ?
			# France
			#   [Unknown] :  Quel est le code de pays a deux lettres pour cette unite ?
			# FR
			#   [Unknown] :  Est-ce CN=Edouard DUPIN, OU=org, O=EWOL, L=Paris, ST=France, C=FR ?
			# oui
			#   [non] :  
			# Generation d'une paire de clees RSA de a 024 bits et d'un certificat autosigne (SHA1withRSA) d'une validite de 365 jours
			# 	pour : CN=Edouard DUPIN, OU=org, O=EWOL, L=Paris, ST=France, C=FR
			
			# keytool is situated in $(JAVA_HOME)/bin ...
			#echo "apk(Signed) <== apk"
			# sign the application request loggin and password : 
			#jarsigner \
			#    -keystore ./config/AndroidKey_$(PROJECT_NAME2).jks \
			#    $(TARGET_OUT_STAGING)/build/$(PROJECT_NAME2)-unalligned.apk \
			#    alias_$(PROJECT_NAME2)
			debug.warning("TODO ...")
		
		debug.printElement("pkg", ".apk(aligned)", "<==", ".apk")
		lutinTools.RemoveFile(self.GetStagingFolder(pkgName) + "/" + pkgName + ".apk")
		# verbose mode : -v
		cmdLine = self.folder_sdk + "/tools/zipalign 4 " \
		          + self.GetStagingFolder(pkgName) + "/build/" + pkgName + "-unalligned.apk " \
		          + self.GetStagingFolder(pkgName) + "/" + pkgName + ".apk "
		RunCommand(cmdLine)
		
		# copy file in the final stage :
		lutinTools.CopyFile(self.GetStagingFolder(pkgName) + "/" + pkgName + ".apk",
		                    self.GetFinalFolder() + "/" + pkgName + ".apk",
		                    True)
	
	def InstallPackage(self, pkgName):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Install package '" + pkgName + "'")
		debug.debug("------------------------------------------------------------------------")
		cmdLine = self.folder_sdk + "/platform-tools/adb install -r " \
		          + self.GetStagingFolder(pkgName) + "/" + pkgName + ".apk "
		RunCommand(cmdLine)
	
	def UnInstallPackage(self, pkgName):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Un-Install package '" + pkgName + "'")
		debug.debug("------------------------------------------------------------------------")
		cmdLine = self.folder_sdk + "/platform-tools/adb uninstall " + pkgName
		RunCommand(cmdLine)
	
	def Log(self, pkgName):
		debug.debug("------------------------------------------------------------------------")
		debug.info("logcat of android board")
		debug.debug("------------------------------------------------------------------------")
		cmdLine = self.folder_sdk + "/platform-tools/adb shell logcat "
		RunCommand(cmdLine)


