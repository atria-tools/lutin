#!/usr/bin/python
# -*- coding: utf-8 -*-
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
import os
import stat
from lutin import multiprocess
from lutin import host
import random
import re

class Target(target.Target):
	def __init__(self, config):
		if config["compilator"] == "gcc":
			debug.info("compile only with clang for IOs");
			config["compilator"] = "clang"
		#processor type selection (auto/arm/ppc/x86)
		if config["arch"] == "auto":
			config["arch"] = "arm"
		#bus size selection (auto/32/64)
		if config["bus-size"] == "auto":
			config["bus-size"] = "64"
		
		# http://biolpc22.york.ac.uk/pub/linux-mac-cross/
		# http://devs.openttd.org/~truebrain/compile-farm/apple-darwin9.txt
		if config["simulation"] == True:
			arch = "i386"
		else:
			arch="arm64" # for ipad air
			#arch="armv7" # for Iphone 4
		target.Target.__init__(self, "IOs", config, arch)
		if self.config["simulation"] == True:
			self.set_cross_base("/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/")
		else:
			self.set_cross_base("/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/")
		
		# remove unneeded ranlib ...
		self.ranlib=""
		#self.path_bin=""
		#self.path_data="share"
		#self.path_doc="doc"
		
		self.suffix_lib_static='.a'
		self.suffix_lib_dynamic='.dylib'
		#self.suffix_binary=''
		#self.suffix_package=''
		
		if False: #self.simulator == True:
			self.sysroot = "-isysroot /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator.sdk"
			self.add_flag("link", "-mios-simulator-version-min=8.0")
			self.add_flag("c", "-mios-simulator-version-min=8.0")
		else:
			self.sysroot = "-isysroot /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS.sdk"
			self.add_flag("link", "-miphoneos-version-min=8.0")
			self.add_flag("c", "-miphoneos-version-min=8.0")
		
		self.add_flag("link", [
		    "-Xlinker",
		    "-objc_abi_version",
		    "-Xlinker 2",
		    "-Xlinker",
		    "-no_implicit_dylibs",
		    "-stdlib=libc++",
		    "-fobjc-arc",
		    "-fobjc-link-runtime"
		    ])
		
		self.add_flag("m", ["-fobjc-arc"])
		#self.add_flag("m", ["-fmodules"])
		
		self.pkg_path_data = "share"
		self.pkg_path_bin = ""
		self.pkg_path_lib = "lib"
		self.pkg_path_license = "license"
		
		# Disable capabiliteis to compile in shared mode
		self.support_dynamic_link = False
	
	def make_package_binary(self, pkg_name, pkg_properties, base_pkg_path, heritage_list, static):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Generate package '" + pkg_name + "' v" + tools.version_to_string(pkg_properties["VERSION"]))
		debug.debug("------------------------------------------------------------------------")
		#output path
		target_outpath = os.path.join(self.get_staging_path(pkg_name), pkg_name + ".app")
		tools.create_directory_of_file(target_outpath)
		
		## Create share datas:
		self.make_package_binary_data(target_outpath, pkg_name, base_pkg_path, heritage_list, static)
		
		## copy binary files:
		self.make_package_binary_bin(target_outpath, pkg_name, base_pkg_path, heritage_list, static)
		
		## Create libraries:
		self.make_package_binary_lib(target_outpath, pkg_name, base_pkg_path, heritage_list, static)
		
		## Create generic files:
		self.make_package_generic_files(target_outpath, pkg_properties, pkg_name, base_pkg_path, heritage_list, static)
		
		## Create icon:
		if    "ICON" in pkg_properties.keys() \
		   and pkg_properties["ICON"] != "":
			# Resize all icon needed for Ios ...
			# TODO : Do not regenerate if source resource is not availlable
			# TODO : Add a colored background ...
			debug.print_element("pkg", os.path.relpath(pkg_properties["ICON"]), "==>", "iTunesArtwork.png")
			image.resize(pkg_properties["ICON"], os.path.join(target_outpath, "iTunesArtwork.png"), 512, 512)
			debug.print_element("pkg", os.path.relpath(pkg_properties["ICON"]), "==>", "iTunesArtwork@2x.png")
			image.resize(pkg_properties["ICON"], os.path.join(target_outpath, "iTunesArtwork@2x.png"), 1024, 1024)
			debug.print_element("pkg", os.path.relpath(pkg_properties["ICON"]), "==>", "Icon-60@2x.png")
			image.resize(pkg_properties["ICON"], os.path.join(target_outpath, "Icon-60@2x.png"), 120, 120)
			debug.print_element("pkg", os.path.relpath(pkg_properties["ICON"]), "==>", "Icon-76.png")
			image.resize(pkg_properties["ICON"], os.path.join(target_outpath, "Icon-76.png"), 76, 76)
			debug.print_element("pkg", os.path.relpath(pkg_properties["ICON"]), "==>", "Icon-76@2x.png")
			image.resize(pkg_properties["ICON"], os.path.join(target_outpath, "Icon-76@2x.png"), 152, 152)
			debug.print_element("pkg", os.path.relpath(pkg_properties["ICON"]), "==>", "Icon-Small-40.png")
			image.resize(pkg_properties["ICON"], os.path.join(target_outpath, "Icon-Small-40.png"), 40, 40)
			debug.print_element("pkg", os.path.relpath(pkg_properties["ICON"]), "==>", "Icon-Small-40@2x.png")
			image.resize(pkg_properties["ICON"], os.path.join(target_outpath, "Icon-Small-40@2x.png"), 80, 80)
			debug.print_element("pkg", os.path.relpath(pkg_properties["ICON"]), "==>", "Icon-Small.png")
			image.resize(pkg_properties["ICON"], os.path.join(target_outpath, "Icon-Small.png"), 29, 29)
			debug.print_element("pkg", os.path.relpath(pkg_properties["ICON"]), "==>", "Icon-Small@2x.png")
			image.resize(pkg_properties["ICON"], os.path.join(target_outpath, "Icon-Small@2x.png"), 58, 58)
		
		## Create the info file:
		debug.print_element("pkg", "PkgInfo", "<==", "APPL????")
		tools.file_write_data(os.path.join(target_outpath, "PkgInfo"),
		                      "APPL????",
		                      only_if_new=True)
		
		## Create Info.plist (in XML mode)
		debug.print_element("pkg", "Info.plist", "<==", "Package properties")
		# http://www.sandroid.org/imcross/#Deployment
		data_file  = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
		data_file += "<!DOCTYPE plist PUBLIC \"-//Apple Computer//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n"
		data_file += "<plist version=\"1.0\">\n"
		data_file += "		<dict>\n"
		data_file += "			<key>CFBundleDevelopmentRegion</key>\n"
		data_file += "			<string>en</string>\n"
		data_file += "			<key>CFBundleDisplayName</key>\n"
		data_file += "			<string>" + pkg_properties["NAME"] + "</string>\n"
		data_file += "			<key>CFBundleExecutable</key>\n"
		data_file += "			<string>" + pkg_name + "</string>\n"
		data_file += "			<key>CFBundleIdentifier</key>\n"
		data_file += "			<string>com." + pkg_properties["COMPAGNY_NAME2"] + "." + pkg_name + "</string>\n"
		
		data_file += "			<key>CFBundleIconFiles</key>\n"
		data_file += "			<array>\n"
		data_file += "				<string>Icon-60@2x.png</string>\n"
		data_file += "				<string>Icon-76.png</string>\n"
		data_file += "				<string>Icon-76@2x.png</string>\n"
		data_file += "				<string>Icon-Small-40.png</string>\n"
		data_file += "				<string>Icon-Small-40@2x.png</string>\n"
		data_file += "				<string>Icon-Small.png</string>\n"
		data_file += "				<string>Icon-Small@2x.png</string>\n"
		data_file += "				<string>iTunesArtwork.png</string>\n"
		data_file += "				<string>iTunesArtwork@2x.png</string>\n"
		data_file += "			</array>\n"
		
		data_file += "			<key>CFBundleInfoDictionaryVersion</key>\n"
		data_file += "			<string>6.0</string>\n"
		data_file += "			<key>CFBundleName</key>\n"
		data_file += "			<string>" + pkg_name + "</string>\n"
		data_file += "			<key>CFBundlePackageType</key>\n"
		data_file += "			<string>APPL</string>\n"
		data_file += "			<key>CFBundleSignature</key>\n"
		data_file += "			<string>????</string>\n"
		data_file += "			<key>CFBundleSupportedPlatforms</key>\n"
		data_file += "			<array>\n"
		data_file += "				<string>iPhoneSimulator</string>\n"
		data_file += "			</array>\n"
		data_file += "			\n"
		data_file += "			<key>CFBundleShortVersionString</key>\n"
		data_file += "			<string>"+tools.version_to_string(pkg_properties["VERSION"])+"</string>\n"
		data_file += "			<key>CFBundleVersion</key>\n"
		data_file += "			<string>"+str(pkg_properties["VERSION_CODE"])+"</string>\n"
		data_file += "			\n"
		data_file += "			<key>CFBundleResourceSpecification</key>\n"
		data_file += "			<string>ResourceRules.plist</string>\n"
		if self.sumulator == False:
			data_file += "			<key>LSRequiresIPhoneOS</key>\n"
			data_file += "			<true/>\n"
		else:
			data_file += "			<key>DTPlatformName</key>\n"
			data_file += "			<string>iphonesimulator</string>\n"
			data_file += "			<key>DTSDKName</key>\n"
			data_file += "			<string>iphonesimulator7.0</string>\n"
		data_file += "			\n"
		data_file += "			<key>UIDeviceFamily</key>\n"
		data_file += "			<array>\n"
		data_file += "				<integer>1</integer>\n"
		data_file += "				<integer>2</integer>\n"
		data_file += "			</array>\n"
		data_file += "			<key>UIRequiredDeviceCapabilities</key>\n"
		data_file += "			<array>\n"
		data_file += "				<string>armv7</string>\n"
		data_file += "			</array>\n"
		data_file += "			<key>UIStatusBarHidden</key>\n"
		data_file += "			<true/>\n"
		data_file += "			<key>UISupportedInterfaceOrientations</key>\n"
		data_file += "			<array>\n"
		data_file += "				<string>UIInterfaceOrientationPortrait</string>\n"
		data_file += "				<string>UIInterfaceOrientationPortraitUpsideDown</string>\n"
		data_file += "				<string>UIInterfaceOrientationLandscapeLeft</string>\n"
		data_file += "				<string>UIInterfaceOrientationLandscapeRight</string>\n"
		data_file += "			</array>\n"
		data_file += "			<key>UISupportedInterfaceOrientations~ipad</key>\n"
		data_file += "			<array>\n"
		data_file += "				<string>UIInterfaceOrientationPortrait</string>\n"
		data_file += "				<string>UIInterfaceOrientationPortraitUpsideDown</string>\n"
		data_file += "				<string>UIInterfaceOrientationLandscapeLeft</string>\n"
		data_file += "				<string>UIInterfaceOrientationLandscapeRight</string>\n"
		data_file += "			</array>\n"
		data_file += "    </dict>\n"
		data_file += "</plist>\n"
		data_file += "\n\n"
		tools.file_write_data(os.path.join(target_outpath, "Info.plist"),
		                      data_file,
		                      only_if_new=True)
		
		"""
		infoFile = self.get_staging_path(pkg_name) + "/" + pkg_name + "-Info.plist"
		# Create the info file
		tmpFile = open(infoFile, 'w')
		tmpFile.write(data_file)
		tmpFile.flush()
		tmpFile.close()
		cmdLine  = "builtin-infoPlistUtility "
		cmdLine += " " + self.get_staging_path(pkg_name) + "/" + pkg_name + "-Info.plist "
		cmdLine += " -genpkginfo " + self.get_staging_path(pkg_name) + "/PkgInfo"
		cmdLine += " -expandbuildsettings "
		cmdLine += " -format binary "
		if self.sumulator == False:
			cmdLine += " -platform iphonesimulator "
		else:
			cmdLine += " -platform iphoneos "
		cmdLine += " -o " + self.get_staging_path(pkg_name) + "/" + "Info.plist"
		multiprocess.run_command(cmdLine)
		"""
		"""
		
			/Users/edouarddupin/dev/exampleProjectXcode/projectName/projectName/projectName-Info.plist
			-genpkginfo
			/Users/edouarddupin/Library/Developer/Xcode/DerivedData/projectName-gwycnyyzohokcmalgodeucqppxro/Build/Products/Debug-iphonesimulator/projectName.app/PkgInfo
			-expandbuildsettings
			-format binary
			-platform iphonesimulator
		    -additionalcontentfile /Users/edouarddupin/Library/Developer/Xcode/DerivedData/projectName-gwycnyyzohokcmalgodeucqppxro/Build/Intermediates/projectName.build/Debug-iphonesimulator/projectName.build/assetcatalog_generated_info.plist
			-o /Users/edouarddupin/Library/Developer/Xcode/DerivedData/projectName-gwycnyyzohokcmalgodeucqppxro/Build/Products/Debug-iphonesimulator/projectName.app/Info.plist
		 -additionalcontentfile /Users/edouarddupin/Library/Developer/Xcode/DerivedData/zdzdzd-bjuyukzpzhnyerdmxohjyuxfdllv/Build/Intermediates/zdzdzd.build/Debug-iphoneos/zdzdzd.build/assetcatalog_generated_info.plist -o /Users/edouarddupin/Library/Developer/Xcode/DerivedData/zdzdzd-bjuyukzpzhnyerdmxohjyuxfdllv/Build/Products/Debug-iphoneos/zdzdzd.app/Info.plist
			
			"""
		#/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/dsymutil /Users/edouarddupin/Library/Developer/Xcode/DerivedData/projectName-gwycnyyzohokcmalgodeucqppxro/Build/Products/Debug-iphonesimulator/projectName.app/projectName -o /Users/edouarddupin/Library/Developer/Xcode/DerivedData/projectName-gwycnyyzohokcmalgodeucqppxro/Build/Products/Debug-iphonesimulator/projectName.app.dSYM
			
		debug.print_element("pkg", "ResourceRules.plist", "<==", "Resources autorisation")
		data_file  = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
		data_file += "<!DOCTYPE plist PUBLIC \"-//Apple Computer//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n"
		data_file += "<plist version=\"1.0\">\n"
		data_file += "	<dict>\n"
		data_file += "		<key>rules</key>\n"
		data_file += "		<dict>\n"
		data_file += "			<key>.*</key>\n"
		data_file += "			<true/>\n"
		data_file += "			<key>Info.plist</key>\n"
		data_file += "			<dict>\n"
		data_file += "				<key>omit</key>\n"
		data_file += "				<true/>\n"
		data_file += "				<key>weight</key>\n"
		data_file += "				<real>10</real>\n"
		data_file += "			</dict>\n"
		data_file += "			<key>ResourceRules.plist</key>\n"
		data_file += "			<dict>\n"
		data_file += "				<key>omit</key>\n"
		data_file += "				<true/>\n"
		data_file += "				<key>weight</key>\n"
		data_file += "				<real>100</real>\n"
		data_file += "			</dict>\n"
		data_file += "		</dict>\n"
		data_file += "	</dict>\n"
		data_file += "</plist>\n"
		data_file += "\n\n"
		tools.file_write_data(os.path.join(target_outpath, "ResourceRules.plist"),
		                      data_file,
		                      only_if_new=True)

		debug.print_element("pkg", "Entitlements.plist", "<==", "application mode")
		data_file  = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
		data_file += "<!DOCTYPE plist PUBLIC \"-//Apple Computer//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n"
		data_file += "<plist version=\"1.0\">\n"
		data_file += "	<dict>\n"
		data_file += "		<key>get-task-allow</key>\n"
		data_file += "		<true/>\n"
		data_file += "    </dict>\n"
		data_file += "</plist>\n"
		data_file += "\n\n"
		tools.file_write_data(os.path.join(target_outpath, "Entitlements.plist"),
		                      data_file,
		                      only_if_new=True)

		# Simulateur path :
		#~/Library/Application\ Support/iPhone\ Simulator/7.0.3/Applications/
		# must have a 'uuidgen' UID generate value with this elemennt ...
		# get the bundle path : ==> maybe usefull in MocOS ...
		# NSLog(@"%@",[[NSBundle mainBundle] bundlePath]);
		
		# Must create the tarball of the application 
		#cd $(TARGET_OUT_FINAL)/; tar -cf $(PROJECT_NAME).tar $(PROJECT_NAME).app
		#cd $(TARGET_OUT_FINAL)/; tar -czf $(PROJECT_NAME).tar.gz $(PROJECT_NAME).app
		if self.sumulator == False:
			if "APPLE_APPLICATION_IOS_ID" not in pkg_properties:
				pkg_properties["APPLE_APPLICATION_IOS_ID"] = "00000000"
				debug.warning("Missing package property : APPLE_APPLICATION_IOS_ID USE " + pkg_properties["APPLE_APPLICATION_IOS_ID"] + " ID ... ==> CAN NOT WORK ..." )
			# Create the info file
			tmpFile = open(os.path.join(target_outpath, pkg_name + ".xcent"), 'w')
			tmpFile.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
			tmpFile.write("<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n")
			tmpFile.write("<plist version=\"1.0\">\n")
			tmpFile.write("    <dict>\n")
			tmpFile.write("        <key>application-identifier</key>\n")
			tmpFile.write("        <string>" + pkg_properties["APPLE_APPLICATION_IOS_ID"] + "." + pkg_properties["COMPAGNY_TYPE"] + "." + pkg_properties["COMPAGNY_NAME2"] + "." + pkg_name + "</string>\n")
			tmpFile.write("        <key>get-task-allow</key>\n")
			tmpFile.write("        <true/>\n")
			tmpFile.write("        <key>keychain-access-groups</key>\n")
			tmpFile.write("        <array>\n")
			tmpFile.write("            <string>" + pkg_properties["APPLE_APPLICATION_IOS_ID"] + "." + pkg_properties["COMPAGNY_TYPE"] + "." + pkg_properties["COMPAGNY_NAME2"] + "." + pkg_name + "</string>\n")
			tmpFile.write("        </array>\n")
			tmpFile.write("    </dict>\n")
			tmpFile.write("</plist>\n")
			tmpFile.flush()
			tmpFile.close()
			# application signing :
			debug.print_element("pkg(signed)", "pkg", "<==", "Signing application")
			iosDevelopperKeyFile = ".iosKey.txt"
			if tools.file_size(iosDevelopperKeyFile) < 10:
				debug.warning("To sign an application we need to have a signing key in the file '" + iosDevelopperKeyFile + "' \n it is represented like: 'iPhone Developer: Francis DUGENOUX (YRRQE5KGTH)'\n you can obtain it with : 'certtool y | grep \"Developer\"'")
				debug.warning("Can not be install ... not runnable")
			else:
				signatureKey = tools.file_read_data(iosDevelopperKeyFile)
				signatureKey = re.sub('\n', '', signatureKey)
				cmdLine  = 'codesign --force --sign '
				# to get this key ; certtool y | grep "Developer"
				cmdLine += ' "' + signatureKey + '" '
				cmdLine += ' --entitlements ' + self.get_build_path(pkg_name) + '/worddown.xcent'
				cmdLine += ' ' + self.get_staging_path(pkg_name)
				multiprocess.run_command(cmdLine)
	
	def create_random_number(self, len):
		out = ""
		for iii in range(0,len):
			out += random.choice(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"])
		return out
	
	def install_package(self, pkg_name):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Install package '" + pkg_name + "'")
		debug.debug("------------------------------------------------------------------------")
		if self.sumulator == False:
			if tools.file_size("ewol/ios-deploy/ios-deploy") == 0:
				debug.print_element("tool", "ios-deploy", "<==", "external sources")
				cmdLine = 'cd ewol/ios-deploy ; make ; cd ../.. '
				multiprocess.run_command(cmdLine)
			if tools.file_size("ewol/ios-deploy/ios-deploy") == 0:
				debug.error("Can not create ios-deploy external software ...")
			debug.print_element("deploy", "iphone/ipad", "<==", "aplication")
			cmdLine = './ewol/ios-deploy/ios-deploy --bundle ' + self.get_staging_path(pkg_name)
			multiprocess.run_command(cmdLine)
		else:
			simulatorIdFile = ".iosSimutatorId_" + pkg_name + ".txt"
			if tools.file_size(simulatorIdFile) < 10:
				#create the file:
				tmpFile = open(simulatorIdFile, 'w')
				tmpFile.write(self.create_random_number(8))
				tmpFile.write("-")
				tmpFile.write(self.create_random_number(4))
				tmpFile.write("-")
				tmpFile.write(self.create_random_number(4))
				tmpFile.write("-")
				tmpFile.write(self.create_random_number(4))
				tmpFile.write("-")
				tmpFile.write(self.create_random_number(12))
				tmpFile.flush()
				tmpFile.close()
			simulatorId = tools.file_read_data(simulatorIdFile)
			home = os.path.expanduser("~")
			destinationpathBase = home + "/Library/Application\\ Support/iPhone\\ Simulator/7.1/Applications/" + simulatorId
			destinationpath = home + "/Library/Application Support/iPhone Simulator/7.1/Applications/" + simulatorId + "/" + pkg_name + ".app"
			destinationpath2 = home + "/Library/Application\\ Support/iPhone\\ Simulator/7.1/Applications/" + simulatorId + "/" + pkg_name + ".app"
			debug.info("install in simulator : " + destinationpath)
			tools.create_directory_of_file(destinationpath + "/plop.txt")
			cmdLine = "cp -rf " + self.get_staging_path(pkg_name) + " " + destinationpath2
			multiprocess.run_command(cmdLine)
			cmdLine = "touch " + destinationpathBase
			multiprocess.run_command(cmdLine)
			
		#sudo dpkg -i $(TARGET_OUT_FINAL)/$(PROJECT_NAME) + self.suffix_package
	
	def un_install_package(self, pkg_name):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Un-Install package '" + pkg_name + "'")
		debug.debug("------------------------------------------------------------------------")
		if self.sumulator == False:
			debug.warning("not implemented")
		else:
			simulatorIdFile = ".iosSimutatorId_" + pkg_name + ".txt"
			if tools.file_size(simulatorIdFile) < 10:
				debug.warning("Can not get simulation O_ID : " + simulatorIdFile)
		
		#sudo dpkg -r $(TARGET_OUT_FINAL)/$(PROJECT_NAME) + self.suffix_package
		
	def Log(self, pkg_name):
		debug.debug("------------------------------------------------------------------------")
		debug.info("log of iOs board")
		debug.debug("------------------------------------------------------------------------")
		if self.sumulator == False:
			if tools.file_size("ewol/ios-deploy/ios-deploy") == 0:
				debug.print_element("tool", "ios-deploy", "<==", "external sources")
				cmdLine = 'cd ewol/ios-deploy ; make ; cd ../.. '
				multiprocess.run_command(cmdLine)
			if tools.file_size("ewol/ios-deploy/ios-deploy") == 0:
				debug.error("Can not create ios-deploy external software ...")
			debug.print_element("deploy", "iphone/ipad", "<==", "aplication")
			cmdLine = './ewol/ios-deploy/ios-deploy --debug --bundle ' + self.get_staging_path(pkg_name)
			multiprocess.run_command(cmdLine)
		else:
			cmdLine = "tail -f ~/Library/Logs/iOS\ Simulator/7.1/system.log"
			multiprocess.run_command(cmdLine)




