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
		
		self.pkg_path_data = "Resources"
		self.pkg_path_bin = "MacOS"
		self.pkg_path_lib = "lib"
		self.pkg_path_license = "license"
		
	"""
	def get_staging_path(self, binary_name):
		return tools.get_run_path() + self.path_out + self.path_staging + "/" + binary_name + ".app/Contents/"
	
	def get_staging_path_data(self, binary_name):
		return self.get_staging_path(binary_name) + self.path_data + "/"
	"""
	
	def make_package_binary(self, pkg_name, pkg_properties, base_pkg_path, heritage_list, static):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Generate package '" + pkg_name + "'")
		debug.debug("------------------------------------------------------------------------")
		#output path
		target_outpath = os.path.join(self.get_staging_path(pkg_name), pkg_name + ".app/Contents")
		tools.create_directory_of_file(target_outpath)
		
		## Create share datas:
		self.make_package_binary_data(target_outpath, pkg_name, base_pkg_path, heritage_list, static)
		
		## copy binary files:
		copy_list={}
		target_outpath_bin = os.path.join(target_outpath, self.pkg_path_bin)
		tools.create_directory_of_file(target_outpath_bin)
		path_src = self.get_build_file_bin(pkg_name)
		path_dst = os.path.join(target_outpath_bin, pkg_name + self.suffix_binary)
		debug.verbose("path_dst: " + str(path_dst))
		tools.copy_file(path_src, path_dst)
		#real copy files
		tools.copy_list(copy_list)
		if self.pkg_path_bin != "":
			# remove unneded files (NOT folder ...)
			tools.clean_directory(target_outpath_bin, copy_list)
		
		## Create libraries:
		copy_list={}
		target_outpath_lib = os.path.join(target_outpath, self.pkg_path_lib)
		if static == False:
			#copy all shred libs...
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
					tools.copy_file(file_src,
					                os.path.join(target_outpath_lib, os.path.basename(file_src)),
					                in_list=copy_list)
		#real copy files
		tools.copy_list(copy_list)
		if self.pkg_path_lib != "":
			# remove unneded files (NOT folder ...)
			tools.clean_directory(target_outpath_bin, copy_list)
		
		## Create icon (no convertion ==> TODO: must test if png is now supported):
		if     "ICON" in pkg_properties.keys() \
		   and pkg_properties["ICON"] != "":
			tools.copy_file(pkg_properties["ICON"], os.path.join(target_outpath, "icon.icns"), force=True)
		
		## Create info.plist file:
		# http://www.sandroid.org/imcross/#Deployment
		data_file  = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
		data_file += "<!DOCTYPE plist PUBLIC \"-//Apple Computer//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n"
		data_file += "<plist version=\"1.0\">\n"
		data_file += "    <dict>\n"
		data_file += "        <key>CFBundleExecutableFile</key>\n"
		data_file += "        <string>"+pkg_name+"</string>\n"
		data_file += "        <key>CFBundleName</key>\n"
		data_file += "        <string>"+pkg_name+"</string>\n"
		data_file += "        <key>CFBundleIdentifier</key>\n"
		data_file += "        <string>" + pkg_properties["COMPAGNY_TYPE"] + "." + pkg_properties["COMPAGNY_NAME2"] + "." + pkg_name + "</string>\n"
		data_file += "        <key>CFBundleSignature</key>\n"
		data_file += "        <string>????</string>\n"
		data_file += "        <key>CFBundleIconFile</key>\n"
		data_file += "        <string>icon.icns</string>\n"
		data_file += "    </dict>\n"
		data_file += "</plist>\n"
		data_file += "\n\n"
		tools.file_write_data(os.path.join(target_outpath, "Info.plist"),
		                      data_file,
		                      only_if_new=True)
		
		## Create PkgInfo file:
		tools.file_write_data(os.path.join(target_outpath, "PkgInfo"),
		                      "APPL????",
		                      only_if_new=True)
		
		## Create a simple interface to localy install the aplication for the shell (a shell command line interface):
		data_file  = "#!/bin/bash\n"
		data_file += "# Simply open the real application in the correct way (a link does not work ...)\n"
		data_file += "/Applications/" + pkg_name + ".app/Contents/MacOS/" + pkg_name + " $*\n"
		#tmpFile.write("open -n /Applications/edn.app --args -AppCommandLineArg $*\n")
		tools.file_write_data(os.path.join(target_outpath, "shell", pkg_name),
		                      data_file,
		                      only_if_new=True)
		
		## Create the disk image of the application:
		debug.info("Generate disk image for '" + pkg_name + "'")
		output_file_name = os.path.join(self.get_final_path(), pkg_name + ".dmg")
		cmd = "hdiutil create -volname "
		cmd += pkg_name + " -srcpath "
		cmd += os.path.join(tools.get_run_path(), self.path_out,  self.path_staging, pkg_name + ".app")
		cmd += " -ov -format UDZO "
		cmd += output_file_name
		tools.create_directory_of_file(output_file_name)
		multiprocess.run_command_direct(cmd)
		debug.info("disk image: " + output_file_name)
		
		## user information:
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




