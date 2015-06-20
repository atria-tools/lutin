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
import datetime
# Local import
from . import debug
from . import heritage
from . import tools
from . import module
from . import system
from . import image
from . import multiprocess

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
		
		self.global_flags_xx=[]
		self.global_flags_mm=[]
		if self.name == "Windows":
			self.global_flags_xx=['-static-libgcc', '-static-libstdc++']
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
		
		self.folder_generate_code="/generate_header"
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
		
		self.action_on_state={}
	
	def update_folder_tree(self):
		self.folder_out="/out/" + self.name + "_" + self.config["arch"] + "_" + self.config["bus-size"] + "/" + self.config["mode"]
		self.folder_final="/final/" + self.config["compilator"]
		self.folder_staging="/staging/" + self.config["compilator"]
		self.folder_build="/build/" + self.config["compilator"]
	
	def create_number_from_version_string(self, data):
		list = data.split(".")
		if len(list) == 1:
			list.append("0")
		if len(list) == 2:
			list.append("0")
		if len(list) > 3:
			list = list[:3]
		out = 0;
		offset = 1000**(len(list)-1)
		for elem in list:
			out += offset*int(elem)
			debug.verbose("get : " + str(int(elem)) + " tmp" + str(out))
			offset /= 1000
		return out
	
	def set_cross_base(self, cross=""):
		self.cross = cross
		debug.debug("== Target='" + self.cross + "'");
		self.java = "javac"
		self.javah = "javah"
		self.jar = "jar"
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
		
		#get g++ compilation version :
		ret = multiprocess.run_command_direct(self.xx + " -dumpversion");
		if ret == False:
			debug.error("Can not get the g++/clang++ version ...")
		self.xx_version = self.create_number_from_version_string(ret)
		debug.verbose(self.config["compilator"] + "++ version=" + str(ret) + " number=" + str(self.xx_version))
		
		self.ld = self.cross + "ld"
		self.nm = self.cross + "nm"
		self.strip = self.cross + "strip"
		self.dlltool = self.cross + "dlltool"
		self.update_folder_tree()
	
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
				tools.copy_file(source, baseFolder+"/"+dst, cmdFile)
			else:
				debug.verbose("resize image : '" + source + "' ==> '" + dst + "' size=(" + str(x) + "," + str(y) + ")");
				image.resize(source, baseFolder+"/"+dst, x, y, cmdFile)
	
	
	def clean_module_tree(self):
		self.buildTreeDone = []
		self.listFinalFile = []
	
	
	# TODO : Remove this hack ... ==> really bad ... but usefull
	def set_ewol_folder(self, folder):
		self.folder_ewol = folder
	
	
	def get_full_name_source(self, basePath, file):
		if file[0] == '/':
			if tools.os.path.isfile(file):
				return file
		return basePath + "/" + file
	
	def get_full_name_cmd(self, moduleName, basePath, file):
		if file[0] == '/':
			if tools.os.path.isfile(file):
				return file + self.suffix_cmdLine
		return self.get_build_folder(moduleName) + "/" + file + self.suffix_cmdLine
	
	def get_full_name_destination(self, moduleName, basePath, file, suffix, remove_suffix=False):
		# special patch for java file:
		if file[-4:] == "java":
			for elem in ["org/", "com/"]:
				pos = file.find(elem);
				if pos > 0:
					file = file[pos:]
		if remove_suffix == True:
			file = file[:file.rfind(".")] + '.'
		else:
			file += "."
		if len(suffix) >= 1:
			suffix = suffix[0]
		else:
			suffix = ""
		return self.get_build_folder(moduleName) + "/" + file + suffix
	
	def get_full_dependency(self, moduleName, basePath, file):
		return self.get_build_folder(moduleName) + "/" + file + self.suffix_dependence
	
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
			list.append(self.get_build_folder(binaryName) + "/" + self.folder_bin + "/" + moduleName + self.suffix_binary + self.suffix_cmdLine)
		elif (type=="lib-shared"):
			list.append(file)
			list.append(self.get_staging_folder(binaryName) + "/" + self.folder_lib + "/" + moduleName + self.suffix_lib_dynamic)
			list.append(self.get_build_folder(moduleName) + "/" + moduleName + self.suffix_dependence)
			list.append(self.get_build_folder(binaryName) + "/" + self.folder_lib + "/" + moduleName + self.suffix_lib_dynamic + self.suffix_cmdLine)
		elif (type=="lib-static"):
			list.append(file)
			list.append(self.get_build_folder(moduleName) + "/" + moduleName + self.suffix_lib_static)
			list.append(self.get_build_folder(moduleName) + "/" + moduleName + self.suffix_dependence)
			list.append(self.get_build_folder(moduleName) + "/" + moduleName + self.suffix_lib_static + self.suffix_cmdLine)
		elif (type=="jar"):
			list.append(file)
			list.append(self.get_build_folder(moduleName) + "/" + moduleName + ".jar")
			list.append(self.get_build_folder(moduleName) + "/" + moduleName + ".jar" + self.suffix_dependence)
			list.append(self.get_build_folder(moduleName) + "/" + moduleName + ".jar" + self.suffix_cmdLine)
		elif (type=="image"):
			list.append(self.get_build_folder(binaryName) + "/data/" + file + self.suffix_cmdLine)
		else:
			debug.error("unknow type : " + type)
		return list
	
	def get_final_folder(self):
		return tools.get_run_folder() + self.folder_out + self.folder_final
	
	def get_staging_folder(self, binaryName):
		return tools.get_run_folder() + self.folder_out + self.folder_staging + "/" + binaryName
	
	def get_staging_folder_data(self, binaryName):
		return self.get_staging_folder(binaryName) + self.folder_data + "/" + binaryName
	
	def get_build_folder(self, moduleName):
		return tools.get_run_folder() + self.folder_out + self.folder_build + "/" + moduleName
	
	def get_doc_folder(self, moduleName):
		return tools.get_run_folder() + self.folder_out + self.folder_doc + "/" + moduleName
	
	def is_module_build(self, my_module):
		for mod in self.buildDone:
			if mod == my_module:
				return True
		self.buildDone.append(my_module)
		return False
	
	def is_module_buildTree(self, my_module):
		for mod in self.buildTreeDone:
			if mod == my_module:
				return True
		self.buildTreeDone.append(my_module)
		return False
	
	def add_module(self, newModule):
		debug.debug("Add nodule for Taget : " + newModule.name)
		self.moduleList.append(newModule)
	
	def get_module(self, name):
		for mod in self.buildDone:
			if mod.name == name:
				return mod
		debug.error("the module '" + str(name) + "'does not exist/already build")
		return None
	
	# return inherit packages ...
	"""
	def build(self, name, packagesName):
		for module in self.moduleList:
			if module.name == name:
				return module.build(self, packagesName)
		debug.error("request to build an un-existant module name : '" + name + "'")
	"""
	
	def build_tree(self, name, packagesName):
		for mod in self.moduleList:
			if mod.name == name:
				mod.build_tree(self, packagesName)
				return
		debug.error("request to build tree on un-existant module name : '" + name + "'")
	
	def clean(self, name):
		for mod in self.moduleList:
			if mod.name == name:
				mod.clean(self)
				return
		debug.error("request to clean an un-existant module name : '" + name + "'")
	
	def load_if_needed(self, name, optionnal=False):
		for elem in self.moduleList:
			if elem.name == name:
				return True
		# TODO : Check internal module and system module ...
		# need to import the module (or the system module ...)
		exist = system.exist(name, self.name, self)
		if exist == True:
			system.load(self, name, self.name)
			return True;
		# try to find in the local Modules:
		exist = module.exist(self, name)
		if exist == True:
			module.load_module(self, name)
			return True;
		else:
			return False;
	
	def load_all(self):
		listOfAllTheModule = module.list_all_module()
		for modName in listOfAllTheModule:
			self.load_if_needed(modName)
	
	def project_add_module(self, name, projectMng, addedModule):
		for mod in self.moduleList:
			if mod.name == name:
				mod.ext_project_add_module(self, projectMng, addedModule)
				return
	
	def build(self, name, packagesName=None, optionnal=False):
		if name == "dump":
			debug.info("dump all")
			self.load_all()
			for mod in self.moduleList:
				mod.display(self)
			return
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
			gettedElement = name.split("?")
			moduleName = gettedElement[0]
			if len(gettedElement)>=2:
				actionName = gettedElement[1]
			else :
				actionName = "build"
			debug.verbose("requested : " + moduleName + "?" + actionName)
			if actionName == "install":
				self.build(moduleName + "?build")
				self.install_package(moduleName)
			elif actionName == "uninstall":
				self.un_install_package(moduleName)
			elif actionName == "log":
				self.Log(moduleName)
			else:
				present = self.load_if_needed(moduleName, optionnal=optionnal)
				if     present == False \
				   and optionnal == True:
					return [heritage.HeritageList(), False]
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
							if optionnal == True:
								return [mod.build(self, None), True]
							return mod.build(self, None)
				if optionnal == True:
					return [heritage.HeritageList(), False]
				debug.error("not know module name : '" + moduleName + "' to '" + actionName + "' it")
	
	def add_action(self, name_of_state="PACKAGE", action=None):
		if name_of_state not in self.action_on_state:
			self.action_on_state[name_of_state] = [action]
		else:
			self.action_on_state[name_of_state].append(action)


targetList=[]
__startTargetName="lutinTarget_"


def import_path(path):
	global targetList
	matches = []
	debug.debug('TARGET: Start find sub File : "%s"' %path)
	for root, dirnames, filenames in os.walk(path):
		tmpList = fnmatch.filter(filenames, __startTargetName + "*.py")
		# Import the module :
		for filename in tmpList:
			debug.debug('TARGET:     Find a file : "%s"' %os.path.join(root, filename))
			#matches.append(os.path.join(root, filename))
			sys.path.append(os.path.dirname(os.path.join(root, filename)) )
			targetName = filename.replace('.py', '')
			targetName = targetName.replace(__startTargetName, '')
			debug.debug("TARGET:     integrate module: '" + targetName + "' from '" + os.path.join(root, filename) + "'")
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
			return tmpTarget
	raise KeyError("No entry for : " + name)

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
