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
import os
import stat
import re
from lutin import host
from lutin import multiprocess

class Target(target.Target):
	def __init__(self, config):
		#processor type selection (auto/arm/ppc/x86)
		if config["arch"] == "auto":
			config["arch"] = "x86"
		#bus size selection (auto/32/64)
		if config["bus-size"] == "auto":
			config["bus-size"] = str(host.BUS_SIZE)
		target.Target.__init__(self, "Linux", config, "")
		if self.config["bus-size"] == "64":
			# 64 bits
			if host.BUS_SIZE != 64:
				self.global_flags_cc.append("-m64")
		else:
			# 32 bits
			if host.BUS_SIZE != 32:
				self.global_flags_cc.append("-m32")
		
		self.global_flags_cc.append("-fpic")
		self.global_flags_cc.append("-D__STDCPP_GNU__")
		
		
		self.pkg_path_data = "share"
		self.pkg_path_bin = "bin"
		self.pkg_path_lib = "lib"
		self.pkg_path_license = "license"
	
	"""
	.local/application
	    *--> applName -> applName.app/bin/applName
	    *--> applName.app
	        *--> appl_description.txt
	        *--> appl_name.txt
	        *--> changelog.txt
	        *--> copyright.txt
	        *--> readme.txt
	        *--> version.txt
	        *--> website.txt
	        *--> icon.png
	        *--> bin
	        *    *--> applName
	        *--> doc
	        *    *--> applName
	        *--> lib
	        *    *--> XX.so
	        *    *--> YY.so
	        *--> license
	        *    *--> applName.txt
	        *    *--> libXX.txt
	        *    *--> libYY.txt
	        *--> man
	        *--> share
	        *    *--> applName
	        *    *--> XX
	        *    *--> YY
	        *--> sources
	"""
	def make_package_generic_binary(self, pkg_name, pkg_properties, base_pkg_path, heritage_list, static):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Generate generic '" + pkg_name + "' v"+pkg_properties["VERSION"])
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
		readme_file_dest = os.path.join(target_outpath, "readme.txt")
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
		
		## create the package:
		debug.debug("package : " + self.get_staging_path(pkg_name) + "/" + pkg_name + ".app.pkg")
		os.system("cd " + self.get_staging_path(pkg_name) + " ; tar -czf " + pkg_name + ".app.tar.gz " + pkg_name + ".app")
		#multiprocess.run_command("cd " + self.get_staging_path(pkg_name) + " ; tar -czf " + pkg_name + ".app.tar.gz " + pkg_name + ".app")
		tools.create_directory_of_file(self.get_final_path())
		tools.copy_file(self.get_staging_path(pkg_name) + "/" + pkg_name + ".app.tar.gz", self.get_final_path() + "/" + pkg_name + ".app.gpkg")
	
	
	
	
	def make_package_debian(self, pkg_name, pkg_properties, base_pkg_path, heritage_list):
		# http://alp.developpez.com/tutoriels/debian/creer-paquet/
		debianpkg_name = re.sub("_", "-", pkg_name)
		debug.debug("------------------------------------------------------------------------")
		debug.info("Generate package '" + debianpkg_name + "' v"+pkg_properties["VERSION"])
		debug.debug("------------------------------------------------------------------------")
		self.get_staging_path(pkg_name)
		target_outpathDebian = self.get_staging_path(pkg_name) + "/DEBIAN/"
		finalFileControl = target_outpathDebian + "control"
		finalFilepostRm = target_outpathDebian + "postrm"
		# create the paths :
		tools.create_directory_of_file(finalFileControl)
		tools.create_directory_of_file(finalFilepostRm)
		## Create the control file
		tools.create_directory_of_file(finalFileControl)
		tmpFile = open(finalFileControl, 'w')
		tmpFile.write("Package: " + debianpkg_name + "\n")
		tmpFile.write("Version: " + pkg_properties["VERSION"] + "\n")
		tmpFile.write("Section: " + self.generate_list_separate_coma(pkg_properties["SECTION"]) + "\n")
		tmpFile.write("Priority: " + pkg_properties["PRIORITY"] + "\n")
		tmpFile.write("Architecture: all\n")
		tmpFile.write("Depends: bash\n")
		tmpFile.write("Maintainer: " + self.generate_list_separate_coma(pkg_properties["MAINTAINER"]) + "\n")
		tmpFile.write("Description: " + pkg_properties["DESCRIPTION"] + "\n")
		tmpFile.write("\n")
		tmpFile.flush()
		tmpFile.close()
		## Create the PostRm
		tmpFile = open(finalFilepostRm, 'w')
		tmpFile.write("#!/bin/bash\n")
		tmpFile.write("touch ~/." + pkg_name + "\n")
		if pkg_name != "":
			tmpFile.write("touch ~/.local/share/" + pkg_name + "\n")
			tmpFile.write("rm -r ~/.local/share/" + pkg_name + "\n")
		tmpFile.write("\n")
		tmpFile.flush()
		tmpFile.close()
		## Enable Execution in script
		os.chmod(finalFilepostRm, stat.S_IRWXU + stat.S_IRGRP + stat.S_IXGRP + stat.S_IROTH + stat.S_IXOTH);
		## Readme donumentation
		readmeFileDest = self.get_staging_path(pkg_name) + "/usr/share/doc/"+ debianpkg_name + "/README"
		tools.create_directory_of_file(readmeFileDest)
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
		## licence file
		license_file_dest = self.get_staging_path(pkg_name) + "/usr/share/doc/"+ debianpkg_name + "/copyright"
		tools.create_directory_of_file(license_file_dest)
		if os.path.exists(base_pkg_path + "/license.txt")==True:
			tools.copy_file(base_pkg_path + "/license.txt", license_file_dest)
		else:
			debug.info("no file 'license.txt' ==> generate an empty one")
			tmpFile = open(license_file_dest, 'w')
			tmpFile.write("No license define by the developper for " + pkg_name + "\n")
			tmpFile.flush()
			tmpFile.close()
		##changeLog file
		change_log_file_dest = self.get_staging_path(pkg_name) + "/usr/share/doc/"+ debianpkg_name + "/changelog"
		tools.create_directory_of_file(change_log_file_dest)
		if os.path.exists(base_pkg_path + "/changelog")==True:
			tools.copy_file(base_pkg_path + "/changelog", change_log_file_dest)
		else:
			debug.info("no file 'changelog' ==> generate an empty one")
			tmpFile = open(change_log_file_dest, 'w')
			tmpFile.write("No changelog data " + pkg_name + "\n")
			tmpFile.flush()
			tmpFile.close()
		## create the package :
		debug.debug("package : " + self.get_staging_path(pkg_name) + "/" + debianpkg_name + ".deb")
		os.system("cd " + self.get_staging_path("") + " ; dpkg-deb --build " + pkg_name)
		tools.create_directory_of_file(self.get_final_path())
		tools.copy_file(self.get_staging_path("") + "/" + pkg_name + self.suffix_package, self.get_final_path() + "/" + pkg_name + self.suffix_package)
	
	def install_package(self, pkg_name):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Install package '" + pkg_name + "'")
		debug.debug("------------------------------------------------------------------------")
		os.system("sudo dpkg -i " + self.get_final_path() + "/" + pkg_name + self.suffix_package)
	
	def un_install_package(self, pkg_name):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Un-Install package '" + pkg_name + "'")
		debug.debug("------------------------------------------------------------------------")
		os.system("sudo dpkg -r " + self.get_final_path() + "/" + pkg_name + self.suffix_package)
	
	"""
	.local/application
	    *--> applName -> applName.app/bin/applName
	    *--> applName.app
	        *--> appl_description.txt
	        *--> appl_name.txt
	        *--> changelog.txt
	        *--> copyright.txt
	        *--> readme.txt
	        *--> version.txt
	        *--> website.txt
	        *--> icon.png
	        *--> bin
	        *    *--> applName
	        *--> doc
	        *    *--> applName
	        *--> lib
	        *    *--> XX.so
	        *    *--> YY.so
	        *--> license
	        *    *--> applName.txt
	        *    *--> libXX.txt
	        *    *--> libYY.txt
	        *--> man
	        *--> share
	        *    *--> applName
	        *    *--> XX
	        *    *--> YY
	        *--> sources
	"""
	def make_package_generic(self, pkg_name, pkg_properties, base_pkg_path, heritage_list):
		debug.warning("heritage for " + str(pkg_name) + ":")
		for heritage in heritage_list.list_heritage:
			debug.warning("heritage .... " + str(heritage.name) + " : " + str(heritage.depends))
		debianpkg_name = re.sub("_", "-", pkg_name)
		debug.debug("------------------------------------------------------------------------")
		debug.info("Generate generic '" + debianpkg_name + "' v"+pkg_properties["VERSION"])
		debug.debug("------------------------------------------------------------------------")
		target_outpath = self.get_staging_path(pkg_name) + "/edn.app/"
		tools.create_directory_of_file(target_outpath)
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
		license_file_dest = target_outpath + "/license/"+ debianpkg_name + ".txt"
		tools.create_directory_of_file(license_file_dest)
		if os.path.exists(base_pkg_path + "/license.txt")==True:
			tools.copy_file(base_pkg_path + "/license.txt", license_file_dest)
		else:
			debug.info("no file 'license.txt' ==> generate an empty one")
			tmpFile = open(license_file_dest, 'w')
			tmpFile.write("No license define by the developper for " + pkg_name + "\n")
			tmpFile.flush()
			tmpFile.close()
		## Create changeLog file
		change_log_file_dest = target_outpath + "/changelog.txt"
		if os.path.exists(base_pkg_path + "/changelog") == True:
			tools.copy_file(base_pkg_path + "/changelog", change_log_file_dest)
		else:
			debug.info("no file 'changelog' ==> generate an empty one")
			tmpFile = open(change_log_file_dest, 'w')
			tmpFile.write("No changelog data " + pkg_name + "\n")
			tmpFile.flush()
			tmpFile.close()
		## copy share path
		#debug.info("plop:" + self.get_staging_path(pkg_name) + self.path_data)
		if os.path.exists(self.get_staging_path(pkg_name) + self.path_data) == True:
			tools.copy_anything(self.get_staging_path(pkg_name) + self.path_data + "/*", target_outpath + self.path_data, recursive=True)
		
		## Create binary path:
		bin_path = target_outpath + self.path_bin
		#tools.create_directory_of_file(bin_path)
		tools.copy_anything(self.get_staging_path(pkg_name) + self.path_bin + "/*",
		                    bin_path)
		
		## create the package:
		debug.debug("package : " + self.get_staging_path(pkg_name) + "/" + debianpkg_name + ".app.pkg")
		os.system("cd " + self.get_staging_path(pkg_name) + " ; tar -czf " + pkg_name + ".app.tar.gz " + pkg_name + ".app")
		#multiprocess.run_command("cd " + self.get_staging_path(pkg_name) + " ; tar -czf " + pkg_name + ".app.tar.gz " + pkg_name + ".app")
		tools.create_directory_of_file(self.get_final_path())
		tools.copy_file(self.get_staging_path(pkg_name) + "/" + pkg_name + ".app.tar.gz", self.get_final_path() + "/" + pkg_name + ".app.gpkg")
		


