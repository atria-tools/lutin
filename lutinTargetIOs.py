#!/usr/bin/python
import lutinDebug as debug
import lutinTarget
import lutinTools
import os
import stat
import lutinExtProjectGeneratorXCode
import lutinMultiprocess
import random

class Target(lutinTarget.Target):
	def __init__(self, typeCompilator, debugMode, generatePackage):
		cross = "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/"
		if typeCompilator == "gcc":
			debug.info("compile only with clang for IOs");
			typeCompilator = "clang"
		# http://biolpc22.york.ac.uk/pub/linux-mac-cross/
		# http://devs.openttd.org/~truebrain/compile-farm/apple-darwin9.txt
		lutinTarget.Target.__init__(self, "IOs", typeCompilator, debugMode, generatePackage, "i386", cross)
		
		# remove unneeded ranlib ...
		self.ranlib=""
		self.folder_bin=""
		self.folder_data="/share"
		self.folder_doc="/doc"
		
		self.suffix_lib_static='.a'
		self.suffix_lib_dynamic='.dylib'
		self.suffix_binary=''
		self.suffix_package=''
		
		self.sysroot = "-isysroot /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator7.0.sdk"
		
		self.global_flags_ld.append([
			"-mios-simulator-version-min=7.0",
			"-Xlinker",
			"-objc_abi_version",
			"-Xlinker 2",
			"-Xlinker",
			"-no_implicit_dylibs",
			"-stdlib=libc++",
			"-fobjc-arc",
			"-fobjc-link-runtime"])
	
		self.global_flags_cc.append("-mios-simulator-version-min=7.0")
		
		#add a project generator:
		self.externProjectManager = lutinExtProjectGeneratorXCode.ExtProjectGeneratorXCode()

	def get_staging_folder(self, binaryName):
		return lutinTools.get_run_folder() + self.folder_out + self.folder_staging + "/" + binaryName + ".app/"
	
	def get_staging_folder_data(self, binaryName):
		return self.get_staging_folder(binaryName) + self.folder_data + "/"
	
	def make_package(self, pkgName, pkgProperties, basePkgPath):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Generate package '" + pkgName + "'")
		debug.debug("------------------------------------------------------------------------")
		
		if    "ICON" in pkgProperties.keys() \
		   and pkgProperties["ICON"] != "":
			lutinTools.copy_file(pkgProperties["ICON"], self.get_staging_folder_data(pkgName) + "/icon.icns", True)
		
		# http://www.sandroid.org/imcross/#Deployment
		infoFile=self.get_staging_folder(pkgName) + "/Info.plist"
		# Create the info file
		tmpFile = open(infoFile, 'w')
		tmpFile.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
		tmpFile.write("<!DOCTYPE plist PUBLIC \"-//Apple Computer//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n")
		tmpFile.write("<plist version=\"1.0\">\n")
		tmpFile.write("		<dict>\n")
		tmpFile.write("			<key>CFBundleDevelopmentRegion</key>\n")
		tmpFile.write("			<string>en</string>\n")
		tmpFile.write("			<key>CFBundleDisplayName</key>\n")
		tmpFile.write("			<string>" + pkgProperties["NAME"] + "</string>\n")
		tmpFile.write("			<key>CFBundleExecutable</key>\n")
		tmpFile.write("			<string>" + pkgName + "</string>\n")
		tmpFile.write("			<key>CFBundleIdentifier</key>\n")
		tmpFile.write("			<string>com." + pkgProperties["COMPAGNY_NAME2"] + "." + pkgName + "</string>\n")
		"""
		tmpFile.write("			<key>CFBundleIconFile</key>\n")
		tmpFile.write("			<string>icon.icns</string>\n")
		"""
		tmpFile.write("			<key>CFBundleInfoDictionaryVersion</key>\n")
		tmpFile.write("			<string>6.0</string>\n")
		tmpFile.write("			<key>CFBundleName</key>\n")
		tmpFile.write("			<string>" + pkgName + "</string>\n")
		tmpFile.write("			<key>CFBundlePackageType</key>\n")
		tmpFile.write("			<string>APPL</string>\n")
		tmpFile.write("			<key>CFBundleShortVersionString</key>\n")
		tmpFile.write("			<string>1.0</string>\n")
		tmpFile.write("			<key>CFBundleSignature</key>\n")
		tmpFile.write("			<string>????</string>\n")
		tmpFile.write("			<key>CFBundleSupportedPlatforms</key>\n")
		tmpFile.write("			<array>\n")
		tmpFile.write("				<string>iPhoneSimulator</string>\n")
		tmpFile.write("			</array>\n")
		"""
		tmpFile.write("			<key>CFBundleVersion</key>\n")
		tmpFile.write("			<string>1.0</string>\n")
		"""
		tmpFile.write("			<key>DTPlatformName</key>\n")
		tmpFile.write("			<string>iphonesimulator</string>\n")
		tmpFile.write("			<key>DTSDKName</key>\n")
		tmpFile.write("			<string>iphonesimulator7.0</string>\n")
		"""
		tmpFile.write("			<key>LSRequiresIPhoneOS</key>\n")
		tmpFile.write("			<true/>\n")
		"""
		tmpFile.write("			<key>UIDeviceFamily</key>\n")
		tmpFile.write("			<array>\n")
		tmpFile.write("				<integer>1</integer>\n")
		tmpFile.write("				<integer>2</integer>\n")
		tmpFile.write("			</array>\n")
		"""
		tmpFile.write("			<key>UILaunchImages</key>\n")
		tmpFile.write("			<array>\n")
		tmpFile.write("				<dict>\n")
		tmpFile.write("					<key>UILaunchImageMinimumOSVersion</key>\n")
		tmpFile.write("					<string>7.0</string>\n")
		tmpFile.write("					<key>UILaunchImageName</key>\n")
		tmpFile.write("					<string>LaunchImage-700-568h</string>\n")
		tmpFile.write("					<key>UILaunchImageOrientation</key>\n")
		tmpFile.write("					<string>Portrait</string>\n")
		tmpFile.write("					<key>UILaunchImageSize</key>\n")
		tmpFile.write("					<string>{320, 568}</string>\n")
		tmpFile.write("				</dict>\n")
		tmpFile.write("			</array>\n")
		"""
		"""
		tmpFile.write("			<key>UIMainStoryboardFile</key>\n")
		tmpFile.write("			<string>Main_iPhone</string>\n")
		tmpFile.write("			<key>UIMainStoryboardFile~ipad</key>\n")
		tmpFile.write("			<string>Main_iPad</string>\n")
		"""
		tmpFile.write("			<key>UIRequiredDeviceCapabilities</key>\n")
		tmpFile.write("			<array>\n")
		tmpFile.write("				<string>armv7</string>\n")
		tmpFile.write("			</array>\n")
		tmpFile.write("			<key>UIStatusBarHidden</key>\n")
		tmpFile.write("			<true/>\n")
		tmpFile.write("			<key>UISupportedInterfaceOrientations</key>\n")
		tmpFile.write("			<array>\n")
		tmpFile.write("				<string>UIInterfaceOrientationPortrait</string>\n")
		tmpFile.write("				<string>UIInterfaceOrientationPortraitUpsideDown</string>\n")
		tmpFile.write("				<string>UIInterfaceOrientationLandscapeLeft</string>\n")
		tmpFile.write("				<string>UIInterfaceOrientationLandscapeRight</string>\n")
		tmpFile.write("			</array>\n")
		tmpFile.write("			<key>UISupportedInterfaceOrientations~ipad</key>\n")
		tmpFile.write("			<array>\n")
		tmpFile.write("				<string>UIInterfaceOrientationPortrait</string>\n")
		tmpFile.write("				<string>UIInterfaceOrientationPortraitUpsideDown</string>\n")
		tmpFile.write("				<string>UIInterfaceOrientationLandscapeLeft</string>\n")
		tmpFile.write("				<string>UIInterfaceOrientationLandscapeRight</string>\n")
		tmpFile.write("			</array>\n")
		tmpFile.write("    </dict>\n")
		tmpFile.write("</plist>\n")
		tmpFile.write("\n\n")
		tmpFile.flush()
		tmpFile.close()
		"""
		builtin-infoPlistUtility
			/Users/edouarddupin/dev/exampleProjectXcode/projectName/projectName/projectName-Info.plist
			-genpkginfo
			/Users/edouarddupin/Library/Developer/Xcode/DerivedData/projectName-gwycnyyzohokcmalgodeucqppxro/Build/Products/Debug-iphonesimulator/projectName.app/PkgInfo
			-expandbuildsettings
			-format binary
			-platform iphonesimulator
		    -additionalcontentfile /Users/edouarddupin/Library/Developer/Xcode/DerivedData/projectName-gwycnyyzohokcmalgodeucqppxro/Build/Intermediates/projectName.build/Debug-iphonesimulator/projectName.build/assetcatalog_generated_info.plist
			-o /Users/edouarddupin/Library/Developer/Xcode/DerivedData/projectName-gwycnyyzohokcmalgodeucqppxro/Build/Products/Debug-iphonesimulator/projectName.app/Info.plist
		"""
		#/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/dsymutil /Users/edouarddupin/Library/Developer/Xcode/DerivedData/projectName-gwycnyyzohokcmalgodeucqppxro/Build/Products/Debug-iphonesimulator/projectName.app/projectName -o /Users/edouarddupin/Library/Developer/Xcode/DerivedData/projectName-gwycnyyzohokcmalgodeucqppxro/Build/Products/Debug-iphonesimulator/projectName.app.dSYM

		infoFile=self.get_staging_folder(pkgName) + "/PkgInfo"
		# Create the info file
		tmpFile = open(infoFile, 'w')
		tmpFile.write("APPL????")
		tmpFile.flush()
		tmpFile.close()
		# Simulateur folder :
		#~/Library/Application\ Support/iPhone\ Simulator/7.0.3/Applications/
		# must have a 'uuidgen' UID generate value with this elemennt ...
		# get the bundle path : ==> maybe usefull in MocOS ...
		# NSLog(@"%@",[[NSBundle mainBundle] bundlePath]);
		
		# Must create the tarball of the application 
		#cd $(TARGET_OUT_FINAL)/; tar -cf $(PROJECT_NAME).tar $(PROJECT_NAME).app
		#cd $(TARGET_OUT_FINAL)/; tar -czf $(PROJECT_NAME).tar.gz $(PROJECT_NAME).app
	
	def createRandomNumber(self, len):
		out = ""
		for iii in range(0,len):
			out += random.choice(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"])
		return out
	
	def install_package(self, pkgName):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Install package '" + pkgName + "'")
		debug.debug("------------------------------------------------------------------------")
		simulatorIdFile = ".iosSimutatorId_" + pkgName + ".txt"
		if lutinTools.file_size(simulatorIdFile) < 10:
			#create the file:
			tmpFile = open(simulatorIdFile, 'w')
			tmpFile.write(self.createRandomNumber(8))
			tmpFile.write("-")
			tmpFile.write(self.createRandomNumber(4))
			tmpFile.write("-")
			tmpFile.write(self.createRandomNumber(4))
			tmpFile.write("-")
			tmpFile.write(self.createRandomNumber(4))
			tmpFile.write("-")
			tmpFile.write(self.createRandomNumber(12))
			tmpFile.flush()
			tmpFile.close()
		simulatorId = lutinTools.file_read_data(simulatorIdFile)
		home = os.path.expanduser("~")
		destinationFolder = home + "/Library/Application Support/iPhone Simulator/7.0.3/Applications/" + simulatorId + "/" + pkgName + ".app"
		destinationFolder2 = home + "/Library/Application\\ Support/iPhone\\ Simulator/7.0.3/Applications/" + simulatorId + "/" + pkgName + ".app"
		debug.info("install in simulator : " + destinationFolder)
		lutinTools.create_directory_of_file(destinationFolder + "/plop.txt")
		cmdLine = "cp -rf " + self.get_staging_folder(pkgName) + " " + destinationFolder2
		lutinMultiprocess.run_command(cmdLine)
		#sudo dpkg -i $(TARGET_OUT_FINAL)/$(PROJECT_NAME) + self.suffix_package
	
	def un_install_package(self, pkgName):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Un-Install package '" + pkgName + "'")
		debug.debug("------------------------------------------------------------------------")
		simulatorIdFile = ".iosSimutatorId_" + pkgName + ".txt"
		if lutinTools.file_size(simulatorIdFile) < 10:
			debug.warning("Can not get simulation O_ID : " + simulatorIdFile)
		
		#sudo dpkg -r $(TARGET_OUT_FINAL)/$(PROJECT_NAME) + self.suffix_package
		
	def Log(self, pkgName):
		debug.debug("------------------------------------------------------------------------")
		debug.info("log of iOs board")
		debug.debug("------------------------------------------------------------------------")
		cmdLine = "tail -f ~/Library/Logs/iOS\ Simulator/7.0.3/system.log"
		lutinMultiprocess.run_command(cmdLine)




