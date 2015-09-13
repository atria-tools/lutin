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
	
	def generate_list_separate_coma(self, list):
		result = ""
		fistTime = True
		for elem in list:
			if fistTime == True:
				fistTime = False
			else:
				result += ","
			result += elem
		return result
	
	def make_package(self, pkgName, pkgProperties, basePkgPath, heritage_list, type="generic"):
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
		   or module.get_type() == 'BINARY_STAND_ALONE' \
		   or module.get_type() == 'BINARY_SHARED':
			self.make_package_generic_binary(pkgName, pkgProperties, basePkgPath, heritage_list)
		if module.get_type() == 'PACKAGE':
			debug.info("Can not create package for package");
			return
		return
		
		if type == "debian":
			self.make_package_debian(pkgName, pkgProperties, basePkgPath, heritage_list)
		elif type == "generic":
			self.make_package_generic(pkgName, pkgProperties, basePkgPath, heritage_list)
	
	
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
	def make_package_generic_binary(self, pkgName, pkgProperties, basePkgPath, heritage_list):
		debianPkgName = re.sub("_", "-", pkgName)
		
		debug.debug("------------------------------------------------------------------------")
		debug.info("Generate generic '" + debianPkgName + "' v"+pkgProperties["VERSION"])
		debug.debug("------------------------------------------------------------------------")
		#output path
		target_outpath = os.path.join(self.get_staging_path(pkgName), pkgName + ".app")
		tools.create_directory_of_file(target_outpath)
		
		## Create share datas
		target_outpath_data = os.path.join(target_outpath, "share", pkgName)
		tools.create_directory_of_file(target_outpath_data)
		debug.debug("heritage for " + str(pkgName) + ":")
		for heritage in heritage_list.list_heritage:
			debug.debug("sub elements: " + str(heritage.name))
			path_src = self.get_build_path_data(heritage.name)
			debug.verbose("      has directory: " + path_src)
			if os.path.isdir(path_src):
				# TODO : Add os.path.dirname( for shared elements ... (like this, this add all element in a single os.path.dirname(path_src)
				debug.debug("      need copy: " + path_src + " to " + target_outpath_data)
				#copy all data:
				# TODO : We can have a problem when writing over library files ...
				tools.copy_anything(path_src, target_outpath_data, recursive=True, force_identical=True)
		
		## Create share datas
		target_outpath_bin = os.path.join(target_outpath, "bin")
		tools.create_directory_of_file(target_outpath_bin)
		path_src = self.get_build_file_bin(pkgName)
		path_dst = os.path.join(target_outpath_bin, pkgName + self.suffix_binary)
		debug.warning("path_dst: " + str(path_dst))
		tools.copy_file(path_src, path_dst)
		
		## Create libraries
		
		
		## Create version file
		tmpFile = open(target_outpath + "/version.txt", 'w')
		tmpFile.write(pkgProperties["VERSION"])
		tmpFile.flush()
		tmpFile.close()
		
		## Create maintainer file
		tmpFile = open(target_outpath + "/maintainer.txt", 'w')
		tmpFile.write(self.generate_list_separate_coma(pkgProperties["MAINTAINER"]))
		tmpFile.flush()
		tmpFile.close()
		
		## Create appl_name file
		tmpFile = open(target_outpath + "/appl_name.txt", 'w')
		tmpFile.write("en_EN:" + pkgProperties["NAME"])
		tmpFile.flush()
		tmpFile.close()
		
		## Create appl_description file
		tmpFile = open(target_outpath + "/appl_description.txt", 'w')
		tmpFile.write("en_EN:" + pkgProperties["DESCRIPTION"])
		tmpFile.flush()
		tmpFile.close()
		
		## Create Readme file
		readmeFileDest = target_outpath + "/readme.txt"
		if os.path.exists(basePkgPath + "/os-Linux/README")==True:
			tools.copy_file(basePkgPath + "/os-Linux/README", readmeFileDest)
		elif os.path.exists(basePkgPath + "/README")==True:
			tools.copy_file(basePkgPath + "/README", readmeFileDest)
		elif os.path.exists(basePkgPath + "/README.md")==True:
			tools.copy_file(basePkgPath + "/README.md", readmeFileDest)
		else:
			debug.info("no file 'README', 'README.md' or 'os-Linux/README' ==> generate an empty one")
			tmpFile = open(readmeFileDest, 'w')
			tmpFile.write("No documentation for " + pkgName + "\n")
			tmpFile.flush()
			tmpFile.close()
		
		## Create licence file
		licenseFileDest = target_outpath + "/license/"+ debianPkgName + ".txt"
		tools.create_directory_of_file(licenseFileDest)
		if os.path.exists(basePkgPath + "/license.txt")==True:
			tools.copy_file(basePkgPath + "/license.txt", licenseFileDest)
		else:
			debug.info("no file 'license.txt' ==> generate an empty one")
			tmpFile = open(licenseFileDest, 'w')
			tmpFile.write("No license define by the developper for " + pkgName + "\n")
			tmpFile.flush()
			tmpFile.close()
		
		## Create changeLog file
		changeLogFileDest = target_outpath + "/changelog.txt"
		if os.path.exists(basePkgPath + "/changelog") == True:
			tools.copy_file(basePkgPath + "/changelog", changeLogFileDest)
		else:
			debug.info("no file 'changelog' ==> generate an empty one")
			tmpFile = open(changeLogFileDest, 'w')
			tmpFile.write("No changelog data " + pkgName + "\n")
			tmpFile.flush()
			tmpFile.close()
		
		## copy share path
		#debug.info("plop:" + self.get_staging_path(pkgName) + self.path_data)
		if os.path.exists(self.get_staging_path(pkgName) + self.path_data) == True:
			tools.copy_anything(self.get_staging_path(pkgName) + self.path_data + "/*", target_outpath + self.path_data, recursive=True)
		
		## Create binary path:
		bin_path = target_outpath + self.path_bin
		#tools.create_directory_of_file(bin_path)
		tools.copy_anything(self.get_staging_path(pkgName) + self.path_bin + "/*",
		                    bin_path)
		
		## create the package:
		debug.debug("package : " + self.get_staging_path(pkgName) + "/" + debianPkgName + ".app.pkg")
		os.system("cd " + self.get_staging_path(pkgName) + " ; tar -czf " + pkgName + ".app.tar.gz " + pkgName + ".app")
		#multiprocess.run_command("cd " + self.get_staging_path(pkgName) + " ; tar -czf " + pkgName + ".app.tar.gz " + pkgName + ".app")
		tools.create_directory_of_file(self.get_final_path())
		tools.copy_file(self.get_staging_path(pkgName) + "/" + pkgName + ".app.tar.gz", self.get_final_path() + "/" + pkgName + ".app.gpkg")
		
	
	def make_package_debian(self, pkgName, pkgProperties, basePkgPath, heritage_list):
		# http://alp.developpez.com/tutoriels/debian/creer-paquet/
		debianPkgName = re.sub("_", "-", pkgName)
		debug.debug("------------------------------------------------------------------------")
		debug.info("Generate package '" + debianPkgName + "' v"+pkgProperties["VERSION"])
		debug.debug("------------------------------------------------------------------------")
		self.get_staging_path(pkgName)
		target_outpathDebian = self.get_staging_path(pkgName) + "/DEBIAN/"
		finalFileControl = target_outpathDebian + "control"
		finalFilepostRm = target_outpathDebian + "postrm"
		# create the paths :
		tools.create_directory_of_file(finalFileControl)
		tools.create_directory_of_file(finalFilepostRm)
		## Create the control file
		tools.create_directory_of_file(finalFileControl)
		tmpFile = open(finalFileControl, 'w')
		tmpFile.write("Package: " + debianPkgName + "\n")
		tmpFile.write("Version: " + pkgProperties["VERSION"] + "\n")
		tmpFile.write("Section: " + self.generate_list_separate_coma(pkgProperties["SECTION"]) + "\n")
		tmpFile.write("Priority: " + pkgProperties["PRIORITY"] + "\n")
		tmpFile.write("Architecture: all\n")
		tmpFile.write("Depends: bash\n")
		tmpFile.write("Maintainer: " + self.generate_list_separate_coma(pkgProperties["MAINTAINER"]) + "\n")
		tmpFile.write("Description: " + pkgProperties["DESCRIPTION"] + "\n")
		tmpFile.write("\n")
		tmpFile.flush()
		tmpFile.close()
		## Create the PostRm
		tmpFile = open(finalFilepostRm, 'w')
		tmpFile.write("#!/bin/bash\n")
		tmpFile.write("touch ~/." + pkgName + "\n")
		if pkgName != "":
			tmpFile.write("touch ~/.local/share/" + pkgName + "\n")
			tmpFile.write("rm -r ~/.local/share/" + pkgName + "\n")
		tmpFile.write("\n")
		tmpFile.flush()
		tmpFile.close()
		## Enable Execution in script
		os.chmod(finalFilepostRm, stat.S_IRWXU + stat.S_IRGRP + stat.S_IXGRP + stat.S_IROTH + stat.S_IXOTH);
		## Readme donumentation
		readmeFileDest = self.get_staging_path(pkgName) + "/usr/share/doc/"+ debianPkgName + "/README"
		tools.create_directory_of_file(readmeFileDest)
		if os.path.exists(basePkgPath + "/os-Linux/README")==True:
			tools.copy_file(basePkgPath + "/os-Linux/README", readmeFileDest)
		elif os.path.exists(basePkgPath + "/README")==True:
			tools.copy_file(basePkgPath + "/README", readmeFileDest)
		elif os.path.exists(basePkgPath + "/README.md")==True:
			tools.copy_file(basePkgPath + "/README.md", readmeFileDest)
		else:
			debug.info("no file 'README', 'README.md' or 'os-Linux/README' ==> generate an empty one")
			tmpFile = open(readmeFileDest, 'w')
			tmpFile.write("No documentation for " + pkgName + "\n")
			tmpFile.flush()
			tmpFile.close()
		## licence file
		licenseFileDest = self.get_staging_path(pkgName) + "/usr/share/doc/"+ debianPkgName + "/copyright"
		tools.create_directory_of_file(licenseFileDest)
		if os.path.exists(basePkgPath + "/license.txt")==True:
			tools.copy_file(basePkgPath + "/license.txt", licenseFileDest)
		else:
			debug.info("no file 'license.txt' ==> generate an empty one")
			tmpFile = open(licenseFileDest, 'w')
			tmpFile.write("No license define by the developper for " + pkgName + "\n")
			tmpFile.flush()
			tmpFile.close()
		##changeLog file
		changeLogFileDest = self.get_staging_path(pkgName) + "/usr/share/doc/"+ debianPkgName + "/changelog"
		tools.create_directory_of_file(changeLogFileDest)
		if os.path.exists(basePkgPath + "/changelog")==True:
			tools.copy_file(basePkgPath + "/changelog", changeLogFileDest)
		else:
			debug.info("no file 'changelog' ==> generate an empty one")
			tmpFile = open(changeLogFileDest, 'w')
			tmpFile.write("No changelog data " + pkgName + "\n")
			tmpFile.flush()
			tmpFile.close()
		## create the package :
		debug.debug("package : " + self.get_staging_path(pkgName) + "/" + debianPkgName + ".deb")
		os.system("cd " + self.get_staging_path("") + " ; dpkg-deb --build " + pkgName)
		tools.create_directory_of_file(self.get_final_path())
		tools.copy_file(self.get_staging_path("") + "/" + pkgName + self.suffix_package, self.get_final_path() + "/" + pkgName + self.suffix_package)
	
	def install_package(self, pkgName):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Install package '" + pkgName + "'")
		debug.debug("------------------------------------------------------------------------")
		os.system("sudo dpkg -i " + self.get_final_path() + "/" + pkgName + self.suffix_package)
	
	def un_install_package(self, pkgName):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Un-Install package '" + pkgName + "'")
		debug.debug("------------------------------------------------------------------------")
		os.system("sudo dpkg -r " + self.get_final_path() + "/" + pkgName + self.suffix_package)
	
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
	def make_package_generic(self, pkgName, pkgProperties, basePkgPath, heritage_list):
		debug.warning("heritage for " + str(pkgName) + ":")
		for heritage in heritage_list.list_heritage:
			debug.warning("heritage .... " + str(heritage.name) + " : " + str(heritage.depends))
		debianPkgName = re.sub("_", "-", pkgName)
		debug.debug("------------------------------------------------------------------------")
		debug.info("Generate generic '" + debianPkgName + "' v"+pkgProperties["VERSION"])
		debug.debug("------------------------------------------------------------------------")
		target_outpath = self.get_staging_path(pkgName) + "/edn.app/"
		tools.create_directory_of_file(target_outpath)
		## Create version file
		tmpFile = open(target_outpath + "/version.txt", 'w')
		tmpFile.write(pkgProperties["VERSION"])
		tmpFile.flush()
		tmpFile.close()
		## Create maintainer file
		tmpFile = open(target_outpath + "/maintainer.txt", 'w')
		tmpFile.write(self.generate_list_separate_coma(pkgProperties["MAINTAINER"]))
		tmpFile.flush()
		tmpFile.close()
		## Create appl_name file
		tmpFile = open(target_outpath + "/appl_name.txt", 'w')
		tmpFile.write("en_EN:" + pkgProperties["NAME"])
		tmpFile.flush()
		tmpFile.close()
		## Create appl_description file
		tmpFile = open(target_outpath + "/appl_description.txt", 'w')
		tmpFile.write("en_EN:" + pkgProperties["DESCRIPTION"])
		tmpFile.flush()
		tmpFile.close()
		## Create Readme file
		readmeFileDest = target_outpath + "/readme.txt"
		if os.path.exists(basePkgPath + "/os-Linux/README")==True:
			tools.copy_file(basePkgPath + "/os-Linux/README", readmeFileDest)
		elif os.path.exists(basePkgPath + "/README")==True:
			tools.copy_file(basePkgPath + "/README", readmeFileDest)
		elif os.path.exists(basePkgPath + "/README.md")==True:
			tools.copy_file(basePkgPath + "/README.md", readmeFileDest)
		else:
			debug.info("no file 'README', 'README.md' or 'os-Linux/README' ==> generate an empty one")
			tmpFile = open(readmeFileDest, 'w')
			tmpFile.write("No documentation for " + pkgName + "\n")
			tmpFile.flush()
			tmpFile.close()
		## Create licence file
		licenseFileDest = target_outpath + "/license/"+ debianPkgName + ".txt"
		tools.create_directory_of_file(licenseFileDest)
		if os.path.exists(basePkgPath + "/license.txt")==True:
			tools.copy_file(basePkgPath + "/license.txt", licenseFileDest)
		else:
			debug.info("no file 'license.txt' ==> generate an empty one")
			tmpFile = open(licenseFileDest, 'w')
			tmpFile.write("No license define by the developper for " + pkgName + "\n")
			tmpFile.flush()
			tmpFile.close()
		## Create changeLog file
		changeLogFileDest = target_outpath + "/changelog.txt"
		if os.path.exists(basePkgPath + "/changelog") == True:
			tools.copy_file(basePkgPath + "/changelog", changeLogFileDest)
		else:
			debug.info("no file 'changelog' ==> generate an empty one")
			tmpFile = open(changeLogFileDest, 'w')
			tmpFile.write("No changelog data " + pkgName + "\n")
			tmpFile.flush()
			tmpFile.close()
		## copy share path
		#debug.info("plop:" + self.get_staging_path(pkgName) + self.path_data)
		if os.path.exists(self.get_staging_path(pkgName) + self.path_data) == True:
			tools.copy_anything(self.get_staging_path(pkgName) + self.path_data + "/*", target_outpath + self.path_data, recursive=True)
		
		## Create binary path:
		bin_path = target_outpath + self.path_bin
		#tools.create_directory_of_file(bin_path)
		tools.copy_anything(self.get_staging_path(pkgName) + self.path_bin + "/*",
		                    bin_path)
		
		## create the package:
		debug.debug("package : " + self.get_staging_path(pkgName) + "/" + debianPkgName + ".app.pkg")
		os.system("cd " + self.get_staging_path(pkgName) + " ; tar -czf " + pkgName + ".app.tar.gz " + pkgName + ".app")
		#multiprocess.run_command("cd " + self.get_staging_path(pkgName) + " ; tar -czf " + pkgName + ".app.tar.gz " + pkgName + ".app")
		tools.create_directory_of_file(self.get_final_path())
		tools.copy_file(self.get_staging_path(pkgName) + "/" + pkgName + ".app.tar.gz", self.get_final_path() + "/" + pkgName + ".app.gpkg")
		


