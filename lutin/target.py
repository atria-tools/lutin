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
		self.select_arch = config["arch"]; # TODO : Remove THIS ...
		#bus size selection (auto/32/64)
		self.select_bus = config["bus-size"]; # TODO : Remove THIS ...
		
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
		self.name = name
		self.end_generate_package = config["generate-package"]
		debug.info("=================================");
		debug.info("== Target='" + self.name + "' " + config["bus-size"] + " bits for arch '" + config["arch"] + "'");
		debug.info("=================================");
		
		self.set_cross_base()
		
		###############################################################################
		# Target global variables.
		###############################################################################
		self.global_include_cc=[]
		self.global_flags_cc=['-D__TARGET_OS__'+self.name,
		                      '-D__TARGET_ARCH__'+self.select_arch,
		                      '-D__TARGET_ADDR__'+self.select_bus + 'BITS',
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
		
		self.suffix_cmd_line='.cmd'
		self.suffix_warning='.warning'
		self.suffix_dependence='.d'
		self.suffix_obj='.o'
		self.suffix_lib_static='.a'
		self.suffix_lib_dynamic='.so'
		self.suffix_binary=''
		self.suffix_package='.deb'
		
		self.path_generate_code="/generate_header"
		self.path_arch="/" + self.name
		
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
		
		self.update_path_tree()
		"""
		self.path_bin="usr/bin"
		self.path_lib="usr/lib"
		self.path_data="usr/share"
		self.path_doc="usr/share/doc"
		"""
		self.path_bin="bin"
		self.path_lib="lib"
		self.path_data="share"
		self.path_doc="doc"
		self.path_include="include"
		self.path_object="obj"
		
		
		self.build_done=[]
		self.build_tree_done=[]
		self.module_list=[]
		# output staging files list :
		self.list_final_file=[]
		
		self.sysroot=""
		
		self.action_on_state={}
	
	def update_path_tree(self):
		self.path_out = os.path.join("out", self.name + "_" + self.config["arch"] + "_" + self.config["bus-size"], self.config["mode"])
		self.path_final = os.path.join("final", self.config["compilator"])
		self.path_staging = os.path.join("staging", self.config["compilator"])
		self.path_build = os.path.join("build", self.config["compilator"])
	
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
			self.ar=self.cross + "llvm-ar"
			self.ranlib=""
		else:
			self.cc = self.cross + "gcc"
			self.xx = self.cross + "g++"
			#self.ar=self.cross + "ar"
			#self.ranlib=self.cross + "ranlib"
		if self.config["compilator-version"] != "":
			self.cc = self.cc + "-" + self.config["compilator-version"]
			self.xx = self.xx + "-" + self.config["compilator-version"]
		
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
		self.update_path_tree()
	
	def get_build_mode(self):
		return self.config["mode"]
	
	## @deprecated ...
	def add_image_staging(self, inputFile, outputFile, sizeX, sizeY, cmdFile=None):
		for source, dst, x, y, cmdFile2 in self.list_final_file:
			if dst == outputFile :
				debug.verbose("already added : " + outputFile)
				return
		debug.verbose("add file : '" + inputFile + "' ==> '" + outputFile + "'")
		self.list_final_file.append([inputFile,outputFile, sizeX, sizeY, cmdFile])
	
	## @deprecated ...
	def add_file_staging(self, inputFile, outputFile, cmdFile=None):
		for source, dst, x, y, cmdFile2 in self.list_final_file:
			if dst == outputFile :
				debug.verbose("already added : " + outputFile)
				return
		debug.verbose("add file : '" + inputFile + "' ==> '" + outputFile + "'");
		self.list_final_file.append([inputFile, outputFile, -1, -1, cmdFile])
	
	## @deprecated ...
	def copy_to_staging(self, binary_name):
		base_path = self.get_staging_path_data(binary_name)
		for source, dst, x, y, cmdFile in self.list_final_file:
			if     cmdFile != None \
			   and cmdFile != "":
				debug.verbose("cmd file " + cmdFile)
			if x == -1:
				debug.verbose("must copy file : '" + source + "' ==> '" + dst + "'");
				tools.copy_file(source, os.path.join(base_path, dst), cmdFile)
			else:
				debug.verbose("resize image : '" + source + "' ==> '" + dst + "' size=(" + str(x) + "," + str(y) + ")");
				image.resize(source, os.path.join(base_path, dst), x, y, cmdFile)
	
	
	def clean_module_tree(self):
		self.build_tree_done = []
		self.list_final_file = []
	
	def get_full_name_source(self, basePath, file):
		if file[0] == '/':
			if tools.os.path.isfile(file):
				return file
		return basePath + "/" + file
	
	def get_full_name_cmd(self, module_name, basePath, file):
		if file[0] == '/':
			if tools.os.path.isfile(file):
				return file + self.suffix_cmd_line
		return self.get_build_path_object(module_name) + "/" + file + self.suffix_cmd_line
	
	def get_full_name_warning(self, module_name, basePath, file):
		return self.get_build_path_object(module_name) + "/" + file + self.suffix_warning;
	
	def get_full_name_destination(self, module_name, basePath, file, suffix, remove_suffix=False):
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
		return self.get_build_path_object(module_name) + "/" + file + suffix
	
	def get_full_dependency(self, module_name, basePath, file):
		return self.get_build_path_object(module_name) + "/" + file + self.suffix_dependence
	
	"""
		return a list of 3 elements :
			0 : sources files (can be a list)
			1 : destination file
			2 : dependence files module (*.d)
	"""
	def generate_file(self,
	                  binary_name,
	                  module_name,
	                  basePath,
	                  file,
	                  type):
		#debug.warning("genrate_file(" + str(binary_name) + "," + str(module_name) + "," + str(basePath) + "," + str(file) + "," + str(type) + ")")
		list=[]
		if (type=="bin"):
			list.append(file)
			list.append(self.get_build_file_bin(binary_name))
			list.append(os.path.join(self.get_build_path(module_name), module_name + self.suffix_dependence))
			list.append(os.path.join(self.get_build_path(binary_name), self.path_bin, module_name + self.suffix_binary + self.suffix_cmd_line))
			list.append(os.path.join(self.get_build_path(binary_name), self.path_bin, module_name + self.suffix_binary + self.suffix_warning))
		elif (type=="lib-shared"):
			list.append(file)
			list.append(os.path.join(self.get_build_path(module_name), self.path_lib, module_name + self.suffix_lib_dynamic))
			list.append(os.path.join(self.get_build_path(module_name), self.path_lib, module_name + self.suffix_dependence))
			list.append(os.path.join(self.get_build_path(module_name), self.path_lib, module_name + self.suffix_lib_dynamic + self.suffix_cmd_line))
			list.append(os.path.join(self.get_build_path(module_name), self.path_lib, module_name + self.suffix_lib_dynamic + self.suffix_warning))
		elif (type=="lib-static"):
			list.append(file)
			list.append(os.path.join(self.get_build_path(module_name), self.path_lib, module_name + self.suffix_lib_static))
			list.append(os.path.join(self.get_build_path(module_name), self.path_lib, module_name + self.suffix_dependence))
			list.append(os.path.join(self.get_build_path(module_name), self.path_lib, module_name + self.suffix_lib_static + self.suffix_cmd_line))
			list.append(os.path.join(self.get_build_path(module_name), self.path_lib, module_name + self.suffix_lib_static + self.suffix_warning))
		elif (type=="jar"):
			list.append(file)
			list.append(os.path.join(self.get_build_path(module_name), module_name + ".jar"))
			list.append(os.path.join(self.get_build_path(module_name), module_name + ".jar" + self.suffix_dependence))
			list.append(os.path.join(self.get_build_path(module_name), module_name + ".jar" + self.suffix_cmd_line))
			list.append(os.path.join(self.get_build_path(module_name), module_name + ".jar" + self.suffix_warning))
		elif (type=="image"):
			list.append(os.path.join(self.get_build_path(binary_name), "data", file + self.suffix_cmd_line))
		else:
			debug.error("unknow type : " + type)
		return list
	
	##
	## @brief Get the fianal path ==> contain all the generated packages
	## @return The path of the pa
	##
	def get_final_path(self):
		return os.path.join(tools.get_run_path(), self.path_out, self.path_final)
	
	def get_staging_path(self, binary_name):
		return os.path.join(tools.get_run_path(), self.path_out, self.path_staging, binary_name)
	
	def get_build_path(self, module_name):
		#debug.warning("A=" + str(tools.get_run_path()) + " " + str(self.path_out) + " " + str(self.path_build) + " " + str(module_name))
		return os.path.join(tools.get_run_path(), self.path_out, self.path_build, module_name)
	
	
	def get_build_path_object(self, binary_name):
		return os.path.join(self.get_build_path(binary_name), self.path_object)
	
	def get_build_path_bin(self, binary_name):
		return os.path.join(self.get_build_path(binary_name), self.path_bin)
	
	def get_build_path_lib(self, binary_name):
		return os.path.join(self.get_build_path(binary_name), self.path_lib, binary_name)
	
	def get_build_path_data(self, binary_name):
		return os.path.join(self.get_build_path(binary_name), self.path_data, binary_name)
	
	def get_build_path_include(self, binary_name):
		return os.path.join(self.get_build_path(binary_name), self.path_include)
	
	
	def get_build_file_bin(self, binary_name):
		return os.path.join(self.get_build_path_bin(binary_name), binary_name + self.suffix_binary)
	
	
	
	
	def get_staging_path_bin(self, package_name):
		return os.path.join(self.get_staging_path(package_name), self.path_bin)
	
	def get_staging_path_lib(self, package_name):
		return os.path.join(self.get_staging_path(package_name), self.path_lib, package_name)
	
	def get_staging_path_data(self, package_name):
		return os.path.join(self.get_staging_path(package_name), self.path_data, package_name)
	
	def get_staging_path_include(self, package_name):
		return os.path.join(self.get_staging_path(package_name), self.path_include)
	
	"""
	def get_staging_file_bin(self, package_name, binary_name):
		return os.path.join(self.get_staging_path_bin(package_name), binary_name + self.suffix_binary)
	"""
	
	
	
	def get_doc_path(self, module_name):
		return os.path.join(tools.get_run_path(), self.path_out, self.path_doc, module_name)
	
	
	def is_module_build(self, my_module):
		for mod in self.build_done:
			if mod == my_module:
				return True
		self.build_done.append(my_module)
		return False
	
	def is_module_build_tree(self, my_module):
		for mod in self.build_tree_done:
			if mod == my_module:
				return True
		self.build_tree_done.append(my_module)
		return False
	
	def add_module(self, newModule):
		debug.debug("Add nodule for Taget : " + newModule.name)
		self.module_list.append(newModule)
	
	def get_module(self, name):
		for mod in self.module_list:
			if mod.name == name:
				return mod
		debug.error("the module '" + str(name) + "'does not exist/already build")
		return None
	
	# return inherit packages ...
	"""
	def build(self, name, packagesName):
		for module in self.module_list:
			if module.name == name:
				return module.build(self, packagesName)
		debug.error("request to build an un-existant module name : '" + name + "'")
	"""
	
	def build_tree(self, name, packagesName):
		for mod in self.module_list:
			if mod.name == name:
				mod.build_tree(self, packagesName)
				return
		debug.error("request to build tree on un-existant module name : '" + name + "'")
	
	def clean(self, name):
		for mod in self.module_list:
			if mod.name == name:
				mod.clean(self)
				return
		debug.error("request to clean an un-existant module name : '" + name + "'")
	
	def load_if_needed(self, name, optionnal=False):
		for elem in self.module_list:
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
		for mod in self.module_list:
			if mod.name == name:
				mod.ext_project_add_module(self, projectMng, addedModule)
				return
	
	def build(self, name, packagesName=None, optionnal=False):
		if name == "gcov":
			debug.info("gcov all")
			debug.error("must set the gcov parsig on a specific library or binary ==> not supported now for all")
		if name == "dump":
			debug.info("dump all")
			self.load_all()
			for mod in self.module_list:
				mod.display(self)
			return
		if name == "all":
			debug.info("build all")
			self.load_all()
			for mod in self.module_list:
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
			for mod in self.module_list:
				mod.clean(self)
		else:
			# get the action an the module ....
			gettedElement = name.split("?")
			module_name = gettedElement[0]
			if len(gettedElement)>=3:
				sub_action_name = gettedElement[2]
			else:
				sub_action_name = ""
			if len(gettedElement)>=2:
				actionName = gettedElement[1]
			else :
				actionName = "build"
			debug.verbose("requested : " + module_name + "?" + actionName)
			if actionName == "install":
				self.build(module_name + "?build")
				self.install_package(module_name)
			elif actionName == "uninstall":
				self.un_install_package(module_name)
			elif actionName == "log":
				self.Log(module_name)
			else:
				present = self.load_if_needed(module_name, optionnal=optionnal)
				if     present == False \
				   and optionnal == True:
					return [heritage.HeritageList(), False]
				# clean requested
				for mod in self.module_list:
					if mod.name == module_name:
						if actionName == "dump":
							debug.info("dump module '" + module_name + "'")
							return mod.display(self)
						elif actionName == "clean":
							debug.info("clean module '" + module_name + "'")
							return mod.clean(self)
						elif actionName == "gcov":
							debug.debug("gcov on module '" + module_name + "'")
							if sub_action_name == "output":
								return mod.gcov(self, generate_output=True)
							return mod.gcov(self, generate_output=False)
						elif actionName == "build":
							debug.debug("build module '" + module_name + "'")
							if optionnal == True:
								return [mod.build(self, None), True]
							return mod.build(self, None)
				if optionnal == True:
					return [heritage.HeritageList(), False]
				debug.error("not know module name : '" + module_name + "' to '" + actionName + "' it")
	
	def add_action(self, name_of_state="PACKAGE", level=5, name="no-name", action=None):
		debug.verbose("add action : " + name)
		if name_of_state not in self.action_on_state:
			self.action_on_state[name_of_state] = [[level, name, action]]
		else:
			self.action_on_state[name_of_state].append([level, name, action])


targetList=[]
__start_target_name="lutinTarget_"


def import_path(path):
	global targetList
	matches = []
	debug.debug('TARGET: Start find sub File : "%s"' %path)
	for root, dirnames, filenames in os.walk(path):
		tmpList = fnmatch.filter(filenames, __start_target_name + "*.py")
		# Import the module :
		for filename in tmpList:
			debug.debug('TARGET:     Find a file : "%s"' %os.path.join(root, filename))
			#matches.append(os.path.join(root, filename))
			sys.path.append(os.path.dirname(os.path.join(root, filename)) )
			targetName = filename.replace('.py', '')
			targetName = targetName.replace(__start_target_name, '')
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
			debug.verbose("import target : '" + __start_target_name + name + "'")
			theTarget = __import__(__start_target_name + name)
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
		theTarget = __import__(__start_target_name + mod[0])
		try:
			tmpdesc = theTarget.get_desc()
			tmpList.append([mod[0], tmpdesc])
		except:
			debug.warning("has no name : " + mod[0])
			tmpList.append([mod[0], ""])
	return tmpList
