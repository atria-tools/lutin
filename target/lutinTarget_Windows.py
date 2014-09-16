#!/usr/bin/python
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##

import lutinDebug as debug
import lutinTarget
import lutinTools
import lutinHost
import os
import stat
import sys

class Target(lutinTarget.Target):
	def __init__(self, config):
		if config["compilator"] != "gcc":
			debug.error("Windows does not support '" + config["compilator"] + "' compilator ... availlable : [gcc]")
			config["compilator"] = "gcc"
		
		#processor type selection (auto/arm/ppc/x86)
		if config["arch"] == "auto":
			config["arch"] = "x86"
		#bus size selection (auto/32/64)
		if config["bus-size"] == "auto":
			config["bus-size"] = str(lutinHost.BUS_SIZE)
		
		lutinTarget.Target.__init__(self, "Windows", config, "")
		
		# on windows board the basic path is not correct 
		# TODO : get external PATH for the minGW path
		# TODO : Set the cyngwin path ...
		if lutinHost.OS == "Windows":
			self.set_cross_base("c:\\MinGW\\bin\\")
			sys.path.append("c:\\MinGW\\bin" )
			os.environ['PATH'] += ";c:\\MinGW\\bin\\"
		else:
			if self.config["bus-size"] == "64":
				# 64 bits
				self.set_cross_base("x86_64-w64-mingw32-")
			else:
				# 32 bits
				self.set_cross_base("i686-w64-mingw32-")
		
		self.folder_bin=""
		self.folder_lib="/lib"
		self.folder_data="/data"
		self.folder_doc="/doc"
		
		self.suffix_lib_static='.a'
		self.suffix_lib_dynamic='.dll'
		self.suffix_binary='.exe'
		self.suffix_package=''
	
	
	def get_staging_folder_data(self, binaryName):
		return self.get_staging_folder(binaryName) + self.folder_data
	
	def make_package(self, pkgName, pkgProperties, basePkgPath):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Generate package '" + pkgName + "'")
		debug.debug("------------------------------------------------------------------------")
		debug.warning("    ==> TODO")
	
	def install_package(self, pkgName):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Install package '" + pkgName + "'")
		debug.debug("------------------------------------------------------------------------")
		debug.warning("    ==> TODO")
		#sudo dpkg -i $(TARGET_OUT_FINAL)/$(PROJECT_NAME) + self.suffix_package
	
	def un_install_package(self, pkgName):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Un-Install package '" + pkgName + "'")
		debug.debug("------------------------------------------------------------------------")
		debug.warning("    ==> TODO")
		#sudo dpkg -r $(TARGET_OUT_FINAL)/$(PROJECT_NAME) + self.suffix_package

