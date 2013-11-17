#!/usr/bin/python

import lutinDebug as debug
import lutinTarget
import lutinTools
import lutinHost
import lutinMultiprocess
import os

class Target(lutinTarget.Target):
	def __init__(self, typeCompilator, debugMode, generatePackage):
		
		self.folder_ndk = os.getenv('PROJECT_NDK', "AUTO")
		self.folder_sdk = os.getenv('PROJECT_SDK', "AUTO")
		# auto search NDK
		if self.folder_ndk == "AUTO":
			for folder in os.listdir("."):
				if os.path.isdir(folder)==True:
					if folder=="android":
						self.folder_ndk = folder + "/ndk"
			if self.folder_ndk == "AUTO":
				self.folder_ndk = lutinTools.GetRunFolder() + "/../android/ndk"
		# auto search SDK
		if self.folder_sdk == "AUTO":
			for folder in os.listdir("."):
				if os.path.isdir(folder)==True:
					if folder=="android":
						self.folder_sdk = folder + "/sdk"
			if self.folder_sdk == "AUTO":
				self.folder_sdk = lutinTools.GetRunFolder() + "/../android/sdk"
		
		
		arch = "ARMv7"
		tmpOsVal = "64"
		gccVersion = "4.8"
		if lutinHost.OS64BITS==True:
			tmpOsVal = "_64"
		if typeCompilator == "clang":
			cross = self.folder_ndk + "/toolchains/llvm-3.3/prebuilt/linux-x86_64/bin/"
		else:
			baseFolderArm = self.folder_ndk + "/toolchains/arm-linux-androideabi-" + gccVersion + "/prebuilt/linux-x86" + tmpOsVal + "/bin/"
			baseFolderMips = self.folder_ndk + "/toolchains/mipsel-linux-android-" + gccVersion + "/prebuilt/linux-x86" + tmpOsVal + "/bin/"
			baseFolderX86 = self.folder_ndk + "/toolchains/x86-" + gccVersion + "/prebuilt/linux-x86" + tmpOsVal + "/bin/"
			cross = baseFolderArm + "arm-linux-androideabi-"
			if not os.path.isdir(baseFolderArm):
				debug.error("Gcc Arm pah does not exist !!!")
			if not os.path.isdir(baseFolderMips):
				debug.info("Gcc Mips pah does not exist !!!")
			if not os.path.isdir(baseFolderX86):
				debug.info("Gcc x86 pah does not exist !!!")
		
		lutinTarget.Target.__init__(self, "Android", typeCompilator, debugMode, generatePackage, arch, cross)
		
		# for gcc :
		
		# for clang :
		
		
		self.folder_bin="/mustNotCreateBinary"
		self.folder_lib="/data/lib/armeabi"
		self.folder_data="/data/assets"
		self.folder_doc="/doc"
		self.suffix_package='.pkg'
		
		# board id at 14 is for android 4.0 and more ...
		self.boardId = 14
		self.global_include_cc.append("-I" + self.folder_ndk +"/platforms/android-" + str(self.boardId) + "/arch-arm/usr/include/")
		#self.global_include_cc.append("-I" + self.folder_ndk +"/platforms/android-" + str(self.boardId) + "/arch-mips/usr/include/")
		#self.global_include_cc.append("-I" + self.folder_ndk +"/platforms/android-" + str(self.boardId) + "/arch-x86/usr/include/")
		self.global_include_cc.append("-I" + self.folder_ndk +"/sources/cxx-stl/system/include/")
		if True:
			if typeCompilator == "clang":
				self.global_include_cc.append("-I" + self.folder_ndk +"/sources/cxx-stl/llvm-libc++/libcxx/include/")
			else:
				self.global_include_cc.append("-I" + self.folder_ndk +"/sources/cxx-stl/gnu-libstdc++/" + gccVersion + "/include/")
				#self.global_include_cc.append("-I" + self.folder_ndk +"/sources/cxx-stl/gnu-libstdc++/" + gccVersion + "/libs/x86/include/")
				self.global_include_cc.append("-I" + self.folder_ndk +"/sources/cxx-stl/gnu-libstdc++/" + gccVersion + "/libs/armeabi/include/")
				#self.global_include_cc.append("-I" + self.folder_ndk +"/sources/cxx-stl/gnu-libstdc++/" + gccVersion + "/libs/armeabi-v7a/include/")
				#self.global_include_cc.append("-I" + self.folder_ndk +"/sources/cxx-stl/gnu-libstdc++/" + gccVersion + "/libs/mips/include/")
				self.global_flags_ld.append(self.folder_ndk +"/platforms/android-" + str(self.boardId) + "/arch-arm/usr/lib/libstdc++.a")
				self.global_flags_ld.append(self.folder_ndk +"/platforms/android-" + str(self.boardId) + "/arch-arm/usr/lib/libstdc++.a")
				self.global_flags_ld.append(self.folder_ndk +"/toolchains/arm-linux-androideabi-4.8/prebuilt/linux-x86_64/arm-linux-androideabi/lib/libatomic.a")
				self.global_flags_ld.append(self.folder_ndk +"/toolchains/arm-linux-androideabi-4.8/prebuilt/linux-x86_64/arm-linux-androideabi/lib/libgomp.a")
		else :
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
		self.global_flags_cc.append("-fomit-frame-pointer")
		self.global_flags_cc.append("-fno-strict-aliasing")
		
		self.global_flags_xx.append("-frtti")
		self.global_flags_xx.append("-Wa,--noexecstack")
		
		
	
	def CheckRightPackage(self, pkgProperties, value):
		for val in pkgProperties["RIGHT"]:
			if value == val:
				return True
		return False
	
	def GetStagingFolderData(self, binaryName):
		return self.GetStagingFolder(binaryName) + self.folder_data
	
	def MakePackage(self, pkgName, pkgProperties, basePkgPath):
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
		
		compleatePackageName = pkgProperties["COMPAGNY_TYPE"]+"."+pkgProperties["COMPAGNY_NAME2"]+"." + pkgName
		
		debug.printElement("pkg", "absractionFile", "<==", "dynamic file")
		# Create folder :
		lutinTools.CreateDirectoryOfFile(self.file_finalAbstraction)
		# Create file :
		tmpFile = open(self.file_finalAbstraction, 'w')
		if pkgProperties["ANDROID_APPL_TYPE"]=="APPL":
			tmpFile.write( "/**\n")
			tmpFile.write( " * @author Edouard DUPIN, Kevin BILLONNEAU\n")
			tmpFile.write( " * @copyright 2011, Edouard DUPIN, all right reserved\n")
			tmpFile.write( " * @license BSD v3 (see license file)\n")
			tmpFile.write( " * @note This file is autogenerate ==> see documantation to generate your own\n")
			tmpFile.write( " */\n")
			tmpFile.write( "package "+ compleatePackageName + ";\n")
			tmpFile.write( "import org.ewol.EwolActivity;\n")
			tmpFile.write( "public class " + pkgName + " extends EwolActivity {\n")
			tmpFile.write( "	public void onCreate(android.os.Bundle savedInstanceState) {\n")
			tmpFile.write( "		super.onCreate(savedInstanceState);\n")
			tmpFile.write( "		initApkPath(\"" + pkgProperties["COMPAGNY_TYPE"]+"\", \""+pkgProperties["COMPAGNY_NAME2"]+"\", \"" + pkgName + "\");\n")
			tmpFile.write( "	}\n")
			tmpFile.write( "}\n")
		else :
			# wallpaper mode ...
			tmpFile.write( "/**\n")
			tmpFile.write( " * @author Edouard DUPIN, Kevin BILLONNEAU\n")
			tmpFile.write( " * @copyright 2011, Edouard DUPIN, all right reserved\n")
			tmpFile.write( " * @license BSD v3 (see license file)\n")
			tmpFile.write( " * @note This file is autogenerate ==> see documantation to generate your own\n")
			tmpFile.write( " */\n")
			tmpFile.write( "package "+ compleatePackageName + ";\n")
			tmpFile.write( "import org.ewol.EwolWallpaper;\n")
			tmpFile.write( "public class " + pkgName + " extends EwolWallpaper {\n")
			tmpFile.write( "	public static final String SHARED_PREFS_NAME = \"" + pkgName + "settings\";\n")
			tmpFile.write( "	public Engine onCreateEngine() {\n")
			tmpFile.write( "		Engine tmpEngine = super.onCreateEngine();\n")
			tmpFile.write( "		initApkPath(\"" + pkgProperties["COMPAGNY_TYPE"]+"\", \""+pkgProperties["COMPAGNY_NAME2"]+"\", \"" + pkgName + "\");\n")
			tmpFile.write( "		return tmpEngine;\n")
			tmpFile.write( "	}\n")
			tmpFile.write( "}\n")
		tmpFile.flush()
		tmpFile.close()
		
		
		lutinTools.CopyFile(pkgProperties["ICON"], self.GetStagingFolder(pkgName) + "/res/drawable/icon.png", True)
		
		
		if pkgProperties["ANDROID_MANIFEST"]!="":
			debug.printElement("pkg", "AndroidManifest.xml", "<==", pkgProperties["ANDROID_MANIFEST"])
			lutinTools.CopyFile(pkgProperties["ANDROID_MANIFEST"], self.GetStagingFolder(pkgName) + "/AndroidManifest.xml", True)
		else:
			debug.printElement("pkg", "AndroidManifest.xml", "<==", "package configurations")
			tmpFile = open(self.GetStagingFolder(pkgName) + "/AndroidManifest.xml", 'w')
			tmpFile.write( "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
			tmpFile.write( "<!-- Manifest is autoGenerated with Ewol ... do not patch it-->\n")
			tmpFile.write( "<manifest xmlns:android=\"http://schemas.android.com/apk/res/android\" \n")
			tmpFile.write( "          package=\"" + compleatePackageName + "\" \n")
			tmpFile.write( "          android:versionCode=\"1\" \n")
			tmpFile.write( "          android:versionName=\""+pkgProperties["VERSION"]+"\"> \n")
			tmpFile.write( "	<uses-feature android:glEsVersion=\"0x00020000\" android:required=\"true\" />\n")
			tmpFile.write( "	<uses-sdk android:minSdkVersion=\"" + str(self.boardId) + "\" /> \n")
			if pkgProperties["ANDROID_APPL_TYPE"]=="APPL":
				tmpFile.write( "	<application android:label=\"" + pkgName + "\" \n")
				tmpFile.write( "	             android:icon=\"@drawable/icon\">\n")
				tmpFile.write( "		<activity android:name=\"." + pkgName + "\" \n")
				tmpFile.write( "		          android:label=\"" + pkgProperties["NAME"])
				if "debug"==self.buildMode:
					tmpFile.write("-debug")
				tmpFile.write( "\"\n")
				tmpFile.write( "		          android:icon=\"@drawable/icon\" \n")
				tmpFile.write( "		          android:hardwareAccelerated=\"true\" \n")
				tmpFile.write( "		          android:configChanges=\"orientation\"> \n")
				tmpFile.write( "			<intent-filter> \n")
				tmpFile.write( "				<action android:name=\"android.intent.action.MAIN\" /> \n")
				tmpFile.write( "				<category android:name=\"android.intent.category.LAUNCHER\" /> \n")
				tmpFile.write( "			</intent-filter> \n")
				tmpFile.write( "		</activity> \n")
				tmpFile.write( "	</application> \n")
			else:
				tmpFile.write( "	<application android:label=\"" + pkgName + "\" \n")
				tmpFile.write( "	             android:permission=\"android.permission.BIND_WALLPAPER\" \n")
				tmpFile.write( "	             android:icon=\"@drawable/icon\">\n")
				tmpFile.write( "		<service android:name=\"." + pkgName + "\" \n")
				tmpFile.write( "		         android:label=\"" + pkgProperties["NAME"])
				if "debug"==self.buildMode:
					tmpFile.write("-debug")
				tmpFile.write( "\"\n")
				tmpFile.write( "		         android:icon=\"@drawable/icon\">\n")
				tmpFile.write( "			<intent-filter>\n")
				tmpFile.write( "				<action android:name=\"android.service.wallpaper.WallpaperService\" />\n")
				tmpFile.write( "			</intent-filter>\n")
				tmpFile.write( "			<meta-data android:name=\"android.service.wallpaper\"\n")
				tmpFile.write( "			           android:resource=\"@xml/" + pkgName + "_resource\" />\n")
				tmpFile.write( "		</service>\n")
				if len(pkgProperties["ANDROID_WALLPAPER_PROPERTIES"])!=0:
					tmpFile.write( "		<activity android:label=\"Setting\"\n")
					tmpFile.write( "		          android:name=\"." + pkgName + "Settings\"\n")
					tmpFile.write( "		          android:theme=\"@android:style/Theme.Light.WallpaperSettings\"\n")
					tmpFile.write( "		          android:exported=\"true\"\n")
					tmpFile.write( "		          android:icon=\"@drawable/icon\">\n")
					tmpFile.write( "		</activity>\n")
				tmpFile.write( "	</application>\n")
			# write package autorisations :
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
			# end generating android manifest
			
			if pkgProperties["ANDROID_APPL_TYPE"]!="APPL":
				#create the Wallpaper sub files : (main element for the application
				debug.printElement("pkg", pkgName + "_resource.xml", "<==", "package configurations")
				lutinTools.CreateDirectoryOfFile(self.GetStagingFolder(pkgName) + "/res/xml/" + pkgName + "_resource.xml")
				tmpFile = open(self.GetStagingFolder(pkgName) + "/res/xml/" + pkgName + "_resource.xml", 'w')
				tmpFile.write( "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
				tmpFile.write( "<wallpaper xmlns:android=\"http://schemas.android.com/apk/res/android\"\n")
				if len(pkgProperties["ANDROID_WALLPAPER_PROPERTIES"])!=0:
					tmpFile.write( "           android:settingsActivity=\""+compleatePackageName + "."+ pkgName + "Settings\"\n")
				tmpFile.write( "           android:thumbnail=\"@drawable/icon\"/>\n")
				tmpFile.flush()
				tmpFile.close()
				# create wallpaper setting if needed (class and config file)
				if len(pkgProperties["ANDROID_WALLPAPER_PROPERTIES"])!=0:
					lutinTools.CreateDirectoryOfFile(self.folder_javaProject + pkgName + "Settings.java")
					debug.printElement("pkg", self.folder_javaProject + pkgName + "Settings.java", "<==", "package configurations")
					tmpFile = open(self.folder_javaProject + pkgName + "Settings.java", 'w');
					tmpFile.write( "package " + compleatePackageName + ";\n")
					tmpFile.write( "\n")
					tmpFile.write( "import " + compleatePackageName + ".R;\n")
					tmpFile.write( "\n")
					tmpFile.write( "import android.content.SharedPreferences;\n")
					tmpFile.write( "import android.os.Bundle;\n")
					tmpFile.write( "import android.preference.PreferenceActivity;\n")
					tmpFile.write( "\n")
					tmpFile.write( "public class " + pkgName + "Settings extends PreferenceActivity implements SharedPreferences.OnSharedPreferenceChangeListener\n")
					tmpFile.write( "{\n")
					tmpFile.write( "	@Override protected void onCreate(Bundle icicle) {\n")
					tmpFile.write( "		super.onCreate(icicle);\n")
					tmpFile.write( "		getPreferenceManager().setSharedPreferencesName("+ pkgName + ".SHARED_PREFS_NAME);\n")
					tmpFile.write( "		addPreferencesFromResource(R.xml."+ pkgName  + "_settings);\n")
					tmpFile.write( "		getPreferenceManager().getSharedPreferences().registerOnSharedPreferenceChangeListener(this);\n")
					tmpFile.write( "	}\n")
					tmpFile.write( "	@Override protected void onResume() {\n")
					tmpFile.write( "		super.onResume();\n")
					tmpFile.write( "	}\n")
					tmpFile.write( "	@Override protected void onDestroy() {\n")
					tmpFile.write( "		getPreferenceManager().getSharedPreferences().unregisterOnSharedPreferenceChangeListener(this);\n")
					tmpFile.write( "		super.onDestroy();\n")
					tmpFile.write( "	}\n")
					tmpFile.write( "	public void onSharedPreferenceChanged(SharedPreferences sharedPreferences,String key) { }\n")
					tmpFile.write( "}\n")
					tmpFile.flush()
					tmpFile.close()
					
					debug.printElement("pkg", self.GetStagingFolder(pkgName) + "/res/xml/" + pkgName + "_settings.xml", "<==", "package configurations")
					lutinTools.CreateDirectoryOfFile(self.GetStagingFolder(pkgName) + "/res/xml/" + pkgName + "_settings.xml")
					tmpFile = open(self.GetStagingFolder(pkgName) + "/res/xml/" + pkgName + "_settings.xml", 'w');
					tmpFile.write( "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
					tmpFile.write( "<PreferenceScreen xmlns:android=\"http://schemas.android.com/apk/res/android\"\n")
					tmpFile.write( "                  android:title=\"Settings\"\n")
					tmpFile.write( "                  android:key=\"" + pkgName  + "_settings\">\n")
					WALL_haveArray = False
					for WALL_type, WALL_key, WALL_title, WALL_summary, WALL_other in pkgProperties["ANDROID_WALLPAPER_PROPERTIES"]:
						debug.info("find : '" + WALL_type + "'");
						if WALL_type == "list":
							debug.info("    create : LIST");
							tmpFile.write( "	<ListPreference android:key=\"" + pkgName + "_" + WALL_key + "\"\n")
							tmpFile.write( "	                android:title=\"" + WALL_title + "\"\n")
							tmpFile.write( "	                android:summary=\"" + WALL_summary + "\"\n")
							tmpFile.write( "	                android:entries=\"@array/" + pkgName + "_" + WALL_key + "_names\"\n")
							tmpFile.write( "	                android:entryValues=\"@array/" + pkgName + "_" + WALL_key + "_prefix\"/>\n")
							WALL_haveArray=True
						elif WALL_type == "bool":
							debug.info("    create : CHECKBOX");
							tmpFile.write( "	<CheckBoxPreference android:key=\"" + pkgName + "_" + WALL_key + "\"\n")
							tmpFile.write( "	                    android:title=\"" + WALL_title + "\"\n")
							tmpFile.write( "	                    android:summary=\"" + WALL_summary + "\"\n")
							tmpFile.write( "	                    android:summaryOn=\"" + WALL_other[0] + "\"\n")
							tmpFile.write( "	                    android:summaryOff=\"" + WALL_other[1] + "\"/>\n")
					tmpFile.write( "</PreferenceScreen>\n")
					tmpFile.flush()
					tmpFile.close()
					if WALL_haveArray==True:
						for WALL_type, WALL_key, WALL_title, WALL_summary, WALL_other in pkgProperties["ANDROID_WALLPAPER_PROPERTIES"]:
							if WALL_type == "list":
								debug.printElement("pkg", self.GetStagingFolder(pkgName) + "/res/values/" + WALL_key + ".xml", "<==", "package configurations")
								lutinTools.CreateDirectoryOfFile(self.GetStagingFolder(pkgName) + "/res/values/" + WALL_key + ".xml")
								tmpFile = open(self.GetStagingFolder(pkgName) + "/res/values/" + WALL_key + ".xml", 'w');
								tmpFile.write( "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
								tmpFile.write( "<resources xmlns:xliff=\"urn:oasis:names:tc:xliff:document:1.2\">\n")
								tmpFile.write( "	<string-array name=\"" + pkgName + "_" + WALL_key + "_names\">\n")
								for WALL_subKey, WALL_display in WALL_other:
									tmpFile.write( "		<item>" + WALL_display + "</item>\n")
								tmpFile.write( "	</string-array>\n")
								tmpFile.write( "	<string-array name=\"" + pkgName + "_" + WALL_key + "_prefix\">\n")
								for WALL_subKey, WALL_display in WALL_other:
									tmpFile.write( "		<item>" + WALL_subKey + "</item>\n")
								tmpFile.write( "	</string-array>\n")
								tmpFile.write( "</resources>\n")
								tmpFile.flush()
								tmpFile.close()
						
		
		#add properties on wallpaper : 
		# myModule.pkgAdd("ANDROID_WALLPAPER_PROPERTIES", ["list", key, title, summary, [["key","value display"],["key2","value display 2"]])
		# myModule.pkgAdd("ANDROID_WALLPAPER_PROPERTIES", ["list", "testpattern", "Select test pattern", "Choose which test pattern to display", [["key","value display"],["key2","value display 2"]]])
		# myModule.pkgAdd("ANDROID_WALLPAPER_PROPERTIES", ["bool", key, title, summary, ["enable string", "disable String"])
		# myModule.pkgAdd("ANDROID_WALLPAPER_PROPERTIES", ["bool", "movement", "Motion", "Apply movement to test pattern", ["Moving test pattern", "Still test pattern"]
		#copy needed resources :
		for res_source, res_dest in pkgProperties["ANDROID_RESOURCES"]:
			if res_source == "":
				continue
			lutinTools.CopyFile(res_source , self.GetStagingFolder(pkgName) + "/res/" + res_dest + "/" + os.path.basename(res_source), True)
		
		
		# Doc :
		# http://asantoso.wordpress.com/2009/09/15/how-to-build-android-application-package-apk-from-the-command-line-using-the-sdk-tools-continuously-integrated-using-cruisecontrol/
		debug.printElement("pkg", "R.java", "<==", "Resources files")
		lutinTools.CreateDirectoryOfFile(self.GetStagingFolder(pkgName) + "/src/noFile")
		androidToolPath = self.folder_sdk + "/build-tools/19.0.0/"
		cmdLine = androidToolPath + "aapt p -f " \
		          + "-M " + self.GetStagingFolder(pkgName) + "/AndroidManifest.xml " \
		          + "-F " + self.GetStagingFolder(pkgName) + "/resources.res " \
		          + "-I " + self.folder_sdk + "/platforms/android-" + str(self.boardId) + "/android.jar "\
		          + "-S " + self.GetStagingFolder(pkgName) + "/res/ " \
		          + "-J " + self.GetStagingFolder(pkgName) + "/src "
		lutinMultiprocess.RunCommand(cmdLine)
		#aapt  package -f -M ${manifest.file} -F ${packaged.resource.file} -I ${path.to.android-jar.library} 
		#      -S ${android-resource-directory} [-m -J ${folder.to.output.the.R.java}]
		
		lutinTools.CreateDirectoryOfFile(self.GetStagingFolder(pkgName) + "/build/classes/noFile")
		debug.printElement("pkg", "*.class", "<==", "*.java")
		# more information with : -Xlint
		#          + self.file_finalAbstraction + " "\ # this generate ex: out/Android/debug/staging/tethys/src/com/edouarddupin/tethys/edn.java
		
		#generate android java files:
		filesString=""
		for element in pkgProperties["ANDROID_JAVA_FILES"]:
			if element=="DEFAULT":
				filesString += self.folder_ewol + "/sources/android/src/org/ewol/EwolAudioTask.java "
				filesString += self.folder_ewol + "/sources/android/src/org/ewol/EwolCallback.java "
				filesString += self.folder_ewol + "/sources/android/src/org/ewol/EwolConstants.java "
				filesString += self.folder_ewol + "/sources/android/src/org/ewol/Ewol.java "
				filesString += self.folder_ewol + "/sources/android/src/org/ewol/EwolRendererGL.java "
				filesString += self.folder_ewol + "/sources/android/src/org/ewol/EwolSurfaceViewGL.java "
				filesString += self.folder_ewol + "/sources/android/src/org/ewol/EwolActivity.java "
				filesString += self.folder_ewol + "/sources/android/src/org/ewol/EwolWallpaper.java "
			else:
				filesString += element + " "
		
		if len(pkgProperties["ANDROID_WALLPAPER_PROPERTIES"])!=0:
			filesString += self.folder_javaProject + pkgName + "Settings.java "
		
		cmdLine = "javac " \
		          + "-d " + self.GetStagingFolder(pkgName) + "/build/classes " \
		          + "-classpath " + self.folder_sdk + "/platforms/android-" + str(self.boardId) + "/android.jar " \
		          + filesString \
		          + self.file_finalAbstraction + " "  \
		          + self.GetStagingFolder(pkgName) + "/src/R.java "
		lutinMultiprocess.RunCommand(cmdLine)
		
		debug.printElement("pkg", ".dex", "<==", "*.class")
		cmdLine = androidToolPath + "dx " \
		          + "--dex --no-strict " \
		          + "--output=" + self.GetStagingFolder(pkgName) + "/build/" + pkgName + ".dex " \
		          + self.GetStagingFolder(pkgName) + "/build/classes/ "
		lutinMultiprocess.RunCommand(cmdLine)
		
		debug.printElement("pkg", ".apk", "<==", ".dex, assets, .so, res")
		#builderDebug="-agentlib:jdwp=transport=dt_socket,server=y,address=8050,suspend=y "
		builderDebug=""
		cmdLine =   "java -Xmx128M " \
		          + "-classpath " + self.folder_sdk + "/tools/lib/sdklib.jar " \
		          + builderDebug \
		          + "com.android.sdklib.build.ApkBuilderMain " \
		          + self.GetStagingFolder(pkgName) + "/build/" + pkgName + "-unalligned.apk " \
		          + "-u " \
		          + "-z " + self.GetStagingFolder(pkgName) + "/resources.res " \
		          + "-f " + self.GetStagingFolder(pkgName) + "/build/" + pkgName + ".dex " \
		          + "-rf " + self.GetStagingFolder(pkgName) + "/data "
		lutinMultiprocess.RunCommand(cmdLine)
		
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
			debug.printElement("pkg", ".apk(signed debug)", "<==", ".apk (not signed)")
			# verbose mode : 
			#debugOption = "-verbose -certs "
			debugOption = ""
			cmdLine = "jarsigner " \
			    + debugOption \
			    + "-keystore " + lutinTools.GetCurrentPath(__file__) + "/AndroidDebugKey.jks " \
			    + self.GetStagingFolder(pkgName) + "/build/" + pkgName + "-unalligned.apk " \
			    + " alias__AndroidDebugKey " \
			    + " < tmpPass.boo"
			lutinMultiprocess.RunCommand(cmdLine)
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
		
		debug.printElement("pkg", ".apk(aligned)", "<==", ".apk (not aligned)")
		lutinTools.RemoveFile(self.GetStagingFolder(pkgName) + "/" + pkgName + ".apk")
		# verbose mode : -v
		cmdLine = self.folder_sdk + "/tools/zipalign 4 " \
		          + self.GetStagingFolder(pkgName) + "/build/" + pkgName + "-unalligned.apk " \
		          + self.GetStagingFolder(pkgName) + "/" + pkgName + ".apk "
		lutinMultiprocess.RunCommand(cmdLine)
		
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
		lutinMultiprocess.RunCommand(cmdLine)
	
	def UnInstallPackage(self, pkgName):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Un-Install package '" + pkgName + "'")
		debug.debug("------------------------------------------------------------------------")
		cmdLine = self.folder_sdk + "/platform-tools/adb uninstall " + pkgName
		RlutinMultiprocess.unCommand(cmdLine)
	
	def Log(self, pkgName):
		debug.debug("------------------------------------------------------------------------")
		debug.info("logcat of android board")
		debug.debug("------------------------------------------------------------------------")
		cmdLine = self.folder_sdk + "/platform-tools/adb shell logcat "
		lutinMultiprocess.RunCommand(cmdLine)


