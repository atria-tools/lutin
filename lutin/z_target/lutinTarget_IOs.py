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
		
		if self.sumulator == True:
			self.sysroot = "-isysroot /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator.sdk"
			self.global_flags_ld.append("-mios-simulator-version-min=8.0")
			self.global_flags_cc.append("-mios-simulator-version-min=8.0")
		else:
			self.sysroot = "-isysroot /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS.sdk"
			self.global_flags_ld.append("-miphoneos-version-min=8.0")
			self.global_flags_cc.append("-miphoneos-version-min=8.0")
		
		self.global_flags_cc.append("-D__STDCPP_LLVM__")
		self.global_flags_ld.append([
			"-Xlinker",
			"-objc_abi_version",
			"-Xlinker 2",
			"-Xlinker",
			"-no_implicit_dylibs",
			"-stdlib=libc++",
			"-fobjc-arc",
			"-fobjc-link-runtime"])
		
		self.global_flags_m.append("-fobjc-arc")
		#self.global_flags_m.append("-fmodules")
		
		self.pkg_path_data = "share"
		self.pkg_path_bin = ""
		self.pkg_path_lib = "lib"
		self.pkg_path_license = "license"
		
	
	def make_package(self, pkg_name, pkg_properties, base_pkg_path, heritage_list):
		#The package generated depend of the type of the element:
		end_point_module_name = heritage_list.list_heritage[-1].name
		module = self.get_module(end_point_module_name)
		if module == None:
			debug.error("can not create package ... ");
		if module.get_type() == 'PREBUILD':
			#nothing to do ...
			return
		if    module.get_type() == 'LIBRARY' \
		   or module.get_type() == 'LIBRARY_DYNAMIC' \
		   or module.get_type() == 'LIBRARY_STATIC':
			debug.info("Can not create package for library");
			return
		if    module.get_type() == 'BINARY' \
		   or module.get_type() == 'BINARY_STAND_ALONE':
			self.make_package_binary(pkg_name, pkg_properties, base_pkg_path, heritage_list, static = True)
		if module.get_type() == 'BINARY_SHARED':
			self.make_package_binary(pkg_name, pkg_properties, base_pkg_path, heritage_list, static = False)
		if module.get_type() == 'PACKAGE':
			debug.info("Can not create package for package");
	
	
	def make_package_binary(self, pkg_name, pkg_properties, base_pkg_path, heritage_list, static):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Generate package '" + pkg_name + "'")
		debug.debug("------------------------------------------------------------------------")
		#output path
		target_outpath = os.path.join(self.get_staging_path(pkg_name), pkg_name + ".app")
		tools.create_directory_of_file(target_outpath)
		
		## Create share datas:
		if static == True:
			target_outpath_data = os.path.join(target_outpath, self.pkg_path_data, pkg_name)
		else:
			target_outpath_data = os.path.join(target_outpath, self.pkg_path_data)
		tools.create_directory_of_file(target_outpath_data)
		debug.debug("heritage for " + str(pkg_name) + ":")
		for heritage in heritage_list.list_heritage:
			debug.debug("sub elements: " + str(heritage.name))
			path_src = self.get_build_path_data(heritage.name)
			debug.verbose("      has directory: " + path_src)
			if os.path.isdir(path_src):
				if static == True:
					debug.debug("      need copy: " + path_src + " to " + target_outpath_data)
					#copy all data:
					tools.copy_anything(path_src, target_outpath_data, recursive=True, force_identical=True)
				else:
					debug.debug("      need copy: " + os.path.dirname(path_src) + " to " + target_outpath_data)
					#copy all data:
					tools.copy_anything(os.path.dirname(path_src), target_outpath_data, recursive=True, force_identical=True)
		
		## copy binary files:
		target_outpath_bin = os.path.join(target_outpath, self.pkg_path_bin)
		tools.create_directory_of_file(target_outpath_bin)
		path_src = self.get_build_file_bin(pkg_name)
		path_dst = os.path.join(target_outpath_bin, pkg_name + self.suffix_binary)
		debug.verbose("path_dst: " + str(path_dst))
		tools.copy_file(path_src, path_dst)
		
		## Create libraries:
		if static == False:
			#copy all shred libs...
			target_outpath_lib = os.path.join(target_outpath, self.pkg_path_lib)
			tools.create_directory_of_file(target_outpath_lib)
			debug.verbose("libs for " + str(pkg_name) + ":")
			for heritage in heritage_list.list_heritage:
				debug.debug("sub elements: " + str(heritage.name))
				file_src = self.get_build_file_dynamic(heritage.name)
				debug.verbose("      has directory: " + file_src)
				if os.path.isfile(file_src):
					debug.debug("      need copy: " + file_src + " to " + target_outpath_lib)
					#copy all data:
					# TODO : We can have a problem when writing over library files ...
					tools.copy_file(file_src, os.path.join(target_outpath_lib, os.path.basename(file_src)) )
		
		## Create icon:
		if    "ICON" in pkg_properties.keys() \
		   and pkg_properties["ICON"] != "":
			# Resize all icon needed for Ios ...
			# TODO : Do not regenerate if source resource is not availlable
			# TODO : Add a colored background ...
			debug.print_element("pkg", "iTunesArtwork.png", "<==", pkg_properties["ICON"])
			image.resize(pkg_properties["ICON"], os.path.join(target_outpath, "iTunesArtwork.png"), 512, 512)
			debug.print_element("pkg", "iTunesArtwork@2x.png", "<==", pkg_properties["ICON"])
			image.resize(pkg_properties["ICON"], os.path.join(target_outpath, "iTunesArtwork@2x.png"), 1024, 1024)
			debug.print_element("pkg", "Icon-60@2x.png", "<==", pkg_properties["ICON"])
			image.resize(pkg_properties["ICON"], os.path.join(target_outpath, "Icon-60@2x.png"), 120, 120)
			debug.print_element("pkg", "Icon-76.png", "<==", pkg_properties["ICON"])
			image.resize(pkg_properties["ICON"], os.path.join(target_outpath, "Icon-76.png"), 76, 76)
			debug.print_element("pkg", "Icon-76@2x.png", "<==", pkg_properties["ICON"])
			image.resize(pkg_properties["ICON"], os.path.join(target_outpath, "Icon-76@2x.png"), 152, 152)
			debug.print_element("pkg", "Icon-Small-40.png", "<==", pkg_properties["ICON"])
			image.resize(pkg_properties["ICON"], os.path.join(target_outpath, "Icon-Small-40.png"), 40, 40)
			debug.print_element("pkg", "Icon-Small-40@2x.png", "<==", pkg_properties["ICON"])
			image.resize(pkg_properties["ICON"], os.path.join(target_outpath, "Icon-Small-40@2x.png"), 80, 80)
			debug.print_element("pkg", "Icon-Small.png", "<==", pkg_properties["ICON"])
			image.resize(pkg_properties["ICON"], os.path.join(target_outpath, "Icon-Small.png"), 29, 29)
			debug.print_element("pkg", "Icon-Small@2x.png", "<==", pkg_properties["ICON"])
			image.resize(pkg_properties["ICON"], os.path.join(target_outpath, "Icon-Small@2x.png"), 58, 58)
		
		debug.print_element("pkg", "PkgInfo", "<==", "APPL????")
		infoFile = os.path.join(target_outpath, "PkgInfo")
		# Create the info file
		tmpFile = open(infoFile, 'w')
		tmpFile.write("APPL????")
		tmpFile.flush()
		tmpFile.close()
		
		debug.print_element("pkg", "Info.plist", "<==", "Package properties")
		# http://www.sandroid.org/imcross/#Deployment
		dataFile  = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
		dataFile += "<!DOCTYPE plist PUBLIC \"-//Apple Computer//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n"
		dataFile += "<plist version=\"1.0\">\n"
		dataFile += "		<dict>\n"
		dataFile += "			<key>CFBundleDevelopmentRegion</key>\n"
		dataFile += "			<string>en</string>\n"
		dataFile += "			<key>CFBundleDisplayName</key>\n"
		dataFile += "			<string>" + pkg_properties["NAME"] + "</string>\n"
		dataFile += "			<key>CFBundleExecutable</key>\n"
		dataFile += "			<string>" + pkg_name + "</string>\n"
		dataFile += "			<key>CFBundleIdentifier</key>\n"
		dataFile += "			<string>com." + pkg_properties["COMPAGNY_NAME2"] + "." + pkg_name + "</string>\n"
		
		dataFile += "			<key>CFBundleIconFiles</key>\n"
		dataFile += "			<array>\n"
		dataFile += "				<string>Icon-60@2x.png</string>\n"
		dataFile += "				<string>Icon-76.png</string>\n"
		dataFile += "				<string>Icon-76@2x.png</string>\n"
		dataFile += "				<string>Icon-Small-40.png</string>\n"
		dataFile += "				<string>Icon-Small-40@2x.png</string>\n"
		dataFile += "				<string>Icon-Small.png</string>\n"
		dataFile += "				<string>Icon-Small@2x.png</string>\n"
		dataFile += "				<string>iTunesArtwork.png</string>\n"
		dataFile += "				<string>iTunesArtwork@2x.png</string>\n"
		dataFile += "			</array>\n"
		
		dataFile += "			<key>CFBundleInfoDictionaryVersion</key>\n"
		dataFile += "			<string>6.0</string>\n"
		dataFile += "			<key>CFBundleName</key>\n"
		dataFile += "			<string>" + pkg_name + "</string>\n"
		dataFile += "			<key>CFBundlePackageType</key>\n"
		dataFile += "			<string>APPL</string>\n"
		dataFile += "			<key>CFBundleSignature</key>\n"
		dataFile += "			<string>????</string>\n"
		dataFile += "			<key>CFBundleSupportedPlatforms</key>\n"
		dataFile += "			<array>\n"
		dataFile += "				<string>iPhoneSimulator</string>\n"
		dataFile += "			</array>\n"
		dataFile += "			\n"
		dataFile += "			<key>CFBundleShortVersionString</key>\n"
		dataFile += "			<string>"+pkg_properties["VERSION"]+"</string>\n"
		dataFile += "			<key>CFBundleVersion</key>\n"
		dataFile += "			<string>"+pkg_properties["VERSION_CODE"]+"</string>\n"
		dataFile += "			\n"
		dataFile += "			<key>CFBundleResourceSpecification</key>\n"
		dataFile += "			<string>ResourceRules.plist</string>\n"
		if self.sumulator == False:
			dataFile += "			<key>LSRequiresIPhoneOS</key>\n"
			dataFile += "			<true/>\n"
		else:
			dataFile += "			<key>DTPlatformName</key>\n"
			dataFile += "			<string>iphonesimulator</string>\n"
			dataFile += "			<key>DTSDKName</key>\n"
			dataFile += "			<string>iphonesimulator7.0</string>\n"
		dataFile += "			\n"
		dataFile += "			<key>UIDeviceFamily</key>\n"
		dataFile += "			<array>\n"
		dataFile += "				<integer>1</integer>\n"
		dataFile += "				<integer>2</integer>\n"
		dataFile += "			</array>\n"
		dataFile += "			<key>UIRequiredDeviceCapabilities</key>\n"
		dataFile += "			<array>\n"
		dataFile += "				<string>armv7</string>\n"
		dataFile += "			</array>\n"
		dataFile += "			<key>UIStatusBarHidden</key>\n"
		dataFile += "			<true/>\n"
		dataFile += "			<key>UISupportedInterfaceOrientations</key>\n"
		dataFile += "			<array>\n"
		dataFile += "				<string>UIInterfaceOrientationPortrait</string>\n"
		dataFile += "				<string>UIInterfaceOrientationPortraitUpsideDown</string>\n"
		dataFile += "				<string>UIInterfaceOrientationLandscapeLeft</string>\n"
		dataFile += "				<string>UIInterfaceOrientationLandscapeRight</string>\n"
		dataFile += "			</array>\n"
		dataFile += "			<key>UISupportedInterfaceOrientations~ipad</key>\n"
		dataFile += "			<array>\n"
		dataFile += "				<string>UIInterfaceOrientationPortrait</string>\n"
		dataFile += "				<string>UIInterfaceOrientationPortraitUpsideDown</string>\n"
		dataFile += "				<string>UIInterfaceOrientationLandscapeLeft</string>\n"
		dataFile += "				<string>UIInterfaceOrientationLandscapeRight</string>\n"
		dataFile += "			</array>\n"
		dataFile += "    </dict>\n"
		dataFile += "</plist>\n"
		dataFile += "\n\n"
		
		infoFile = os.path.join(target_outpath, "Info.plist")
		# Create the info file
		tmpFile = open(infoFile, 'w')
		tmpFile.write(dataFile)
		tmpFile.flush()
		tmpFile.close()
		"""
		infoFile = self.get_staging_path(pkg_name) + "/" + pkg_name + "-Info.plist"
		# Create the info file
		tmpFile = open(infoFile, 'w')
		tmpFile.write(dataFile)
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
		dataFile  = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
		dataFile += "<!DOCTYPE plist PUBLIC \"-//Apple Computer//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n"
		dataFile += "<plist version=\"1.0\">\n"
		dataFile += "	<dict>\n"
		dataFile += "		<key>rules</key>\n"
		dataFile += "		<dict>\n"
		dataFile += "			<key>.*</key>\n"
		dataFile += "			<true/>\n"
		dataFile += "			<key>Info.plist</key>\n"
		dataFile += "			<dict>\n"
		dataFile += "				<key>omit</key>\n"
		dataFile += "				<true/>\n"
		dataFile += "				<key>weight</key>\n"
		dataFile += "				<real>10</real>\n"
		dataFile += "			</dict>\n"
		dataFile += "			<key>ResourceRules.plist</key>\n"
		dataFile += "			<dict>\n"
		dataFile += "				<key>omit</key>\n"
		dataFile += "				<true/>\n"
		dataFile += "				<key>weight</key>\n"
		dataFile += "				<real>100</real>\n"
		dataFile += "			</dict>\n"
		dataFile += "		</dict>\n"
		dataFile += "	</dict>\n"
		dataFile += "</plist>\n"
		dataFile += "\n\n"

		infoFile = os.path.join(target_outpath, "ResourceRules.plist")
		# Create the info file
		tmpFile = open(infoFile, 'w')
		tmpFile.write(dataFile)
		tmpFile.flush()
		tmpFile.close()

		debug.print_element("pkg", "Entitlements.plist", "<==", "application mode")
		dataFile  = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
		dataFile += "<!DOCTYPE plist PUBLIC \"-//Apple Computer//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n"
		dataFile += "<plist version=\"1.0\">\n"
		dataFile += "	<dict>\n"
		dataFile += "		<key>get-task-allow</key>\n"
		dataFile += "		<true/>\n"
		dataFile += "    </dict>\n"
		dataFile += "</plist>\n"
		dataFile += "\n\n"

		infoFile = os.path.join(target_outpath, "Entitlements.plist")
		# Create the info file
		tmpFile = open(infoFile, 'w')
		tmpFile.write(dataFile)
		tmpFile.flush()
		tmpFile.close()

		# Simulateur path :
		#~/Library/Application\ Support/iPhone\ Simulator/7.0.3/Applications/
		# must have a 'uuidgen' UID generate value with this elemennt ...
		# get the bundle path : ==> maybe usefull in MocOS ...
		# NSLog(@"%@",[[NSBundle mainBundle] bundlePath]);
		
		# Must create the tarball of the application 
		#cd $(TARGET_OUT_FINAL)/; tar -cf $(PROJECT_NAME).tar $(PROJECT_NAME).app
		#cd $(TARGET_OUT_FINAL)/; tar -czf $(PROJECT_NAME).tar.gz $(PROJECT_NAME).app
		
		if self.sumulator == False:
			# Create the info file
			tmpFile = open(os.path.join(target_outpath, pkg_name + ".xcent"), 'w')
			tmpFile.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
			tmpFile.write("<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n")
			tmpFile.write("<plist version=\"1.0\">\n")
			tmpFile.write("    <dict>\n")
			tmpFile.write("        <key>application-identifier</key>\n")
			try:
				tmpFile.write("        <string>" + pkg_properties["APPLE_APPLICATION_IOS_ID"] + "." + pkg_properties["COMPAGNY_TYPE"] + "." + pkg_properties["COMPAGNY_NAME2"] + "." + pkg_name + "</string>\n")
			except:
				debug.error("Missing package property : APPLE_APPLICATION_IOS_ID")
			tmpFile.write("        <key>get-task-allow</key>\n")
			tmpFile.write("        <true/>\n")
			tmpFile.write("        <key>keychain-access-groups</key>\n")
			tmpFile.write("        <array>\n")
			tmpFile.write("            <string>" + pkg_properties["APPLE_APPLICATION_IOS_ID"] + ".atriasoft.worddown</string>\n")
			tmpFile.write("        </array>\n")
			tmpFile.write("    </dict>\n")
			tmpFile.write("</plist>\n")
			tmpFile.flush()
			tmpFile.close()
			# application signing :
			debug.print_element("pkg(signed)", "pkg", "<==", "Signing application")
			iosDevelopperKeyFile = ".iosKey.txt"
			if tools.file_size(iosDevelopperKeyFile) < 10:
				debug.error("To sign an application we need to have a signing key in the file '" + iosDevelopperKeyFile + "' \n it is represented like: 'iPhone Developer: Francis DUGENOUX (YRRQE5KGTH)'\n you can obtain it with : 'certtool y | grep \"Developer\"'")
			signatureKey = tools.file_read_data(iosDevelopperKeyFile)
			signatureKey = re.sub('\n', '', signatureKey)
			cmdLine  = 'codesign  --force --sign '
			# to get this key ;    certtool y | grep "Developer"
			cmdLine += ' "' + signatureKey + '" '
			cmdLine += ' --entitlements ' + self.get_build_path(pkg_name) + '/worddown.xcent'
			cmdLine += ' ' + self.get_staging_path(pkg_name)
			multiprocess.run_command(cmdLine)
			
			# --force --sign "iPhone Developer: Edouard DUPIN (SDFGSDFGSDFG)"
			#		  --resource-rules=/Users/edouarddupin/Library/Developer/Xcode/DerivedData/worddown-cmuvjchgtiteexdiacyqoexsyadg/Build/Products/Debug-iphoneos/worddown.app/ResourceRules.plist
			#		  --entitlements /Users/edouarddupin/Library/Developer/Xcode/DerivedData/worddown-cmuvjchgtiteexdiacyqoexsyadg/Build/Intermediates/worddown.build/Debug-iphoneos/worddown.build/worddown.xcent
			#		  /Users/edouarddupin/Library/Developer/Xcode/DerivedData/worddown-cmuvjchgtiteexdiacyqoexsyadg/Build/Products/Debug-iphoneos/worddown.app

	
	def createRandomNumber(self, len):
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




