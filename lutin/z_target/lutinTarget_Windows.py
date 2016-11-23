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
from lutin import host
from lutin import depend
import os
import stat
import sys
from lutin import zip
from lutin import multiprocess

class Target(target.Target):
	def __init__(self, config, sub_name=[]):
		if config["compilator"] != "gcc":
			debug.error("Windows does not support '" + config["compilator"] + "' compilator ... availlable : [gcc]")
			config["compilator"] = "gcc"
		
		#processor type selection (auto/arm/ppc/x86)
		if config["arch"] == "auto":
			config["arch"] = "x86"
		#bus size selection (auto/32/64)
		if config["bus-size"] == "auto":
			config["bus-size"] = str(host.BUS_SIZE)
		
		target.Target.__init__(self, ["Windows"] + sub_name, config, "")
		
		# on windows board the basic path is not correct 
		# TODO : get external PATH for the minGW path
		# TODO : Set the cyngwin path ...
		if host.OS == "Windows":
			self.set_cross_base("c:\\MinGW\\bin\\")
			sys.path.append("c:\\MinGW\\bin" )
			os.environ['PATH'] += ";c:\\MinGW\\bin\\"
		else:
			if self.config["bus-size"] == "64":
				# 64 bits
				self.set_cross_base("x86_64-w64-mingw32-")
				self.base_path = "x86_64-w64-mingw32"
			else:
				# 32 bits
				self.set_cross_base("i686-w64-mingw32-")
				self.base_path = "i686-w64-mingw32"
		self.add_flag("c", [
		    "-DWIN32=1"
		    ])
		"""
		self.add_flag("link-lib", [
		    "dl"
		    ])
		"""
		
		self.pkg_path_data = "data"
		self.pkg_path_bin = ""
		self.pkg_path_lib = "lib"
		self.pkg_path_license = "license"
		
		self.suffix_lib_static = '.a'
		self.suffix_lib_dynamic = '.dll'
		self.suffix_binary = '.exe'
		#self.suffix_package = ''
		# TODO : Remove this ==> pb with openSSL shared lib ...
		self.support_dynamic_link = False
	
	
	def get_staging_path_data(self, binary_name, tmp=False):
		return os.path.join(self.get_staging_path(binary_name, tmp), binary_name + ".app", self.pkg_path_data)
	
	def make_package_binary(self, pkg_name, pkg_properties, base_pkg_path, heritage_list, static):
		debug.debug("------------------------------------------------------------------------")
		debug.debug("Generate package '" + pkg_name + "' v" + tools.version_to_string(pkg_properties["VERSION"]))
		debug.debug("------------------------------------------------------------------------")
		#output path
		target_outpath = os.path.join(self.get_staging_path(pkg_name, tmp=True), pkg_name + ".app")
		tools.create_directory_of_file(target_outpath)
		
		## Create share datas:
		ret_share = self.make_package_binary_data(target_outpath, pkg_name, base_pkg_path, heritage_list, static)
		
		## copy binary files:
		ret_bin = self.make_package_binary_bin(target_outpath, pkg_name, base_pkg_path, heritage_list, static)
		
		## Create libraries:
		ret_lib = self.make_package_binary_lib(target_outpath, pkg_name, base_pkg_path, heritage_list, static)
		
		## Create generic files:
		ret_file = self.make_package_generic_files(target_outpath+"/pkg", pkg_properties, pkg_name, base_pkg_path, heritage_list, static)
		
		build_package_path_done = os.path.join(self.get_build_path(pkg_name), "generatePackageDone.txt")
		#Check date between the current file "list of action to generate package and the end of package generation
		need_generate_package = depend.need_re_package(build_package_path_done, [__file__], True)
		## create the package:
		if    ret_share \
		   or ret_bin \
		   or ret_lib \
		   or ret_file \
		   or need_generate_package:
			# Zip the data
			debug.print_element("zip", "data.zip", "<==", self.get_staging_path_data(pkg_name, tmp=True) + "/*")
			zip_path = os.path.join(self.get_staging_path(pkg_name), pkg_name + ".app", "data.zip")
			zip.create_zip([
			    self.get_staging_path_data(pkg_name, tmp=True),
			    target_outpath+"/pkg"
			    ], zip_path)
			# copy if needed the binary:
			tools.copy_file(
			    os.path.join(self.get_staging_path(pkg_name, tmp=True), pkg_name + ".app", pkg_name + self.suffix_binary),
			    os.path.join(self.get_staging_path(pkg_name), pkg_name + ".app", pkg_name + self.suffix_binary),
			    force_identical=True)
			
			zip_path_final = os.path.join(self.get_final_path(), pkg_name + ".zip")
			# generate deployed zip (for user)
			debug.print_element("zip", pkg_name + ".zip", "<==", self.get_staging_path(pkg_name), pkg_name + ".app")
			zip.create_zip_file([
			    zip_path,
			    os.path.join(self.get_staging_path(pkg_name), pkg_name + ".app", pkg_name + self.suffix_binary)
			    ],
			    pkg_name + ".app",
			    zip_path_final)
			
			tools.file_write_data(build_package_path_done, "done...")
	
	def make_package_single_file(self, pkg_name, pkg_properties, base_pkg_path, heritage_list):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Generate package '" + pkg_name + "'")
		debug.debug("------------------------------------------------------------------------")
		debug.print_element("zip", "data.zip", "<==", "data/*")
		zipPath = self.get_staging_path(pkg_name) + "/data.zip"
		zip.create_zip(self.get_staging_path_data(pkg_name), zipPath)
		
		binPath = self.get_staging_path(pkg_name) + "/" + self.path_bin + "/" + pkg_name + self.suffix_binary
		binSize = tools.file_size(binPath)
		debug.info("binarysize : " + str(binSize/1024) + " ko ==> " + str(binSize) + " octets")
		
		#now we create a simple bundle binary ==> all file is stored in one file ...
		self.get_staging_path(pkg_name)
		finalBin = self.get_final_path() + "/" + pkg_name + self.suffix_binary
		tools.create_directory_of_file(finalBin);
		debug.print_element("pkg", finalBin, "<==", pkg_name + self.suffix_binary)
		#open output file
		tmpFile = open(finalBin, 'wb')
		# read all executable binary
		dataExecutable = tools.file_read_data(binPath, binary=True)
		# wrte binary to the output
		tmpFile.write(dataExecutable)
		#align data in the 32 Bytes position (prevent zip align error)
		residualToAllign = 32 + 32 - (len(dataExecutable) - int(len(dataExecutable)/32)*32)
		for iii in range(0,residualToAllign):
			tmpFile.write(b'\0');
		positionOfZip = len(dataExecutable) + residualToAllign;
		# write a control TAG
		tmpFile.write(b'***START DATA***');
		# write all the zip file
		debug.print_element("pkg", finalBin, "<==", "data.zip")
		dataData = tools.file_read_data(zipPath, binary=True)
		tmpFile.write(dataData)
		#align data in the 32 Bytes position (to be fun"
		tmpLen = len(dataData) + positionOfZip
		residualToAllign = 32 + 32 - (tmpLen - int(tmpLen/32)*32)
		for iii in range(0,residualToAllign):
			tmpFile.write(b'\0');
		# write a control TAG
		tmpFile.write(b'*** END DATA ***');
		# reserved AREA (can be use later for extra value ...)
		for iii in range(0,8):
			tmpFile.write(b'\0');
		# write the position of the zip file (TAG position)
		h = '{0:016x}'.format(positionOfZip)
		s = ('0'*(len(h) % 2) + h).decode('hex')
		tmpFile.write(s)
		# package is done
		tmpFile.flush()
		tmpFile.close()
		debug.verbose("zip position=" + str(positionOfZip) + " = 0x" + h)
	
	def install_package(self, pkg_name):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Install package '" + pkg_name + "'")
		debug.debug("------------------------------------------------------------------------")
		debug.warning("    ==> TODO")
		#sudo dpkg -i $(TARGET_OUT_FINAL)/$(PROJECT_NAME) + self.suffix_package
	
	def un_install_package(self, pkg_name):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Un-Install package '" + pkg_name + "'")
		debug.debug("------------------------------------------------------------------------")
		debug.warning("    ==> TODO")
		#sudo dpkg -r $(TARGET_OUT_FINAL)/$(PROJECT_NAME) + self.suffix_package
	
	def run(self, pkg_name, option_list, binary_name = None):
		debug.debug("------------------------------------------------------------------------")
		debug.info("-- Run package '" + pkg_name + "' + option: " + str(option_list))
		debug.debug("------------------------------------------------------------------------")
		if host.OS == "Windows":
			debug.error("action not implemented ...")
			return
		debug.debug(" think to configure your wine : 'winecfg' : https://www.winehq.org/docs/wineusr-guide/config-wine-main")
		appl_path = os.path.join(self.get_staging_path(pkg_name), pkg_name + ".app", pkg_name + self.suffix_binary)
		cmd = "wine " + appl_path + " "
		for elem in option_list:
			cmd += elem + " "
		multiprocess.run_command_no_lock_out(cmd)
		debug.debug("------------------------------------------------------------------------")
		debug.info("-- Run package '" + pkg_name + "' Finished")
		debug.debug("------------------------------------------------------------------------")

