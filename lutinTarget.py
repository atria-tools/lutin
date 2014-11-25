#!/usr/bin/python
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##

import sys
import os
import inspect
import fnmatch
import lutinDebug as debug
import datetime
import lutinTools
import lutinModule
import lutinImage
import lutinHost

class Target:
	def __init__(self, name, config, arch):
		self.config = config
		
		#processor type selection (auto/arm/ppc/x86)
		self.selectArch = config["arch"]; # TODO : Remove THIS ...
		#bus size selection (auto/32/64)
		self.selectBus = config["bus-size"]; # TODO : Remove THIS ...
		
		if config["bus-size"] == "auto":
			debug.error("system error ==> must generate the default 'bus-size' config")
		if config["arch"] == "auto":
			debug.error("system error ==> must generate the default 'bus-size' config")
		
		debug.debug("config=" + str(config))
		if arch != "":
			self.arch = "-arch " + arch
		else:
			self.arch = ""
		
		# todo : remove this :
		self.sumulator = config["simulation"]
		self.name=name
		self.endGeneratePackage = config["generate-package"]
		debug.info("=================================");
		debug.info("== Target='" + self.name + "' " + config["bus-size"] + " bits for arch '" + config["arch"] + "'");
		debug.info("=================================");
		
		self.set_cross_base()
		
		###############################################################################
		# Target global variables.
		###############################################################################
		self.global_include_cc=[]
		self.global_flags_cc=['-D__TARGET_OS__'+self.name,
		                      '-D__TARGET_ARCH__'+self.selectArch,
		                      '-D__TARGET_ADDR__'+self.selectBus + 'BITS',
		                      '-D_REENTRANT']
		
		if self.name != "Windows":
			self.global_flags_xx=['-std=c++11']
			self.global_flags_mm=['-std=c++11']
		else:
			self.global_flags_xx=['-static-libgcc', '-static-libstdc++', '-std=c++11']
			self.global_flags_mm=[]
		self.global_flags_m=[]
		self.global_flags_ar=['rcs']
		self.global_flags_ld=[]
		self.global_flags_ld_shared=[]
		self.global_libs_ld=[]
		self.global_libs_ld_shared=[]
		
		self.global_sysroot=""
		
		self.suffix_cmdLine='.cmd'
		self.suffix_dependence='.d'
		self.suffix_obj='.o'
		self.suffix_lib_static='.a'
		self.suffix_lib_dynamic='.so'
		self.suffix_binary=''
		self.suffix_package='.deb'
		
		self.folder_arch="/" + self.name
		
		if "debug" == self.config["mode"]:
			self.global_flags_cc.append("-g")
			self.global_flags_cc.append("-DDEBUG")
			self.global_flags_cc.append("-O0")
		else:
			self.global_flags_cc.append("-DNDEBUG")
			self.global_flags_cc.append("-O3")
		
		## To add code coverate on build result system
		if self.config["gcov"] == True:
			self.global_flags_cc.append("-fprofile-arcs")
			self.global_flags_cc.append("-ftest-coverage")
			self.global_flags_ld.append("-fprofile-arcs")
			self.global_flags_ld.append("-ftest-coverage")
		
		self.update_folder_tree()
		self.folder_bin="/usr/bin"
		self.folder_lib="/usr/lib"
		self.folder_data="/usr/share"
		self.folder_doc="/usr/share/doc"
		self.buildDone=[]
		self.buildTreeDone=[]
		self.moduleList=[]
		# output staging files list :
		self.listFinalFile=[]
		
		self.sysroot=""
		
		self.externProjectManager = None
	
	def update_folder_tree(self):
		self.folder_out="/out/" + self.name + "_" + self.config["arch"] + "_" + self.config["bus-size"] + "/" + self.config["mode"]
		self.folder_final="/final/" + self.config["compilator"]
		self.folder_staging="/staging/" + self.config["compilator"]
		self.folder_build="/build/" + self.config["compilator"]
	
	def set_cross_base(self, cross=""):
		self.cross = cross
		debug.debug("== Target='" + self.cross + "'");
		self.ar = self.cross + "ar"
		self.ranlib = self.cross + "ranlib"
		if self.config["compilator"] == "clang":
			self.cc = self.cross + "clang"
			self.xx = self.cross + "clang++"
			#self.ar=self.cross + "llvm-ar"
			#self.ranlib="ls"
		else:
			self.cc = self.cross + "gcc"
			self.xx = self.cross + "g++"
			#self.ar=self.cross + "ar"
			#self.ranlib=self.cross + "ranlib"
		self.ld = self.cross + "ld"
		self.nm = self.cross + "nm"
		self.strip = self.cross + "strip"
		self.dlltool = self.cross + "dlltool"
		self.update_folder_tree()
	
	def set_use_of_extern_build_tool(self, mode):
		if mode == True:
			if self.externProjectManager == None:
				debug.error("This target does not support extern tool")
		else:
			# remove extern tool generator...
			self.externProjectManager = None
	
	def get_build_mode(self):
		return self.config["mode"]
	
	def add_image_staging(self, inputFile, outputFile, sizeX, sizeY, cmdFile=None):
		for source, dst, x, y, cmdFile2 in self.listFinalFile:
			if dst == outputFile :
				debug.verbose("already added : " + outputFile)
				return
		debug.verbose("add file : '" + inputFile + "' ==> '" + outputFile + "'")
		self.listFinalFile.append([inputFile,outputFile, sizeX, sizeY, cmdFile])
	
	def add_file_staging(self, inputFile, outputFile, cmdFile=None):
		for source, dst, x, y, cmdFile2 in self.listFinalFile:
			if dst == outputFile :
				debug.verbose("already added : " + outputFile)
				return
		debug.verbose("add file : '" + inputFile + "' ==> '" + outputFile + "'");
		self.listFinalFile.append([inputFile, outputFile, -1, -1, cmdFile])
	
	def copy_to_staging(self, binaryName):
		baseFolder = self.get_staging_folder_data(binaryName)
		for source, dst, x, y, cmdFile in self.listFinalFile:
			if     cmdFile != None \
			   and cmdFile != "":
				debug.verbose("cmd file " + cmdFile)
			if x == -1:
				debug.verbose("must copy file : '" + source + "' ==> '" + dst + "'");
				lutinTools.copy_file(source, baseFolder+"/"+dst, cmdFile)
			else:
				debug.verbose("resize image : '" + source + "' ==> '" + dst + "' size=(" + str(x) + "," + str(y) + ")");
				lutinImage.resize(source, baseFolder+"/"+dst, x, y, cmdFile)
	
	
	def clean_module_tree(self):
		self.buildTreeDone = []
		self.listFinalFile = []
	
	
	# TODO : Remove this hack ... ==> really bad ... but usefull
	def set_ewol_folder(self, folder):
		self.folder_ewol = folder
	
	
	def file_generate_object(self,binaryName,moduleName,basePath,file):
		list=[]
		list.append(basePath + "/" + file)
		list.append(self.get_build_folder(moduleName) + "/" + file + self.suffix_obj)
		list.append(self.get_build_folder(moduleName) + "/" + file + self.suffix_dependence)
		list.append(self.get_build_folder(moduleName) + "/" + file + self.suffix_cmdLine)
		return list
	"""
		return a list of 3 elements :
			0 : sources files (can be a list)
			1 : destination file
			2 : dependence files module (*.d)
	"""
	def generate_file(self,binaryName,moduleName,basePath,file,type):
		list=[]
		if (type=="bin"):
			list.append(file)
			list.append(self.get_staging_folder(binaryName) + "/" + self.folder_bin + "/" + moduleName + self.suffix_binary)
			list.append(self.get_build_folder(moduleName) + "/" + moduleName + self.suffix_dependence)
			list.append(self.get_build_folder(binaryName) + "/" + self.folder_bin + "/" + moduleName + self.suffix_cmdLine)
		elif (type=="lib-shared"):
			list.append(file)
			list.append(self.get_staging_folder(binaryName) + "/" + self.folder_lib + "/" + moduleName + self.suffix_lib_dynamic)
			list.append(self.get_build_folder(moduleName) + "/" + moduleName + self.suffix_dependence)
			list.append(self.get_build_folder(binaryName) + "/" + self.folder_lib + "/" + moduleName + self.suffix_cmdLine)
		elif (type=="lib-static"):
			list.append(file)
			list.append(self.get_build_folder(moduleName) + "/" + moduleName + self.suffix_lib_static)
			list.append(self.get_build_folder(moduleName) + "/" + moduleName + self.suffix_dependence)
			list.append(self.get_build_folder(moduleName) + "/" + moduleName + self.suffix_cmdLine)
		elif (type=="image"):
			list.append(self.get_build_folder(binaryName) + "/data/" + file + self.suffix_cmdLine)
		else:
			debug.error("unknow type : " + type)
		return list
	
	def get_final_folder(self):
		return lutinTools.get_run_folder() + self.folder_out + self.folder_final
	
	def get_staging_folder(self, binaryName):
		return lutinTools.get_run_folder() + self.folder_out + self.folder_staging + "/" + binaryName
	
	def get_staging_folder_data(self, binaryName):
		return self.get_staging_folder(binaryName) + self.folder_data + "/" + binaryName
	
	def get_build_folder(self, moduleName):
		return lutinTools.get_run_folder() + self.folder_out + self.folder_build + "/" + moduleName
	
	def get_doc_folder(self, moduleName):
		return lutinTools.get_run_folder() + self.folder_out + self.folder_doc + "/" + moduleName
	
	def is_module_build(self,module):
		for mod in self.buildDone:
			if mod == module:
				return True
		self.buildDone.append(module)
		return False
	
	def is_module_buildTree(self,module):
		for mod in self.buildTreeDone:
			if mod == module:
				return True
		self.buildTreeDone.append(module)
		return False
	
	def add_module(self, newModule):
		debug.debug("Import nodule for Taget : " + newModule.name)
		self.moduleList.append(newModule)
	
	
	# return inherit packages ...
	"""
	def build(self, name, packagesName):
		for module in self.moduleList:
			if module.name == name:
				return module.build(self, packagesName)
		debug.error("request to build an un-existant module name : '" + name + "'")
	"""
	
	def build_tree(self, name, packagesName):
		for module in self.moduleList:
			if module.name == name:
				module.build_tree(self, packagesName)
				return
		debug.error("request to build tree on un-existant module name : '" + name + "'")
	
	def clean(self, name):
		for module in self.moduleList:
			if module.name == name:
				module.clean(self)
				return
		debug.error("request to clean an un-existant module name : '" + name + "'")
	
	def load_if_needed(self, name):
		for elem in self.moduleList:
			if elem.name == name:
				return
		lutinModule.load_module(self, name)
	
	def load_all(self):
		listOfAllTheModule = lutinModule.list_all_module()
		for modName in listOfAllTheModule:
			self.load_if_needed(modName)
	
	def project_add_module(self, name, projectMng, addedModule):
		for module in self.moduleList:
			if module.name == name:
				module.ext_project_add_module(self, projectMng, addedModule)
				return
	
	def build(self, name, packagesName=None):
		if name == "dump":
			debug.info("dump all")
			self.load_all()
			for mod in self.moduleList:
				mod.display(self)
		elif self.externProjectManager != None:
			# TODO : Do it only if needed:
			debug.debug("generate project")
			# TODO : Set an option to force Regeneration of the project or the oposite....
			self.load_all()
			for mod in self.moduleList:
				if mod.name != "edn":
					continue
				if mod.type == "PACKAGE":
					mod.create_project(self, self.externProjectManager)
			# TODO : Run project or do something else ...
			debug.error("stop here ...")
		else:
			if name == "all":
				debug.info("build all")
				self.load_all()
				for mod in self.moduleList:
					if self.name=="Android":
						if mod.type == "PACKAGE":
							mod.build(self, None)
					else:
						if    mod.type == "BINARY" \
						   or mod.type == "PACKAGE":
							mod.build(self, None)
			elif name == "clean":
				debug.info("clean all")
				self.load_all()
				for mod in self.moduleList:
					mod.clean(self)
			else:
				# get the action an the module ....
				gettedElement = name.split("-")
				moduleName = gettedElement[0]
				if len(gettedElement)>=2:
					actionName = gettedElement[1]
				else :
					actionName = "build"
				debug.verbose("requested : " + moduleName + "-" + actionName)
				if actionName == "install":
					self.build(moduleName + "-build")
					self.install_package(moduleName)
				elif actionName == "uninstall":
					self.un_install_package(moduleName)
				elif actionName == "log":
					self.Log(moduleName)
				else:
					self.load_if_needed(moduleName)
					# clean requested
					for mod in self.moduleList:
						if mod.name == moduleName:
							if actionName == "dump":
								debug.info("dump module '" + moduleName + "'")
								return mod.display(self)
							elif actionName == "clean":
								debug.info("clean module '" + moduleName + "'")
								return mod.clean(self)
							elif actionName == "build":
								debug.debug("build module '" + moduleName + "'")
								return mod.build(self, None)
					debug.error("not know module name : '" + moduleName + "' to '" + actionName + "' it")
	

