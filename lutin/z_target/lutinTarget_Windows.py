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
	
	def make_package_generic_binary(self, pkg_name, pkg_properties, base_pkg_path, heritage_list, static):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Generate package '" + pkg_name + "'")
		debug.debug("------------------------------------------------------------------------")
		#output path
		target_outpath = os.path.join(self.get_staging_path(pkg_name), pkg_name + ".app")
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
		tools.copy_file(path_src,
		                path_dst,
		                in_list=copy_list)
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
			tools.clean_directory(target_outpath_lib, copy_list)
		
		## Create version file:
		tools.file_write_data(os.path.join(target_outpath, "version.txt"),
		                      pkg_properties["VERSION"],
		                      only_if_new=True)
		
		## Create maintainer file:
		tools.file_write_data(os.path.join(target_outpath, "maintainer.txt"),
		                      self.generate_list_separate_coma(pkg_properties["MAINTAINER"]),
		                      only_if_new=True)
		
		## Create appl_name file:
		tools.file_write_data(os.path.join(target_outpath, "appl_name.txt"),
		                      "en_EN:" + pkg_properties["NAME"],
		                      only_if_new=True)
		
		## Create appl_description file:
		tools.file_write_data(os.path.join(target_outpath, "appl_description.txt"),
		                      "en_EN:" + pkg_properties["DESCRIPTION"],
		                      only_if_new=True)
		
		## Create Readme file:
		readme_file_dest = target_outpath + "/readme.txt"
		if os.path.exists(base_pkg_path + "/os-Linux/README")==True:
			tools.copy_file(base_pkg_path + "/os-Linux/README", readme_file_dest)
		elif os.path.exists(base_pkg_path + "/README")==True:
			tools.copy_file(base_pkg_path + "/README", readme_file_dest)
		elif os.path.exists(base_pkg_path + "/README.md")==True:
			tools.copy_file(base_pkg_path + "/README.md", readme_file_dest)
		else:
			debug.info("no file 'README', 'README.md' or 'os-Linux/README' ==> generate an empty one")
			tools.file_write_data(readme_file_dest,
			                      "No documentation for " + pkg_name + "\n",
			                      only_if_new=True)
		
		## Create licence file:
		license_file_dest = os.path.join(target_outpath, self.pkg_path_license, pkg_name + ".txt")
		tools.create_directory_of_file(license_file_dest)
		if os.path.exists(base_pkg_path + "/license.txt")==True:
			tools.copy_file(base_pkg_path + "/license.txt", license_file_dest)
		else:
			debug.info("no file 'license.txt' ==> generate an empty one")
			tmpFile = open(license_file_dest, 'w')
			tools.file_write_data(license_file_dest,
			                      "No license define by the developper for " + pkg_name + "\n",
			                      only_if_new=True)
		
		## Create changeLog file:
		change_log_file_dest = target_outpath + "/changelog.txt"
		if os.path.exists(base_pkg_path + "/changelog") == True:
			tools.copy_file(base_pkg_path + "/changelog", change_log_file_dest)
		else:
			debug.info("no file 'changelog' ==> generate an empty one")
			tools.file_write_data(change_log_file_dest,
			                      "No changelog data " + pkg_name + "\n",
			                      only_if_new=True)
		
	
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

