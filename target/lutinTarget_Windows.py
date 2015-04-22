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
import lutinTools as tools
import lutinHost
import os
import stat
import sys
import lutinZip as zip

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
		# force static link to prenvent many errors ...
		self.global_flags_ld.append(["-static-libgcc",
		                             "-static-libstdc++",
		                             "-static"])
		
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
		debug.print_element("zip", "data.zip", "<==", "data/*")
		zipPath = self.get_staging_folder(pkgName) + "/data.zip"
		zip.create_zip(self.get_staging_folder_data(pkgName), zipPath)
		
		binPath = self.get_staging_folder(pkgName) + "/" + self.folder_bin + "/" + pkgName + self.suffix_binary
		binSize = tools.file_size(binPath)
		debug.info("binarysize : " + str(binSize/1024) + " ko ==> " + str(binSize) + " octets")
		
		#now we create a simple bundle binary ==> all file is stored in one file ...
		self.get_staging_folder(pkgName)
		finalBin = self.get_final_folder() + "/" + pkgName + self.suffix_binary
		tools.create_directory_of_file(finalBin);
		debug.print_element("pkg", finalBin, "<==", pkgName + self.suffix_binary)
		tmpFile = open(finalBin, 'wb')
		dataExecutable = tools.file_read_data(binPath, binary=True)
		tmpFile.write(dataExecutable)
		residualToAllign = len(dataExecutable) - int(len(dataExecutable)/32)*32
		for iii in range(1,residualToAllign):
			tmpFile.write(b'j');
		positionOfZip = len(dataExecutable) + residualToAllign;
		
		debug.print_element("pkg", finalBin, "<==", "data.zip")
		dataData = tools.file_read_data(zipPath, binary=True)
		tmpFile.write(dataData)
		tmpLen = len(dataData) + positionOfZip
		residualToAllign = tmpLen - int(tmpLen/32)*32
		for iii in range(1,residualToAllign):
			tmpFile.write(b'j');
		tmpFile.write(bin(positionOfZip))
		tmpFile.flush()
		tmpFile.close()
		debug.info("zip position=" + str(positionOfZip))
	
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