targetList=[]
__startTargetName="lutinTarget_"


def import_path(path):
	global targetList
	matches = []
	debug.debug('Start find sub File : "%s"' %path)
	for root, dirnames, filenames in os.walk(path):
		tmpList = fnmatch.filter(filenames, __startTargetName + "*.py")
		# Import the module :
		for filename in tmpList:
			debug.debug('    Find a file : "%s"' %os.path.join(root, filename))
			#matches.append(os.path.join(root, filename))
			sys.path.append(os.path.dirname(os.path.join(root, filename)) )
			targetName = filename.replace('.py', '')
			targetName = targetName.replace(__startTargetName, '')
			debug.debug("integrate module: '" + targetName + "' from '" + os.path.join(root, filename) + "'")
			targetList.append([targetName,os.path.join(root, filename)])


def load_target(name, config):
	global targetList
	debug.debug("load target: " + name)
	if len(targetList) == 0:
		debug.error("No target to compile !!!")
	debug.debug("list target: " + str(targetList))
	for mod in targetList:
		if mod[0] == name:
			debug.verbose("add to path: '" + os.path.dirname(mod[1]) + "'")
			sys.path.append(os.path.dirname(mod[1]))
			debug.verbose("import target : '" + __startTargetName + name + "'")
			theTarget = __import__(__startTargetName + name)
			#create the target
			tmpTarget = theTarget.Target(config)
			#tmpTarget.set_use_of_extern_build_tool(externBuild)
			return tmpTarget

def list_all_target():
	global targetList
	tmpListName = []
	for mod in targetList:
		tmpListName.append(mod[0])
	return tmpListName

def list_all_target_with_desc():
	global targetList
	tmpList = []
	for mod in targetList:
		sys.path.append(os.path.dirname(mod[1]))
		theTarget = __import__(__startTargetName + mod[0])
		try:
			tmpdesc = theTarget.get_desc()
			tmpList.append([mod[0], tmpdesc])
		except:
			debug.warning("has no name : " + mod[0])
			tmpList.append([mod[0], ""])
	return tmpList
