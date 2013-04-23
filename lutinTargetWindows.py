#!/usr/bin/python
import lutinDebug as debug
import lutinTarget
import lutinTools
import os
import stat

class Target(lutinTarget.Target):
	def __init__(self, typeCompilator, debugMode):
		cross = "i586-mingw32msvc-"
		
		if typeCompilator!="gcc":
			debug.error("Android does not support '" + typeCompilator + "' compilator ... availlable : [gcc]")
		
		lutinTarget.Target.__init__(self, "Windows", typeCompilator, debugMode, "", cross)
		
		self.folder_bin=""
		self.folder_lib="/lib"
		self.folder_data="/data"
		self.folder_doc="/doc"
		
		self.suffix_lib_static='.a'
		self.suffix_lib_dynamic='.dll'
		self.suffix_binary='.exe'
		self.suffix_package=''
		
	
	def MakePackage(self, pkgName, pkgProperties):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Generate package '" + pkgName + "'")
		debug.debug("------------------------------------------------------------------------")
		debug.warning("    ==> TODO")
	
	def InstallPackage(self, pkgName):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Install package '" + pkgName + "'")
		debug.debug("------------------------------------------------------------------------")
		debug.warning("    ==> TODO")
		#sudo dpkg -i $(TARGET_OUT_FINAL)/$(PROJECT_NAME) + self.suffix_package
	
	def UnInstallPackage(self, pkgName):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Un-Install package '" + pkgName + "'")
		debug.debug("------------------------------------------------------------------------")
		debug.warning("    ==> TODO")
		#sudo dpkg -r $(TARGET_OUT_FINAL)/$(PROJECT_NAME) + self.suffix_package

