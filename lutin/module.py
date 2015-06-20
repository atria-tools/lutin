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
# Local import
from . import host
from . import tools
from . import debug
from . import heritage
from . import builder
from . import multiprocess

class Module:
	
	##
	## @brief Module class represent all system needed for a specific
	## 	module like 
	## 		- type (bin/lib ...)
	## 		- dependency
	## 		- flags
	## 		- files
	## 		- ...
	##
	def __init__(self, file, moduleName, moduleType):
		## Remove all variable to prevent error of multiple deffinition of the module ...
		debug.verbose("Create a new module : '" + moduleName + "' TYPE=" + moduleType)
		self.origin_file=''
		self.origin_folder=''
		# type of the module:
		self.type='LIBRARY'
		# Name of the module
		self.name=moduleName
		# Dependency list:
		self.depends = []
		# Dependency list (optionnal module):
		self.depends_optionnal = []
		self.depends_find = []
		# Documentation list:
		self.documentation = None
		# export PATH
		self.path = {"export":{},
		             "local":{}
		            }
		self.flags = {"export":{},
		              "local":{}
		             }
		self.extention_order_build = ["java", "javah"] # all is not set here is done in the provided order ...
		# sources list:
		self.src = []
		# copy files and folders:
		self.imageToCopy = []
		self.files = []
		self.folders = []
		self.isbuild = False
		
		## end of basic INIT ...
		if    moduleType == 'BINARY' \
		   or moduleType == 'LIBRARY' \
		   or moduleType == 'PACKAGE' \
		   or moduleType == 'PREBUILD':
			self.type=moduleType
		else :
			debug.error('for module "%s"' %moduleName)
			debug.error('    ==> error : "%s" ' %moduleType)
			raise 'Input value error'
		self.origin_file = file;
		self.origin_folder = tools.get_current_path(self.origin_file)
		self.local_heritage = heritage.heritage(self)
		
		self.package_prop = { "COMPAGNY_TYPE" : set(""),
		                      "COMPAGNY_NAME" : set(""),
		                      "COMPAGNY_NAME2" : set(""),
		                      "MAINTAINER" : set([]),
		                      #"ICON" : set(""),
		                      "SECTION" : set([]),
		                      "PRIORITY" : set(""),
		                      "DESCRIPTION" : set(""),
		                      "VERSION" : set("0.0.0"),
		                      "VERSION_CODE" : "",
		                      "NAME" : set("no-name"), # name of the application
		                      "ANDROID_MANIFEST" : "", # By default generate the manifest
		                      "ANDROID_RESOURCES" : [],
		                      "ANDROID_APPL_TYPE" : "APPL", # the other mode is "WALLPAPER" ... and later "WIDGET"
		                      "ANDROID_WALLPAPER_PROPERTIES" : [], # To create properties of the wallpaper (no use of EWOL display)
		                      "RIGHT" : [],
		                      "ADMOD_POSITION" : "top"
		                     }
		self.sub_heritage_list = None
	
	##
	## @brief add Some copilation flags for this module (and only this one)
	##
	def add_extra_compile_flags(self):
		self.compile_flags('c', [
			"-Wall",
			"-Wsign-compare",
			"-Wreturn-type",
			#"-Wint-to-pointer-cast",
			"-Wno-write-strings",
			"-Woverloaded-virtual",
			"-Wnon-virtual-dtor",
			"-Wno-unused-variable"]);
		#only for gcc : "-Wunused-variable", "-Wunused-but-set-variable",
	
	##
	## @brief remove all unneeded warning on compilation ==> for extern libs ...
	##
	def remove_compile_warning(self):
		self.compile_flags('c', [
			"-Wno-int-to-pointer-cast"
			]);
		self.compile_flags('c++', [
			"-Wno-c++11-narrowing"
			])
		# only for gcc :"-Wno-unused-but-set-variable"
	
	##
	## @brief Commands for copying files
	##
	def image_to_staging(self, binary_name, target):
		for source, destination, sizeX, sizeY in self.imageToCopy:
			extension = source[source.rfind('.'):]
			if     extension != ".png" \
			   and extension != ".jpg" \
			   and sizeX > 0:
				debug.error("Can not manage image other than .png and jpg to resize : " + source);
			displaySource = source
			source = self.origin_folder + "/" + source
			if destination == "":
				destination = source[source.rfind('/')+1:]
				debug.verbose("Regenerate Destination : '" + destination + "'")
			file_cmd = target.generate_file(binary_name, self.name, self.origin_folder, destination, "image")[0]
			if sizeX > 0:
				debug.verbose("Image file : " + displaySource + " ==> " + destination + " resize=(" + str(sizeX) + "," + str(sizeY) + ")")
				fileName, fileExtension = os.path.splitext(self.origin_folder+"/" + source)
				target.add_image_staging(source, destination, sizeX, sizeY, file_cmd)
			else:
				debug.verbose("Might copy file : " + displaySource + " ==> " + destination)
				target.add_file_staging(source, destination, file_cmd)
	
	##
	## @brief Commands for copying files
	##
	def files_to_staging(self, binary_name, target):
		for source, destination in self.files:
			displaySource = source
			source = self.origin_folder + "/" + source
			if destination == "":
				destination = source[source.rfind('/')+1:]
				debug.verbose("Regenerate Destination : '" + destination + "'")
			file_cmd = target.generate_file(binary_name, self.name, self.origin_folder, destination, "image")[0]
			# TODO : when destination is missing ...
			debug.verbose("Might copy file : " + displaySource + " ==> " + destination)
			target.add_file_staging(source, destination, file_cmd)
	
	##
	## @brief Commands for copying files
	##
	def folders_to_staging(self, binary_name, target):
		for source, destination in self.folders:
			debug.debug("Might copy folder : " + source + "==>" + destination)
			tools.copy_anything_target(target, self.origin_folder + "/" + source, destination)
	
	# call here to build the module
	def build(self, target, package_name):
		# ckeck if not previously build
		if target.is_module_build(self.name)==True:
			if self.sub_heritage_list == None:
				self.local_heritage = heritage.heritage(self)
			return self.sub_heritage_list
		# create the package heritage
		self.local_heritage = heritage.heritage(self)
		
		if     package_name==None \
		   and (    self.type=="BINARY" \
		         or self.type=="PACKAGE" ) :
			# this is the endpoint binary ...
			package_name = self.name
		else :
			# TODO : Set it better ...
			None
		# build dependency before
		list_sub_file_needed_to_build = []
		self.sub_heritage_list = heritage.HeritageList()
		# optionnal dependency :
		for dep, option, export in self.depends_optionnal:
			inherit_list, isBuilt = target.build(dep, package_name, True)
			if isBuilt == True:
				self.local_heritage.add_depends(dep);
				# TODO : Add optionnal Flags ...
				#     ==> do it really better ...
				if export == False:
					self.compile_flags(option[0], option[1]);
				else:
					self.add_export_flag(option[0], option[1]);
			# add at the heritage list :
			self.sub_heritage_list.add_heritage_list(inherit_list)
		for dep in self.depends:
			debug.debug("module: '" + str(self.name) + "'   request: '" + dep + "'")
			inherit_list = target.build(dep, package_name, False)
			# add at the heritage list :
			self.sub_heritage_list.add_heritage_list(inherit_list)
		# do sub library action for automatic generating ...
		if self.type in target.action_on_state:
			for action in target.action_on_state[self.type]:
				elem = action(target, self, package_name);
				
		
		if self.type != 'PREBUILD':
			# build local sources in a specific order :
			for extention_local in self.extention_order_build:
				list_file = tools.filter_extention(self.src, [extention_local])
				for file in list_file:
					#debug.info(" " + self.name + " <== " + file);
					fileExt = file.split(".")[-1]
					try:
						tmp_builder = builder.get_builder(fileExt);
						resFile = tmp_builder.compile(file,
						                             package_name,
						                             target,
						                             self.sub_heritage_list,
						                             flags = self.flags,
						                             path = self.path,
						                             name = self.name,
						                             basic_folder = self.origin_folder)
						if resFile["action"] == "add":
							list_sub_file_needed_to_build.append(resFile["file"])
						elif resFile["action"] == "path":
							self.add_path(resFile["path"], type='c')
						else:
							debug.error("an not do action for : " + str(resFile))
					except ValueError:
						debug.warning(" UN-SUPPORTED file format:  '" + self.origin_folder + "/" + file + "'")
			# now build the other :
			list_file = tools.filter_extention(self.src, self.extention_order_build, invert=True)
			for file in list_file:
				#debug.info(" " + self.name + " <== " + file);
				fileExt = file.split(".")[-1]
				try:
					tmp_builder = builder.get_builder(fileExt);
					resFile = tmp_builder.compile(file,
					                             package_name,
					                             target,
					                             self.sub_heritage_list,
					                             flags = self.flags,
					                             path = self.path,
					                             name = self.name,
					                             basic_folder = self.origin_folder)
					if resFile["action"] == "add":
						list_sub_file_needed_to_build.append(resFile["file"])
					elif resFile["action"] == "path":
						self.add_path(resFile["path"], type='c')
					else:
						debug.error("an not do action for : " + str(resFile))
				except ValueError:
					debug.warning(" UN-SUPPORTED file format:  '" + self.origin_folder + "/" + file + "'")
			# when multiprocess availlable, we need to synchronize here ...
			multiprocess.pool_synchrosize()
		
		# generate end point:
		if self.type=='PREBUILD':
			debug.print_element("Prebuild", self.name, "==>", "find")
			self.local_heritage.add_sources(self.src)
		elif self.type=='LIBRARY':
			try:
				tmp_builder = builder.get_builder_with_output("a");
				list_file = tools.filter_extention(list_sub_file_needed_to_build, tmp_builder.get_input_type())
				if len(list_file) > 0:
					resFile = tmp_builder.link(list_file,
					                           package_name,
					                           target,
					                           self.sub_heritage_list,
					                           name = self.name,
					                           basic_folder = self.origin_folder)
					self.local_heritage.add_sources(resFile)
			except ValueError:
				debug.error(" UN-SUPPORTED link format:  '.a'")
			try:
				tmp_builder = builder.get_builder_with_output("jar");
				list_file = tools.filter_extention(list_sub_file_needed_to_build, tmp_builder.get_input_type())
				if len(list_file) > 0:
					resFile = tmp_builder.link(list_file,
					                           package_name,
					                           target,
					                           self.sub_heritage_list,
					                           name = self.name,
					                           basic_folder = self.origin_folder)
					self.local_heritage.add_sources(resFile)
			except ValueError:
				debug.error(" UN-SUPPORTED link format:  '.jar'")
		elif self.type=='BINARY':
			try:
				tmp_builder = builder.get_builder_with_output("bin");
				resFile = tmp_builder.link(list_sub_file_needed_to_build,
				                           package_name,
				                           target,
				                           self.sub_heritage_list,
				                           name = self.name,
				                           basic_folder = self.origin_folder)
			except ValueError:
				debug.error(" UN-SUPPORTED link format:  '.bin'")
			# generate tree for this special binary
			target.clean_module_tree()
			self.build_tree(target, self.name)
			target.copy_to_staging(self.name)
		elif self.type=="PACKAGE":
			if target.name=="Android":
				# special case for android wrapper:
				try:
					tmp_builder = builder.get_builder_with_output("so");
					list_file = tools.filter_extention(list_sub_file_needed_to_build, tmp_builder.get_input_type())
					resFile = tmp_builder.link(list_file,
					                           package_name,
					                           target,
					                           self.sub_heritage_list,
					                           name = "lib" + self.name,
					                           basic_folder = self.origin_folder)
					self.local_heritage.add_sources(resFile)
				except ValueError:
					debug.error(" UN-SUPPORTED link format:  '.so'")
				try:
					tmp_builder = builder.get_builder_with_output("jar");
					list_file = tools.filter_extention(list_sub_file_needed_to_build, tmp_builder.get_input_type())
					if len(list_file) > 0:
						resFile = tmp_builder.link(list_file,
						                           package_name,
						                           target,
						                           self.sub_heritage_list,
						                           name = self.name,
						                           basic_folder = self.origin_folder)
						self.local_heritage.add_sources(resFile)
				except ValueError:
					debug.error(" UN-SUPPORTED link format:  '.jar'")
			else:
				try:
					tmp_builder = builder.get_builder_with_output("bin");
					resFile = tmp_builder.link(list_sub_file_needed_to_build,
					                           package_name,
					                           target,
					                           self.sub_heritage_list,
					                           name = self.name,
					                           basic_folder = self.origin_folder)
				except ValueError:
					debug.error(" UN-SUPPORTED link format:  'binary'")
			target.clean_module_tree()
			# generate tree for this special binary
			self.build_tree(target, self.name)
			target.copy_to_staging(self.name)
			if target.endGeneratePackage==True:
				# generate the package with his properties ...
				if target.name=="Android":
					self.sub_heritage_list.add_heritage(self.local_heritage)
					target.make_package(self.name, self.package_prop, self.origin_folder + "/..", self.sub_heritage_list)
				else:
					target.make_package(self.name, self.package_prop, self.origin_folder + "/..")
		else:
			debug.error("Dit not know the element type ... (impossible case) type=" + self.type)
			
		self.sub_heritage_list.add_heritage(self.local_heritage)
		# return local dependency ...
		return self.sub_heritage_list
	
	# call here to build the module
	def build_tree(self, target, package_name):
		# ckeck if not previously build
		if target.is_module_buildTree(self.name)==True:
			return
		debug.verbose("build tree of " + self.name)
		# add all the elements (first added only one keep ==> permit to everload sublib element)
		self.image_to_staging(package_name, target)
		self.files_to_staging(package_name, target)
		self.folders_to_staging(package_name, target)
		#build tree of all submodules
		for dep in self.depends:
			inherit = target.build_tree(dep, package_name)
	
	
	# call here to clean the module
	def clean(self, target):
		if self.type=='PREBUILD':
			# nothing to add ==> just dependence
			None
		elif self.type=='LIBRARY':
			# remove folder of the lib ... for this targer
			folderbuild = target.get_build_folder(self.name)
			debug.info("remove folder : '" + folderbuild + "'")
			tools.remove_folder_and_sub_folder(folderbuild)
		elif    self.type=='BINARY' \
		     or self.type=='PACKAGE':
			# remove folder of the lib ... for this targer
			folderbuild = target.get_build_folder(self.name)
			debug.info("remove folder : '" + folderbuild + "'")
			tools.remove_folder_and_sub_folder(folderbuild)
			folderStaging = target.get_staging_folder(self.name)
			debug.info("remove folder : '" + folderStaging + "'")
			tools.remove_folder_and_sub_folder(folderStaging)
		else:
			debug.error("Dit not know the element type ... (impossible case) type=" + self.type)
	
	def append_and_check(self, listout, newElement, order):
		for element in listout:
			if element==newElement:
				return
		listout.append(newElement)
		if True==order:
			listout.sort()
	
	def append_to_internalList2(self, listout, module, list, order=False):
		# add list in the Map
		if module not in listout:
			listout[module] = []
		# add elements...
		self.append_to_internalList(listout[module], list, order)
	
	def append_to_internalList(self, listout, list, order=False):
		if type(list) == type(str()):
			self.append_and_check(listout, list, order)
		else:
			# mulyiple imput in the list ...
			for elem in list:
				self.append_and_check(listout, elem, order)
	
	def add_module_depend(self, list):
		self.append_to_internalList(self.depends, list, True)
	
	def add_optionnal_module_depend(self, module_name, compilation_flags=["", ""], export=False):
		self.append_and_check(self.depends_optionnal, [module_name, compilation_flags, export], True)
	
	def add_export_path(self, list, type='c'):
		self.append_to_internalList2(self.path["export"], type, list)
	
	def add_path(self, list, type='c'):
		self.append_to_internalList2(self.path["local"], type, list)
	
	def add_export_flag(self, type, list):
		self.append_to_internalList2(self.flags["export"], type, list)
	
	# add the link flag at the module
	def compile_flags(self, type, list):
		self.append_to_internalList2(self.flags["local"], type, list)
	
	def compile_version_XX(self, version, same_as_api=True, gnu=False):
		cpp_version_list = [1999, 2003, 2011, 2014]
		if version not in cpp_version_list:
			debug.error("can not select CPP version : " + str(version) + " not in " + str(cpp_version_list))
		# select API version:
		api_version = 1999
		if same_as_api == True:
			api_version = version
		self.flags["local"]["c++-version"] = { "version":version,
		                                       "gnu":gnu
		                                     }
		self.flags["export"]["c++-version"] = api_version
		if gnu == True and same_as_api == True:
			debug.warning("Can not propagate the gnu extention of the CPP vesion for API");
	
	def compile_version_CC(self, version, same_as_api=True, gnu=False):
		c_version_list = [1989, 1990, 1999, 2011]
		if version not in c_version_list:
			debug.error("can not select C version : " + str(version) + " not in " + str(c_version_list))
		# select API version:
		api_version = 1999
		if same_as_api == True:
			api_version = version
		self.flags["local"]["c-version"] = { "version":version,
		                                     "gnu":gnu
		                                   }
		self.flags["export"]["c-version"] = api_version
		if gnu == True and same_as_api == True:
			debug.warning("Can not propagate the gnu extention of the C vesion for API");
	
	def add_src_file(self, list):
		self.append_to_internalList(self.src, list, True)
	
	def copy_image(self, source, destination='', sizeX=-1, sizeY=-1):
		self.imageToCopy.append([source, destination, sizeX, sizeY])
	
	def copy_file(self, source, destination=''):
		self.files.append([source, destination])
	
	def copy_folder(self, source, destination=''):
		self.folders.append([source, destination])
	
	def print_list(self, description, list):
		if len(list) > 0:
			print('        ' + str(description))
			for elem in list:
				print('            ' + str(elem))
	
	def display(self, target):
		print('-----------------------------------------------')
		print(' package : "' + self.name + "'")
		print('-----------------------------------------------')
		print('    type:"' + str(self.type) + "'")
		print('    file:"' + str(self.origin_file) + "'")
		print('    folder:"' + str(self.origin_folder) + "'")
		
		self.print_list('depends',self.depends)
		self.print_list('depends_optionnal', self.depends_optionnal)
		
		for element in self.flags["local"]:
			value = self.flags["local"][element]
			self.print_list('flags ' + element, value)
		
		for element in self.flags["export"]:
			value = self.flags["export"][element]
			self.print_list('flags export ' + element, value)
		
		self.print_list('src',self.src)
		self.print_list('files',self.files)
		self.print_list('folders',self.folders)
		for element in self.path["local"]:
			value = self.path["local"][element]
			self.print_list('local path ' + element, value)
		
		for element in self.path["export"]:
			value = self.path["export"][element]
			self.print_list('export path ' + element, value)
		
	
	def pkg_set(self, variable, value):
		if "COMPAGNY_TYPE" == variable:
			#	com : Commercial
			#	net : Network??
			#	org : Organisation
			#	gov : Governement
			#	mil : Military
			#	edu : Education
			#	pri : Private
			#	museum : ...
			if value not in ["com", "net", "org", "gov", "mil", "edu", "pri", "museum"]:
				debug.error("can not set the value for this Input : '" + variable + "' : '" + value + "'")
			else:
				self.package_prop[variable] = value
		elif "COMPAGNY_NAME" == variable:
			self.package_prop[variable] = value
			val2 = value.lower()
			val2 = val2.replace(' ', '')
			val2 = val2.replace('-', '')
			val2 = val2.replace('_', '')
			self.package_prop["COMPAGNY_NAME2"] = val2
		elif "ICON" == variable:
			self.package_prop[variable] = value
		elif "MAINTAINER" == variable:
			self.package_prop[variable] = value
		elif "SECTION" == variable:
			# project section : (must be separate by coma
			#    refer to : http://packages.debian.org/sid/
			#        admin cli-mono comm database debian-installer
			#        debug doc editors electronics devel embedded
			#        fonts games gnome gnu-r gnustep graphics
			#        hamradio haskell httpd interpreters java
			#        kde kernel libdevel libs lisp localization
			#        mail math misc net news ocaml oldlibs otherosfs
			#        perl php python ruby science shells sound tex
			#        text utils vcs video virtual web x11 xfce zope ...
			self.package_prop[variable] = value
		elif "PRIORITY" == variable:
			#list = ["required","important","standard","optional","extra"]
			#if isinstance(value, list):
			if value not in ["required", "important", "standard", "optional", "extra"]:
				debug.error("can not set the value for this Input : '" + variable + "' : '" + value + "'")
			else:
				self.package_prop[variable] = value
		elif "DESCRIPTION" == variable:
			self.package_prop[variable] = value
		elif "VERSION" == variable:
			self.package_prop[variable] = value
		elif "VERSION_CODE" == variable:
			self.package_prop[variable] = value
		elif "NAME" == variable:
			self.package_prop[variable] = value
		elif "ANDROID_MANIFEST" == variable:
			self.package_prop[variable] = value
		elif "ANDROID_JAVA_FILES" == variable:
			self.package_prop[variable] = value
		elif "RIGHT" == variable:
			self.package_prop[variable] = value
		elif "ANDROID_RESOURCES" == variable:
			self.package_prop[variable] = value
		elif "ANDROID_APPL_TYPE" == variable:
			self.package_prop[variable] = value
		elif "ADMOD_ID" == variable:
			self.package_prop[variable] = value
		elif "APPLE_APPLICATION_IOS_ID" == variable:
			self.package_prop[variable] = value
		elif "ADMOD_POSITION" == variable:
			if value in ["top", "bottom"]:
				self.package_prop[variable] = value
			else:
				debug.error("not know pkg element : '" + variable + "' with value : '" + value + "' must be [top|bottom]")
		else:
			debug.error("not know pkg element : '" + variable + "'")
	
	def pkg_add(self, variable, value):
		# TODO : Check values...
		self.package_prop[variable].append(value)
	
	def ext_project_add_module(self, target, projectMng, added_module = []):
		if self.name in added_module:
			return
		added_module.append(self.name)
		debug.verbose("add a module to the project generator :" + self.name)
		debug.verbose("local path :" + self.origin_folder)
		projectMng.add_files(self.name, self.origin_folder, self.src)
		#projectMng.add_data_file(self.origin_folder, self.files)
		#projectMng.add_data_folder(self.origin_folder, self.folders)
		"""
		for depend in self.depends:
			target.project_add_module(depend, projectMng, added_module)
		"""
	
	def create_project(self, target, projectMng):
		projectMng.set_project_name(self.name)
		self.ext_project_add_module(target, projectMng)
		projectMng.generate_project_file()



