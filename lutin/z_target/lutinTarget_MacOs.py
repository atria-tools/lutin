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
from lutin import host
from lutin import multiprocess
import os
import stat
import shutil

class Target(target.Target):
	def __init__(self, config):
		#processor type selection (auto/arm/ppc/x86)
		if config["arch"] == "auto":
			config["arch"] = "x86"
		#bus size selection (auto/32/64)
		if config["bus-size"] == "auto":
			config["bus-size"] = str(host.BUS_SIZE)
		# http://biolpc22.york.ac.uk/pub/linux-mac-cross/
		# http://devs.openttd.org/~truebrain/compile-farm/apple-darwin9.txt
		target.Target.__init__(self, "MacOs", config, "")
		
		#self.path_bin="MacOS"
		#self.path_lib="lib"
		#self.path_data="Resources"
		#self.path_doc="doc"
		
		self.suffix_lib_static='.a'
		self.suffix_lib_dynamic='.dylib'
		#self.suffix_binary=''
		#self.suffix_package=''
		
		self.global_flags_cc.append("-D__STDCPP_LLVM__")
		
	
	def get_staging_path(self, binary_name):
		return tools.get_run_path() + self.path_out + self.path_staging + "/" + binary_name + ".app/Contents/"
	
	def get_staging_path_data(self, binary_name):
		return self.get_staging_path(binary_name) + self.path_data + "/"
	
	def make_package(self, pkg_name, pkg_properties, base_pkg_path, heritage_list):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Generate package '" + pkg_name + "'")
		debug.debug("------------------------------------------------------------------------")
		
		if    "ICON" in pkg_properties.keys() \
		   and pkg_properties["ICON"] != "":
			tools.copy_file(pkg_properties["ICON"], self.get_staging_path_data(pkg_name) + "/icon.icns", force=True)
		
		# http://www.sandroid.org/imcross/#Deployment
		infoFile=self.get_staging_path(pkg_name) + "/Info.plist"
		# Create the info file
		tmpFile = open(infoFile, 'w')
		tmpFile.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
		tmpFile.write("<!DOCTYPE plist PUBLIC \"-//Apple Computer//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n")
		tmpFile.write("<plist version=\"1.0\">\n")
		tmpFile.write("    <dict>\n")
		tmpFile.write("        <key>CFBundleExecutableFile</key>\n")
		tmpFile.write("        <string>"+pkg_name+"</string>\n")
		tmpFile.write("        <key>CFBundleName</key>\n")
		tmpFile.write("        <string>"+pkg_name+"</string>\n")
		tmpFile.write("        <key>CFBundleIdentifier</key>\n")
		tmpFile.write("        <string>" + pkg_properties["COMPAGNY_TYPE"] + "." + pkg_properties["COMPAGNY_NAME2"] + "." + pkg_name + "</string>\n")
		tmpFile.write("        <key>CFBundleSignature</key>\n")
		tmpFile.write("        <string>????</string>\n")
		tmpFile.write("        <key>CFBundleIconFile</key>\n")
		tmpFile.write("        <string>icon.icns</string>\n")
		tmpFile.write("    </dict>\n")
		tmpFile.write("</plist>\n")
		tmpFile.write("\n\n")
		tmpFile.flush()
		tmpFile.close()
		infoFile=self.get_staging_path(pkg_name) + "/PkgInfo"
		# Create the info file
		tmpFile = open(infoFile, 'w')
		tmpFile.write("APPL????")
		tmpFile.flush()
		tmpFile.close()
		
		# Create a simple interface to localy install the aplication for the shell (a shell command line interface)
		shell_file_name=self.get_staging_path(pkg_name) + "/shell/" + pkg_name
		# Create the info file
		tools.create_directory_of_file(shell_file_name)
		tmpFile = open(shell_file_name, 'w')
		tmpFile.write("#!/bin/bash\n")
		tmpFile.write("# Simply open the real application in the correct way (a link does not work ...)\n")
		tmpFile.write("/Applications/" + pkg_name + ".app/Contents/MacOS/" + pkg_name + " $*\n")
		#tmpFile.write("open -n /Applications/edn.app --args -AppCommandLineArg $*\n")
		tmpFile.flush()
		tmpFile.close()
		
		
		# Must create the disk image of the application 
		debug.info("Generate disk image for '" + pkg_name + "'")
		output_file_name = self.get_final_path() + "/" + pkg_name + ".dmg"
		cmd = "hdiutil create -volname "
		cmd += pkg_name + " -srcpath "
		cmd += tools.get_run_path() + self.path_out + self.path_staging + "/" + pkg_name + ".app"
		cmd += " -ov -format UDZO "
		cmd += output_file_name
		tools.create_directory_of_file(output_file_name)
		multiprocess.run_command_direct(cmd)
		debug.info("disk image: " + output_file_name)
		
		debug.info("You can have an shell interface by executing : ")
		debug.info("    sudo cp " + shell_file_name + " /usr/local/bin")
	
	def install_package(self, pkg_name):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Install package '" + pkg_name + "'")
		debug.debug("------------------------------------------------------------------------")
		debug.info("copy " + tools.get_run_path() + self.path_out + self.path_staging + "/" + pkg_name + ".app in /Applications/")
		if os.path.exists("/Applications/" + pkg_name + ".app") == True:
			shutil.rmtree("/Applications/" + pkg_name + ".app")
		# copy the application in the basic application path : /Applications/xxx.app
		shutil.copytree(tools.get_run_path() + self.path_out + self.path_staging + "/" + pkg_name + ".app", "/Applications/" + pkg_name + ".app")
	
	def un_install_package(self, pkg_name):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Un-Install package '" + pkg_name + "'")
		debug.debug("------------------------------------------------------------------------")
		debug.info("remove OLD application /Applications/" + pkg_name + ".app")
		# Remove the application in the basic application path : /Applications/xxx.app
		if os.path.exists("/Applications/" + pkg_name + ".app") == True:
			shutil.rmtree("/Applications/" + pkg_name + ".app")




