#!/usr/bin/python
import lutinDebug as debug
import lutinTarget
import lutinTools
import os
import stat
import lutinMultiprocess

class Target(lutinTarget.Target):
	def __init__(self, typeCompilator, debugMode, generatePackage, sumulator=False):
		lutinTarget.Target.__init__(self, "Linux", typeCompilator, debugMode, generatePackage, "", "")
	
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
		debug.debug("------------------------------------------------------------------------")
		debug.info("Generate package '" + pkgName + "' v"+pkgProperties["VERSION"])
		debug.debug("------------------------------------------------------------------------")
		self.get_staging_folder(pkgName)
		targetOutFolderDebian=self.get_staging_folder(pkgName) + "/DEBIAN/"
		finalFileControl = targetOutFolderDebian + "control"
		finalFilepostRm = targetOutFolderDebian + "postrm"
		# create the folders :
		lutinTools.create_directory_of_file(finalFileControl)
		lutinTools.create_directory_of_file(finalFilepostRm)
		## Create the control file
		tmpFile = open(finalFileControl, 'w')
		tmpFile.write("Package: " + pkgName + "\n")
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
		readmeFileDest = self.get_staging_folder(pkgName) + "/usr/share/doc/"+ pkgName + "/README"
		if os.path.exists(basePkgPath + "/os-Linux/README")==True:
			lutinTools.copy_file(basePkgPath + "/os-Linux/README", readmeFileDest)
		elif os.path.exists(basePkgPath + "/README")==True:
			lutinTools.copy_file(basePkgPath + "/README", readmeFileDest)
		elif os.path.exists(basePkgPath + "/README.md")==True:
			lutinTools.copy_file(basePkgPath + "/README.md", readmeFileDest)
		else:
			debug.info("no file 'README', 'README.md' or 'os-Linux/README' ==> generate an empty one")
			tmpFile = open(readmeFileDest, 'w')
			tmpFile.write("No documentation for " + pkgName + "\n")
			tmpFile.flush()
			tmpFile.close()
		## licence file
		licenseFileDest = self.get_staging_folder(pkgName) + "/usr/share/doc/"+ pkgName + "/copyright"
		if os.path.exists(basePkgPath + "/license.txt")==True:
			lutinTools.copy_file(basePkgPath + "/license.txt", licenseFileDest)
		else:
			debug.info("no file 'license.txt' ==> generate an empty one")
			tmpFile = open(licenseFileDest, 'w')
			tmpFile.write("No license define by the developper for " + pkgName + "\n")
			tmpFile.flush()
			tmpFile.close()
		##changeLog file
		changeLogFileDest = self.get_staging_folder(pkgName) + "/usr/share/doc/"+ pkgName + "/changelog"
		if os.path.exists(basePkgPath + "/changelog")==True:
			lutinTools.copy_file(basePkgPath + "/changelog", changeLogFileDest)
		else:
			debug.info("no file 'changelog' ==> generate an empty one")
			lutinMultiprocess.run_command("git log > " + changeLogFileDest)
		## create the package :
		debug.debug("pachage : " + self.get_staging_folder(pkgName) + "/" + pkgName + ".deb")
		os.system("cd " + self.get_staging_folder("") + " ; dpkg-deb --build " + pkgName)
		lutinTools.create_directory_of_file(self.get_final_folder())
		lutinTools.copy_file(self.get_staging_folder("") + "/" + pkgName + self.suffix_package, self.get_final_folder() + "/" + pkgName + self.suffix_package)
	
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