moduleList=[]
__startModuleName="lutin_"

def import_path(path):
	global moduleList
	matches = []
	debug.debug('MODULE: Start find sub File : "%s"' %path)
	for root, dirnames, filenames in os.walk(path):
		tmpList = fnmatch.filter(filenames, __startModuleName + "*.py")
		# Import the module :
		for filename in tmpList:
			debug.debug('Module:     Find a file : "%s"' %os.path.join(root, filename))
			#matches.append(os.path.join(root, filename))
			sys.path.append(os.path.dirname(os.path.join(root, filename)) )
			moduleName = filename.replace('.py', '')
			moduleName = moduleName.replace(__startModuleName, '')
			debug.debug("MODULE:     Integrate module: '" + moduleName + "' from '" + os.path.join(root, filename) + "'")
			moduleList.append([moduleName,os.path.join(root, filename)])

def exist(target, name):
	global moduleList
	for mod in moduleList:
		if mod[0] == name:
			return True
	return False

def load_module(target, name):
	global moduleList
	for mod in moduleList:
		if mod[0] == name:
			sys.path.append(os.path.dirname(mod[1]))
			debug.verbose("import module : '" + __startModuleName + name + "'")
			theModule = __import__(__startModuleName + name)
			#try:
			tmpElement = theModule.create(target)
			#except:
			#tmpElement = None
			#debug.warning(" no function 'create' in the module : " + mod[0] + " from:'" + mod[1] + "'")
			if (tmpElement == None) :
				debug.debug("Request load module '" + name + "' not define for this platform")
			else:
				target.add_module(tmpElement)

def list_all_module():
	global moduleList
	tmpListName = []
	for mod in moduleList:
		tmpListName.append(mod[0])
	return tmpListName

def list_all_module_with_desc():
	global moduleList
	tmpList = []
	for mod in moduleList:
		sys.path.append(os.path.dirname(mod[1]))
		theModule = __import__("lutin_" + mod[0])
		try:
			tmpdesc = theModule.get_desc()
			tmpList.append([mod[0], tmpdesc])
		except:
			debug.warning("has no naeme : " + mod[0])
			tmpList.append([mod[0], ""])
	return tmpList


