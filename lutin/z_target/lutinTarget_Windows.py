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
import os
import stat
import sys
from lutin import zip

class Target(target.Target):
	def __init__(self, config):
		if config["compilator"] != "gcc":
			debug.error("Windows does not support '" + config["compilator"] + "' compilator ... availlable : [gcc]")
			config["compilator"] = "gcc"
		
		#processor type selection (auto/arm/ppc/x86)
		if config["arch"] == "auto":
			config["arch"] = "x86"
		#bus size selection (auto/32/64)
		if config["bus-size"] == "auto":
			config["bus-size"] = str(host.BUS_SIZE)
		
		target.Target.__init__(self, "Windows", config, "")
		
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
			else:
				# 32 bits
				self.set_cross_base("i686-w64-mingw32-")
		# force static link to prenvent many errors ...
		self.global_flags_ld.append(["-static-libgcc",
		                             "-static-libstdc++",
		                             "-static"])
		
		#self.path_bin=""
		#self.path_lib="lib"
		#self.path_data="data"
		#self.path_doc="doc"
		
		self.pkg_path_data = "data"
		self.pkg_path_bin = ""
		self.pkg_path_lib = "lib"
		self.pkg_path_license = "license"
		
		self.suffix_lib_static='.a'
		self.suffix_lib_dynamic='.dll'
		self.suffix_binary='.exe'
		#self.suffix_package=''
		self.global_flags_cc.append("-D__STDCPP_GNU__")
	
	
	def get_staging_path_data(self, binary_name, heritage_list):
		return self.get_staging_path(binary_name) + self.path_data
	
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
			self.make_package_generic_binary(pkg_name, pkg_properties, base_pkg_path, heritage_list, static = True)
		if module.get_type() == 'BINARY_SHARED':
			self.make_package_generic_binary(pkg_name, pkg_properties, base_pkg_path, heritage_list, static = False)
		if module.get_type() == 'PACKAGE':
			debug.info("Can not create package for package");
			return
		return
	
	def make_package_generic_binary(self, pkg_name, pkg_properties, base_pkg_path, heritage_list, static):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Generate package '" + pkg_name + "'")
		debug.debug("------------------------------------------------------------------------")
		#output path
		target_outpath = os.path.join(self.get_staging_path(pkg_name), pkg_name + ".app")
		tools.create_directory_of_file(target_outpath)
		
		## Create share datas
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
		
		## copy binary files
		target_outpath_bin = os.path.join(target_outpath, self.pkg_path_bin)
		tools.create_directory_of_file(target_outpath_bin)
		path_src = self.get_build_file_bin(pkg_name)
		path_dst = os.path.join(target_outpath_bin, pkg_name + self.suffix_binary)
		debug.verbose("path_dst: " + str(path_dst))
		tools.copy_file(path_src, path_dst)
		
		## Create version file
		tmpFile = open(target_outpath + "/version.txt", 'w')
		tmpFile.write(pkg_properties["VERSION"])
		tmpFile.flush()
		tmpFile.close()
		
		## Create maintainer file
		tmpFile = open(target_outpath + "/maintainer.txt", 'w')
		tmpFile.write(self.generate_list_separate_coma(pkg_properties["MAINTAINER"]))
		tmpFile.flush()
		tmpFile.close()
		
		## Create appl_name file
		tmpFile = open(target_outpath + "/appl_name.txt", 'w')
		tmpFile.write("en_EN:" + pkg_properties["NAME"])
		tmpFile.flush()
		tmpFile.close()
		
		## Create appl_description file
		tmpFile = open(target_outpath + "/appl_description.txt", 'w')
		tmpFile.write("en_EN:" + pkg_properties["DESCRIPTION"])
		tmpFile.flush()
		tmpFile.close()
		
		## Create Readme file
		readmeFileDest = target_outpath + "/readme.txt"
		if os.path.exists(base_pkg_path + "/os-Linux/README")==True:
			tools.copy_file(base_pkg_path + "/os-Linux/README", readmeFileDest)
		elif os.path.exists(base_pkg_path + "/README")==True:
			tools.copy_file(base_pkg_path + "/README", readmeFileDest)
		elif os.path.exists(base_pkg_path + "/README.md")==True:
			tools.copy_file(base_pkg_path + "/README.md", readmeFileDest)
		else:
			debug.info("no file 'README', 'README.md' or 'os-Linux/README' ==> generate an empty one")
			tmpFile = open(readmeFileDest, 'w')
			tmpFile.write("No documentation for " + pkg_name + "\n")
			tmpFile.flush()
			tmpFile.close()
		
		## Create licence file
		licenseFileDest = os.path.join(target_outpath, self.pkg_path_license, pkg_name + ".txt")
		tools.create_directory_of_file(licenseFileDest)
		if os.path.exists(base_pkg_path + "/license.txt")==True:
			tools.copy_file(base_pkg_path + "/license.txt", licenseFileDest)
		else:
			debug.info("no file 'license.txt' ==> generate an empty one")
			tmpFile = open(licenseFileDest, 'w')
			tmpFile.write("No license define by the developper for " + pkg_name + "\n")
			tmpFile.flush()
			tmpFile.close()
		
		## Create changeLog file
		changeLogFileDest = target_outpath + "/changelog.txt"
		if os.path.exists(base_pkg_path + "/changelog") == True:
			tools.copy_file(base_pkg_path + "/changelog", changeLogFileDest)
		else:
			debug.info("no file 'changelog' ==> generate an empty one")
			tmpFile = open(changeLogFileDest, 'w')
			tmpFile.write("No changelog data " + pkg_name + "\n")
			tmpFile.flush()
			tmpFile.close()
		
		
	
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

