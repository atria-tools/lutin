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
import lutinModule as module
import lutinHost as host
import lutinTools
import lutinDebug as debug
import lutinHeritage as heritage
import lutinDepend as dependency
import lutinBuilder as builder
import lutinMultiprocess
import lutinEnv

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
		self.originFile=''
		self.originFolder=''
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
		self.path = {"export":[],
		             "local":[]
		            }
		self.flags = {"export":{},
		              "local":{}
		             }
		"""
		self.export_flags_ld = []
		self.export_flags_cc = []
		self.export_flags_xx = []
		self.export_flags_m = []
		self.export_flags_mm = []
		# list of all flags:
		self.flags_ld = []
		self.flags_cc = []
		self.flags_xx = []
		self.flags_m = []
		self.flags_mm = []
		self.flags_s = []
		self.flags_ar = []
		"""
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
		self.originFile = file;
		self.originFolder = lutinTools.get_current_path(self.originFile)
		self.localHeritage = heritage.heritage(self)
		
		self.packageProp = { "COMPAGNY_TYPE" : set(""),
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
		                     "ANDROID_JAVA_FILES" : ["DEFAULT"], # when user want to create his own services and activities
		                     "ANDROID_RESOURCES" : [],
		                     "ANDROID_APPL_TYPE" : "APPL", # the other mode is "WALLPAPER" ... and later "WIDGET"
		                     "ANDROID_WALLPAPER_PROPERTIES" : [], # To create properties of the wallpaper (no use of EWOL display)
		                     "RIGHT" : [],
		                     "ADMOD_POSITION" : "top"
		                    }
		self.subHeritageList = None
	
	##
	## @brief add Some copilation flags for this module (and only this one)
	##
	def add_extra_compile_flags(self):
		self.compile_flags_CC([
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
		self.compile_flags_CC([
			"-Wno-int-to-pointer-cast"
			]);
		self.compile_flags_XX([
			"-Wno-c++11-narrowing"
			])
		# only for gcc :"-Wno-unused-but-set-variable"
	
	##
	## @brief Commands for copying files
	##
	def image_to_staging(self, binaryName, target):
		for source, destination, sizeX, sizeY in self.imageToCopy:
			extension = source[source.rfind('.'):]
			if     extension != ".png" \
			   and extension != ".jpg" \
			   and sizeX > 0:
				debug.error("Can not manage image other than .png and jpg to resize : " + source);
			displaySource = source
			source = self.originFolder + "/" + source
			if destination == "":
				destination = source[source.rfind('/')+1:]
				debug.verbose("Regenerate Destination : '" + destination + "'")
			file_cmd = target.generate_file(binaryName, self.name, self.originFolder, destination, "image")[0]
			if sizeX > 0:
				debug.verbose("Image file : " + displaySource + " ==> " + destination + " resize=(" + str(sizeX) + "," + str(sizeY) + ")")
				fileName, fileExtension = os.path.splitext(self.originFolder+"/" + source)
				target.add_image_staging(source, destination, sizeX, sizeY, file_cmd)
			else:
				debug.verbose("Might copy file : " + displaySource + " ==> " + destination)
				target.add_file_staging(source, destination, file_cmd)
	
	##
	## @brief Commands for copying files
	##
	def files_to_staging(self, binaryName, target):
		for source, destination in self.files:
			displaySource = source
			source = self.originFolder + "/" + source
			if destination == "":
				destination = source[source.rfind('/')+1:]
				debug.verbose("Regenerate Destination : '" + destination + "'")
			file_cmd = target.generate_file(binaryName, self.name, self.originFolder, destination, "image")[0]
			# TODO : when destination is missing ...
			debug.verbose("Might copy file : " + displaySource + " ==> " + destination)
			target.add_file_staging(source, destination, file_cmd)
	
	##
	## @brief Commands for copying files
	##
	def folders_to_staging(self, binaryName, target):
		for source, destination in self.folders:
			debug.debug("Might copy folder : " + source + "==>" + destination)
			lutinTools.copy_anything_target(target, self.originFolder + "/" + source, destination)
	
	# call here to build the module
	def build(self, target, packageName):
		# ckeck if not previously build
		if target.is_module_build(self.name)==True:
			if self.subHeritageList == None:
				self.localHeritage = heritage.heritage(self)
			return self.subHeritageList
		# create the packege heritage
		self.localHeritage = heritage.heritage(self)
		
		if     packageName==None \
		   and (    self.type=="BINARY" \
		         or self.type=="PACKAGE" ) :
			# this is the endpoint binary ...
			packageName = self.name
		else :
			# TODO : Set it better ...
			None
		
		# build dependency before
		listSubFileNeededTobuild = []
		self.subHeritageList = heritage.HeritageList()
		# optionnal dependency :
		for dep, option, export in self.depends_optionnal:
			inheritList, isBuilt = target.build_optionnal(dep, packageName)
			if isBuilt == True:
				self.localHeritage.add_depends(dep);
				# TODO : Add optionnal Flags ...
				#     ==> do it really better ...
				if export == False:
					self.compile_flags_CC("-D"+option);
				else:
					self.add_export_flag_CC("-D"+option);
			# add at the heritage list :
			self.subHeritageList.add_heritage_list(inheritList)
		for dep in self.depends:
			inheritList = target.build(dep, packageName)
			# add at the heritage list :
			self.subHeritageList.add_heritage_list(inheritList)
		
		# build local sources
		for file in self.src:
			#debug.info(" " + self.name + " <== " + file);
			fileExt = file.split(".")[-1]
			tmpBuilder = builder.getBuilder(fileExt);
			if tmpBuilder != None:
				resFile = tmpBuilder.compile(file,
				                             packageName,
				                             target,
				                             self.subHeritageList,
				                             flags = self.flags,
				                             path = self.path,
				                             name = self.name,
				                             basic_folder = self.originFolder)
				listSubFileNeededTobuild.append(resFile)
			else:
				debug.warning(" UN-SUPPORTED file format:  '" + self.originFolder + "/" + file + "'")
		
		# when multiprocess availlable, we need to synchronize here ...
		lutinMultiprocess.pool_synchrosize()
		
		# generate end point:
		if self.type=='PREBUILD':
			debug.print_element("Prebuild", self.name, "==>", "find")
		elif self.type=='LIBRARY':
			resFile = self.link_to_a(listSubFileNeededTobuild, packageName, target, self.subHeritageList)
			self.localHeritage.add_sources(resFile)
		elif self.type=='BINARY':
			resFile = self.link_to_bin(listSubFileNeededTobuild, packageName, target, self.subHeritageList)
			# generate tree for this special binary
			target.clean_module_tree()
			self.build_tree(target, self.name)
			target.copy_to_staging(self.name)
		elif self.type=="PACKAGE":
			if target.name=="Android":
				# special case for android wrapper :
				resFile = self.link_to_so(listSubFileNeededTobuild, packageName, target, self.subHeritageList, "libewol")
			else:
				resFile = self.link_to_bin(listSubFileNeededTobuild, packageName, target, self.subHeritageList)
			target.clean_module_tree()
			# generate tree for this special binary
			self.build_tree(target, self.name)
			target.copy_to_staging(self.name)
			if target.endGeneratePackage==True:
				# generate the package with his properties ...
				target.make_package(self.name, self.packageProp, self.originFolder + "/..")
		else:
			debug.error("Dit not know the element type ... (impossible case) type=" + self.type)
			
		self.subHeritageList.add_heritage(self.localHeritage)
		# return local dependency ...
		return self.subHeritageList
	
	# call here to build the module
	def build_tree(self, target, packageName):
		# ckeck if not previously build
		if target.is_module_buildTree(self.name)==True:
			return
		debug.verbose("build tree of " + self.name)
		# add all the elements (first added only one keep ==> permit to everload sublib element)
		self.image_to_staging(packageName, target)
		self.files_to_staging(packageName, target)
		self.folders_to_staging(packageName, target)
		#build tree of all submodules
		for dep in self.depends:
			inherit = target.build_tree(dep, packageName)
	
	
	# call here to clean the module
	def clean(self, target):
		if self.type=='PREBUILD':
			# nothing to add ==> just dependence
			None
		elif self.type=='LIBRARY':
			# remove folder of the lib ... for this targer
			folderbuild = target.get_build_folder(self.name)
			debug.info("remove folder : '" + folderbuild + "'")
			lutinTools.remove_folder_and_sub_folder(folderbuild)
		elif    self.type=='BINARY' \
		     or self.type=='PACKAGE':
			# remove folder of the lib ... for this targer
			folderbuild = target.get_build_folder(self.name)
			debug.info("remove folder : '" + folderbuild + "'")
			lutinTools.remove_folder_and_sub_folder(folderbuild)
			folderStaging = target.get_staging_folder(self.name)
			debug.info("remove folder : '" + folderStaging + "'")
			lutinTools.remove_folder_and_sub_folder(folderStaging)
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
	
	def add_optionnal_module_depend(self, module_name, compilation_flags="", export=False):
		self.append_and_check(self.depends_optionnal, [module_name, compilation_flags, export], True)
	
	def add_export_path(self, list):
		self.append_to_internalList(self.path["export"], list)
	
	def add_path(self, list):
		self.append_to_internalList(self.path["local"], list)
	
	def add_export_flag_LD(self, list):
		self.append_to_internalList2(self.flags["export"], "link", list)
	
	def add_export_flag_CC(self, list):
		self.append_to_internalList2(self.flags["export"], "c", list)
	
	def add_export_flag_XX(self, list):
		self.append_to_internalList2(self.flags["export"], "c++", list)
	
	def add_export_flag_M(self, list):
		self.append_to_internalList2(self.flags["export"], "m", list)
	
	def add_export_flag_MM(self, list):
		self.append_to_internalList2(self.flags["export"], "mm", list)
	
	# add the link flag at the module
	def compile_flags_LD(self, list):
		self.append_to_internalList2(self.flags["local"], "link", list)
	
	def compile_flags_CC(self, list):
		self.append_to_internalList2(self.flags["local"], "c", list)
	
	def compile_flags_XX(self, list):
		self.append_to_internalList2(self.flags["local"], "c++", list)
	
	def compile_flags_M(self, list):
		self.append_to_internalList2(self.flags["local"], "m", list)
	
	def compile_flags_MM(self, list):
		self.append_to_internalList2(self.flags["local"], "mm", list)
	
	def compile_flags_S(self, list):
		self.append_to_internalList2(self.flags["local"], "s", list)
	
	def compile_version_XX(self, version, same_as_api=True, gnu=False):
		cpp_version_list = [1999, 2003, 2011, 2014]
		if version not in cpp_version_list:
			debug.error("can not select CPP version : " + str(version) + " not in " + str(cpp_version_list))
		# select API version:
		api_version = 1999
		if same_as_api == True:
			api_version = version
		self.flags["local"]["c++-version"] = { "version":version,
		                                       "api-version":api_version,
		                                       "gnu":gnu
		                                     }
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
		                                     "api-version":api_version,
		                                     "gnu":gnu
		                                   }
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
		print('    file:"' + str(self.originFile) + "'")
		print('    folder:"' + str(self.originFolder) + "'")
		
		self.print_list('depends',self.depends)
		self.print_list('depends_optionnal', self.depends_optionnal)
		
		for element,value in self.flags["local"]:
			self.print_list('flags ' + element, value)
		
		for element,value in self.flags["export"]:
			self.print_list('flags export ' + element, value)
		
		self.print_list('src',self.src)
		self.print_list('files',self.files)
		self.print_list('folders',self.folders)
		self.print_list('export path',self.path["export"])
		self.print_list('local  path',self.path["local"])
	
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
				self.packageProp[variable] = value
		elif "COMPAGNY_NAME" == variable:
			self.packageProp[variable] = value
			val2 = value.lower()
			val2 = val2.replace(' ', '')
			val2 = val2.replace('-', '')
			val2 = val2.replace('_', '')
			self.packageProp["COMPAGNY_NAME2"] = val2
		elif "ICON" == variable:
			self.packageProp[variable] = value
		elif "MAINTAINER" == variable:
			self.packageProp[variable] = value
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
			self.packageProp[variable] = value
		elif "PRIORITY" == variable:
			#list = ["required","important","standard","optional","extra"]
			#if isinstance(value, list):
			if value not in ["required", "important", "standard", "optional", "extra"]:
				debug.error("can not set the value for this Input : '" + variable + "' : '" + value + "'")
			else:
				self.packageProp[variable] = value
		elif "DESCRIPTION" == variable:
			self.packageProp[variable] = value
		elif "VERSION" == variable:
			self.packageProp[variable] = value
		elif "VERSION_CODE" == variable:
			self.packageProp[variable] = value
		elif "NAME" == variable:
			self.packageProp[variable] = value
		elif "ANDROID_MANIFEST" == variable:
			self.packageProp[variable] = value
		elif "ANDROID_JAVA_FILES" == variable:
			self.packageProp[variable] = value
		elif "RIGHT" == variable:
			self.packageProp[variable] = value
		elif "ANDROID_RESOURCES" == variable:
			self.packageProp[variable] = value
		elif "ANDROID_APPL_TYPE" == variable:
			self.packageProp[variable] = value
		elif "ADMOD_ID" == variable:
			self.packageProp[variable] = value
		elif "APPLE_APPLICATION_IOS_ID" == variable:
			self.packageProp[variable] = value
		elif "ADMOD_POSITION" == variable:
			if value in ["top", "bottom"]:
				self.packageProp[variable] = value
			else:
				debug.error("not know pkg element : '" + variable + "' with value : '" + value + "' must be [top|bottom]")
		else:
			debug.error("not know pkg element : '" + variable + "'")
	
	def pkg_add(self, variable, value):
		# TODO : Check values...
		self.packageProp[variable].append(value)
	
	def ext_project_add_module(self, target, projectMng, addedModule = []):
		if self.name in addedModule:
			return
		addedModule.append(self.name)
		debug.verbose("add a module to the project generator :" + self.name)
		debug.verbose("local path :" + self.originFolder)
		projectMng.add_files(self.name, self.originFolder, self.src)
		#projectMng.add_data_file(self.originFolder, self.files)
		#projectMng.add_data_folder(self.originFolder, self.folders)
		"""
		for depend in self.depends:
			target.project_add_module(depend, projectMng, addedModule)
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


