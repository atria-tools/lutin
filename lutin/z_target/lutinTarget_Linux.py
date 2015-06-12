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
	
	def make_package(self, pkgName, pkgProperties, basePkgPath):
		# http://alp.developpez.com/tutoriels/debian/creer-paquet/
		debianPkgName = re.sub("_", "-", pkgName)
		debug.debug("------------------------------------------------------------------------")
		debug.info("Generate package '" + debianPkgName + "' v"+pkgProperties["VERSION"])
		debug.debug("------------------------------------------------------------------------")
		self.get_staging_folder(pkgName)
		targetOutFolderDebian = self.get_staging_folder(pkgName) + "/DEBIAN/"
		finalFileControl = targetOutFolderDebian + "control"
		finalFilepostRm = targetOutFolderDebian + "postrm"
		# create the folders :
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
		readmeFileDest = self.get_staging_folder(pkgName) + "/usr/share/doc/"+ debianPkgName + "/README"
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
		licenseFileDest = self.get_staging_folder(pkgName) + "/usr/share/doc/"+ debianPkgName + "/copyright"
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
		changeLogFileDest = self.get_staging_folder(pkgName) + "/usr/share/doc/"+ debianPkgName + "/changelog"
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
		debug.debug("package : " + self.get_staging_folder(pkgName) + "/" + debianPkgName + ".deb")
		os.system("cd " + self.get_staging_folder("") + " ; dpkg-deb --build " + pkgName)
		tools.create_directory_of_file(self.get_final_folder())
		tools.copy_file(self.get_staging_folder("") + "/" + pkgName + self.suffix_package, self.get_final_folder() + "/" + pkgName + self.suffix_package)
	
	def install_package(self, pkgName):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Install package '" + pkgName + "'")
		debug.debug("------------------------------------------------------------------------")
		os.system("sudo dpkg -i " + self.get_final_folder() + "/" + pkgName + self.suffix_package)
	
	def un_install_package(self, pkgName):
		debug.debug("------------------------------------------------------------------------")
		debug.info("Un-Install package '" + pkgName + "'")
		debug.debug("------------------------------------------------------------------------")
		os.system("sudo dpkg -r " + self.get_final_folder() + "/" + pkgName + self.suffix_package)
