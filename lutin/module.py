#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license MPL v2.0 (see license file)
##
import re
import sys
import os
import copy
import inspect
import fnmatch
import json
import re
# Local import
from . import host
from . import tools
from realog import debug
from . import heritage
from . import builder
from . import multiprocess
from . import image
from . import license
from . import env
from . import moduleGLD
from warnings import catch_warnings
from xmlrpc.client import boolean


##
## @brief Module class represent all system needed for a specific
##	 module like 
##		 - type (bin/lib ...)
##		 - dependency
##		 - flags
##		 - files
##		 - ...
##
class Module:
	##
	## @brief Constructor
	## @param[in] self (handle) Class handle
	## @param[in] file (string) Plug-in file name (use __file__ to get it)
	## @param[in] module_name (string) Name of the module
	## @param[in] module_type (string) Type of the module:
	##	 - BINARY
	##	 - BINARY_SHARED // deprecated ...
	##	 - BINARY_DYNAMIC
	##	 - BINARY_STAND_ALONE
	##	 - LIBRARY
	##	 - LIBRARY_DYNAMIC
	##	 - LIBRARY_STATIC
	##	 - PACKAGE
	##	 - PREBUILD
	##	 - DATA
	## @return None
	##
	def __init__(self, file, module_name, module_type):
		## Remove all variable to prevent error of multiple definition of the module ...
		if module_type == "BINARY_SHARED":
			module_type = "BINARY_DYNAMIC";
		debug.verbose("Create a new module : '" + module_name + "' TYPE=" + module_type)
		self._origin_file = file;
		self._origin_path = tools.get_current_path(self._origin_file)
		# type of the module:
		if	module_type in moduleGLD.get_module_type_availlable():
			self._type=module_type
		else :
			debug.error('for module "%s"' %module_name)
			debug.error('	==> error : "%s" ' %module_type)
			raise 'Input value error'
		# Name of the module
		self._name = module_name
		# Tools list:
		self._tools = []
		# list of action to do:
		self._actions = []
		# Dependency list:
		self._depends = []
		# Dependency list (optional module):
		self._depends_optionnal = []
		self._depends_find = []
		# Documentation list:
		self._documentation = None
		# export PATH
		self._path = {"export":{},
					  "local":{}
					 }
		self._flags = {"export":{},
					   "local":{}
					  }
		self._ordered_builder = builder.get_ordered_builder_list();##### TODO: remove this :["java", "javah"] # all is not set here is done in the provided order ...
		# sources list with the type of files (auto_detected if not specified (c/c++/java/javah/asm/...):
		self._src = {}
		self._header = {}
		# copy files and paths:
		self._image_to_copy = []
		self._files = []
		self._paths = []
		# The module has been already build ...
		self._isbuild = False
		# add include install path after building package
		self._include_header_after = False
		# configure default heritage
		self._local_heritage = None
		# TODO : Do a better dynamic property system => not really versatile
		self._package_prop = { "COMPAGNY_TYPE" : "",
							   "COMPAGNY_NAME" : "",
							   "COMPAGNY_NAME2" : "",
							   "MAINTAINER" : [],
							   #"ICON" : set(""),
							   "SECTION" : [],
							   "PRIORITY" : "",
							   "DESCRIPTION" : "",
							   "VERSION" : [0,0,0],
							   "VERSION_CODE" : "",
							   "NAME" : "no-name", # name of the application
							   "ANDROID_MANIFEST" : "", # By default generate the manifest
							   "ANDROID_RESOURCES" : [],
							   "ANDROID_APPL_TYPE" : "APPL", # the other mode is "WALLPAPER" ... and later "WIDGET"
							   "ANDROID_WALLPAPER_PROPERTIES" : [], # To create properties of the wallpaper (no use of EWOL display)
							   "RIGHT" : [],
							   "LICENSE" : "", # by default: no license
							   "ADMOD_POSITION" : "top",
							   "ANDROID_SIGN" : "no_file.jks"
							  }
		self._package_prop_default = { "COMPAGNY_TYPE" : True,
									   "COMPAGNY_NAME" : True,
									   "COMPAGNY_NAME2" : True,
									   "MAINTAINER" : True,
									   #"ICON" : True,
									   "SECTION" : True,
									   "PRIORITY" : True,
									   "DESCRIPTION" : True,
									   "VERSION" : True,
									   "VERSION_CODE" : True,
									   "NAME" : True,
									   "ANDROID_MANIFEST" : True,
									   "ANDROID_RESOURCES" : True,
									   "ANDROID_APPL_TYPE" : True,
									   "ANDROID_WALLPAPER_PROPERTIES" : True,
									   "RIGHT" : True,
									   "LICENSE" : True,
									   "ADMOD_POSITION" : True,
									   "ANDROID_SIGN" : True
									 }
		self._sub_heritage_list = None
		self._generate_file = []
	
	##
	## @brief set the header not used for the compilation, thay are copied in the include folder, but they are only used for external library include.
	## @param[in] self (handle) Class handle.
	## @param[in] calue (boolean) Value of the variable.
	##
	def set_include_header_after(self, value):
		self._include_header_after = value;
	
	##
	## @brief Generate a string representing the class (for str(xxx))
	## @param[in] self (handle) Class handle
	## @return (string) string of str() conversion
	##
	def __repr__(self):
		return "{lutin.Module:" + str(self._name) + "}"
	
	##
	## @brief Get name of the module
	## @param[in] self (handle) Class handle
	## @return (string) Name of the current module
	##
	def get_name(self):
		return self._name
	
	##
	## @brief Get origin path of the module declaration
	## @param[in] self (handle) Class handle
	## @return (string) path of the module
	##
	def get_origin_path(self):
		return self._origin_path
	
	##
	## @brief Get type of the module ("BINARY", "LIBRARY", ...)
	## @param[in] self (handle) Class handle
	## @return (string) string with type of the @ref Module
	##
	def get_type(self):
		return self._type
	
	##
	## @brief Get module dependency
	## @param[in] self (handle) Class handle
	## @return ([string,...]) List of module that depend on
	##
	def get_depends(self):
		return self._depends
	
	##
	## @brief Get all header
	## @param[in] self (handle) Class handle
	## @return ([string,...]) List of module install header
	##
	def get_header(self):
		return self._header
	
	##
	## @brief add Some compilation flags for this module (and only this one)
	## @param[in] self (handle) Class handle
	## @return None
	## @deprecated Use set_code_quality("MEDIUM");
	##
	def add_extra_flags(self):
		self.set_code_quality("MEDIUM");
		
		#only for gcc : "-Wunused-variable", "-Wunused-but-set-variable",
	def set_code_quality(self, quality):
		quality_availlable = ["LOW","MEDIUM","HARD","PROFESSIONAL"];
		if quality not in quality_availlable:
			debug.error("Does not support other level than " + str(quality_availlable));
		id = quality_availlable.index(quality)
		# LOW ==> nothing to do ...
		if id >= 1:
			# MEDIUM
			self.add_flag('c', [
				"-Wall",
				"-Wsign-compare",
				"-Wreturn-type",
				"-Wno-write-strings"
				]);
			self.add_flag('c++', [
				"-Woverloaded-virtual",
				"-Wnon-virtual-dtor"
				]);
		if id >= 2:
			# HARD
			self.add_flag('c', [
				"-Wextra",
				"-Wmissing-braces",
				"-Wmissing-field-initializers",
				"-Wmissing-format-attribute",
				"-Wmissing-include-dirs",
				"-Wmissing-noreturn",
				"-Wpacked",
				"-Wsequence-point",
				"-Wshadow",
				"-Wsign-compare",
				"-Wsign-conversion",
				"-Wstack-protector",
				"-Wstrict-aliasing",
				"-Wno-unused-variable"
				]);
			self.add_flag('c++', [
				"-Wreorder",
				"-Weffc++",
				"-Wold-style-cast",
				"-Woverloaded-virtual",
				"-Wsign-promo",
				"-Wno-multichar",
				"-Wnonnull",
				"-Wno-overflow",
				"-Woverlength-strings",
				"-Wpadded",
				"-Wparentheses",
				"-Wpointer-arith",
				"-Wno-pointer-to-int-cast",
				"-Wredundant-decls",
				]);
		if id >= 3:
			# PROFESSIONAL
			self.add_flag('c', [
				"-Werror"
				]);
	
	##
	## @brief remove all unneeded warning on compilation ==> for extern libs ...
	## @param[in] self (handle) Class handle
	## @return None
	##
	def remove_compile_warning(self):
		self.add_flag('c', [
			"-Wno-int-to-pointer-cast"
			]);
		self.add_flag('c++', [
			"-Wno-c++11-narrowing"
			])
		# only for gcc :"-Wno-unused-but-set-variable"
	
	##
	## @brief Send image in the build data directory
	## @param[in] self (handle) Class handle
	## @param[in] target (handle) @ref lutin.target.Target class
	## @param[in] copy_list ([{},...]) When copy file, this API permit to remove unneeded files
	## @return None
	##
	def image_to_build(self, target, copy_list):
		for source, destination, sizeX, sizeY in self._image_to_copy:
			extension = source[source.rfind('.'):]
			if	 extension != ".png" \
			   and extension != ".jpg" \
			   and sizeX > 0:
				debug.error("Can not manage image other than .png and jpg to resize : " + source);
			display_source = source
			source = self._origin_path + "/" + source
			if destination == "":
				destination = source[source.rfind('/')+1:]
				debug.verbose("Regenerate Destination : '" + destination + "'")
			# TODO : set it back : file_cmd = target.get_build_path_data(self.name)
			file_cmd = ""
			if sizeX > 0:
				debug.verbose("Image file : " + display_source + " ==> " + destination + " resize=(" + str(sizeX) + "," + str(sizeY) + ")")
				fileName, fileExtension = os.path.splitext(os.path.join(self._origin_path,source))
				# Create the resized file in a temporary path to auto-copy when needed
				temporary_file = os.path.join(target.get_build_path_temporary_generate(self._name), "image_generation", destination)
				image.resize(source, temporary_file, sizeX, sizeY, file_cmd)
				# Copy file in statndard mode
				tools.copy_file(temporary_file,
								os.path.join(target.get_build_path_data(self._name, group="in-shared"), destination),
								file_cmd,
								in_list=copy_list)
			else:
				debug.verbose("Might copy file : " + display_source + " ==> " + destination)
				tools.copy_file(source,
								os.path.join(target.get_build_path_data(self._name, group="in-shared"), destination),
								file_cmd,
								in_list=copy_list)
	
	##
	## @brief Send files in the build data directory
	## @param[in] self (handle) Class handle
	## @param[in] target (handle) Target object
	## @param[in] copy_list ([{},...]) When copy file, this API permit to remove unneeded files
	## @return None
	##
	def files_to_build(self, target, copy_list):
		for source, destination, group in self._files:
			display_source = source
			source = os.path.join(self._origin_path, source)
			if destination == "":
				destination = source[source.rfind('/')+1:]
				debug.verbose("Regenerate Destination : '" + destination + "'")
			# TODO : set it back : file_cmd = target.get_build_path_data(self.name)
			file_cmd = ""
			debug.warning("Might copy file : " + display_source + "==> (" + str(group) + ") " + destination)
			tools.copy_file(source,
							os.path.join(target.get_build_path_data(self._name, group=group_folder), destination),
							force_identical=True,
							in_list=copy_list)
	
	##
	## @brief Send compleate folder in the build data directory
	## @param[in] self (handle) Class handle
	## @param[in] target (handle) Target object
	## @param[in] copy_list ([{},...]) When copy file, this API permit to remove unneeded files
	## @return None
	##
	def paths_to_build(self, target, copy_list):
		for source, destination, group in self._paths:
			debug.warning("Might copy path : " + source + "==> (" + str(group) + ") " + destination)
			tmp_path = os.path.dirname(os.path.realpath(os.path.join(self._origin_path, source)))
			tmp_rule = os.path.basename(source)
			for root, dirnames, filenames in os.walk(tmp_path):
				debug.extreme_verbose(" root='" + str(root) + "' tmp_path='" + str(tmp_path))
				if root != tmp_path:
					break
				debug.verbose(" root='" + str(root) + "' dir='" + str(dirnames) + "' filenames=" + str(filenames))
				list_files = filenames
				if len(tmp_rule)>0:
					list_files = fnmatch.filter(filenames, tmp_rule)
				debug.verbose("	   filenames=" + str(filenames))
				# Import the module :
				for cycle_file in list_files:
					#for cycle_file in filenames:
					new_destination = destination
					# TODO : maybe an error when changing subdirectory ...
					#if root[len(source)-1:] != "":
					#	new_destination = os.path.join(new_destination, root[len(source)-1:])
					debug.verbose("Might copy : '" + os.path.join(root, cycle_file) + "' ==> '" + os.path.join(target.get_build_path_data(self._name, group=group), new_destination, cycle_file) + "'" )
					file_cmd = "" # TODO : ...
					tools.copy_file(os.path.join(root, cycle_file),
									os.path.join(target.get_build_path_data(self._name, group=group), new_destination, cycle_file),
									file_cmd,
									in_list=copy_list)
	
	##
	## @brief Process GCOV on the Current module
	## @param[in] self (handle) Class handle
	## @param[in] target (handle) Target object
	## @param[in] generate_output (bool) Generate the output gcov file of every library file (to debug wich branch is used)
	## @return None
	##
	def gcov(self, target, generate_output=False):
		if self._type == 'PREBUILD':
			debug.error("Can not generate gcov on prebuid system ... : '" + self._name + "'");
			return
		# list of path that can apear in the output data :
		gcov_path_file = []
		if self._include_header_after == False:
			gcov_path_file.append(target.get_build_path_include(self._name)) # for include (that is installed)
		#gcov_path_file.append(" " + target.get_build_path_include(self._name))
		gcov_path_file.append(self._origin_path) # for sources.
		gcov_path_file.append(" " + self._origin_path)
		# squash header and src...
		full_list_file = []
		for key in self._header.keys():
			for elem in self._header[key]:
				debug.extreme_verbose("plop H : " + str(key) + "->" + str(elem['src']))
				full_list_file.append([self._name, elem['src']])
		for key in self._src.keys():
			for elem in self._src[key]:
				debug.extreme_verbose("plop S : " + str(key) + "->" + str(elem))
				full_list_file.append([self._name, elem])
		for mod_name in self._tools:
			tool_module = load_module(target, mod_name)
			if tool_module == None:
				continue
			for elem in tool_module.header:
				debug.extreme_verbose("plop HH: " + ":" + str(elem['src']))
				full_list_file.append([tool_module.name, elem['src']])
			for elem in tool_module.src:
				debug.extreme_verbose("plop SS: " + tool_module.name + ":" + str(elem))
				full_list_file.append([tool_module.name, elem])
		debug.extreme_verbose("plop F : " +str(self._ordered_builder))
		# remove uncompilable elements:
		# TODO: list_file = tools.filter_extention(full_list_file, self.extention_order_build, True)
		list_file = full_list_file;
		global_list_file = ""
		for file in list_file:
			debug.verbose(" gcov : " + self._name + " <== " + str(file));
			file_dst = target.get_full_name_destination(file[0], self._origin_path, file[1], "o")
			global_list_file += file_dst + " "
		cmd = "gcov"
		# specify the version of gcov we need to use
		if target.config["compilator-version"] != "":
			cmd += "-" + target.config["compilator-version"] + " "
		cmd += " --branch-counts --preserve-paths "
		if generate_output == False:
			cmd += "--no-output "
		cmd += global_list_file
		debug.extreme_verbose("	  " + cmd);
		ret = multiprocess.run_command_direct(cmd)
		# parsing ret :
		debug.extreme_verbose("result: " + str(ret));
		ret = ret.split('\n');
		debug.verbose("*** Gcov result parsing ...");
		useful_list = []
		remove_next = False
		last_file = ""
		executed_lines = 0
		executable_lines = 0
		for elem in ret:
			debug.debug("line: " + elem)
			if remove_next == True:
				remove_next = False
				debug.debug("--------------------------")
				continue;
			if	elem[:10] == "Creating '" \
			   or elem[:10] == "Removing '" \
			   or elem[:14] == "Suppression de" \
			   or elem[:11] == "Création de":
				remove_next = True
				continue
			if	elem[:6] in ["File '", "File «"] \
			   or elem[:7] in ["File ' ", "File « "]:
				path_finder = False
				for path_base_finder in gcov_path_file:
					if path_base_finder == elem[6:len(path_base_finder)+6]:
						path_finder = True
						last_file = elem[6+len(path_base_finder)+1:-1]
						while last_file[-1] == " ":
							last_file = last_file[:-1]
				if path_finder == False:
					remove_next = True
					debug.verbose("	REMOVE: '" + str(elem[6:len(self._origin_path)+1]) + "' not in " + str(gcov_path_file))
					continue
				continue
			if	elem[:7] == "Aucune " \
			   or elem[:19] == "No executable lines":
				debug.verbose("	Nothing to execute");
				continue
			start_with = ["Lines executed:", "Lignes exécutées:"]
			find = False
			for line_base in start_with:
				if elem[:len(line_base)] == line_base:
					find = True
					elem = elem[len(line_base):]
					break;
			debug.verbose(" temp Value: " + str(elem))
			if find == False:
				debug.warning("	gcov ret : " + str(elem));
				debug.warning("		 ==> does not start with : " + str(start_with));
				debug.warning("		 Parsing error");
				continue
			out = elem.split("% of ")
			if len(out) != 2:
				out = elem.split("% de ")
				if len(out) != 2:
					debug.warning("	gcov ret : " + str(elem));
					debug.warning("		 Parsing error of '% of '");
					continue
			debug.verbose("property : " + str(out))
			pourcent = float(out[0])
			total_line_count = int(out[1])
			total_executed_line = int(float(total_line_count)*pourcent/100.0)
			# check if in source or header:
			in_source_file = False
			debug.verbose("	??> Check: " + str(last_file))
			for key_header in self._header.key():
				for elem_header in self._header[key_header]:
					debug.verbose("		==> Check: " + str(elem_header['src']))
					if elem_header['src'] == last_file:
						in_source_file = True
			for key_src in self._src.keys():
				for elem_src in self._src[key_src]:
					debug.verbose("		==> Check: " + str(elem_src))
					if elem_src == last_file:
						in_source_file = True
			if in_source_file == False:
				debug.verbose("		==> Remove not in source: " + str(out))
				continue
			useful_list.append([last_file, pourcent, total_executed_line, total_line_count])
			executed_lines += total_executed_line
			executable_lines += total_line_count
			last_file = ""
			debug.debug("--------------------------")
		ret = useful_list[:-1]
		debug.verbose("plopppp " + str(useful_list))
		#for elem in ret:
		#	debug.info("	" + str(elem));
		for elem in ret:
			if elem[1]<10.0:
				debug.info("   %   " + str(elem[1]) + "\r\t\t" + str(elem[0]));
			elif elem[1]<100.0:
				debug.info("   %  " + str(elem[1]) + "\r\t\t" + str(elem[0]));
			else:
				debug.info("   % " + str(elem[1]) + "\r\t\t" + str(elem[0]));
			debug.verbose("	   " + str(elem[2]) + " / " + str(elem[3]));
		try:
			pourcent = 100.0*float(executed_lines)/float(executable_lines)
		except ZeroDivisionError:
			pourcent = 0.0
		# generate json file:
		json_file_name = target.get_build_path(self._name) + "/" + self._name + "_coverage.json"
		debug.debug("generate json file : " + json_file_name)
		tmp_file = open(json_file_name, 'w')
		tmp_file.write('{\n')
		tmp_file.write('	"lib-name":"' + self._name + '",\n')
		#tmp_file.write('	"coverage":"' + str(pourcent) + '",\n')
		tmp_file.write('	"executed":"' + str(executed_lines) + '",\n')
		tmp_file.write('	"executable":"' + str(executable_lines) + '",\n')
		tmp_file.write('	"list":[\n')
		val = 0
		for elem in ret:
			if val == 0 :
				tmp_file.write('		{\n')
			else:
				tmp_file.write('		}, {\n')
			val += 1
			tmp_file.write('			"file":"' + elem[0] + '",\n')
			tmp_file.write('			"executed":' + str(elem[2]) + ',\n')
			tmp_file.write('			"executable":' + str(elem[3]) + '\n')
		tmp_file.write('		}\n')
		tmp_file.write('	]\n')
		tmp_file.write('}\n')
		tmp_file.flush()
		tmp_file.close()
		# print debug:
		debug.print_element("coverage", self._name, ":", str(pourcent) + "%  " + str(executed_lines) + "/" + str(executable_lines))
		return True
	
	##
	## @brief Build the current the module and install in staging path.
	## @param[in] self (handle) Class handle.
	## @param[in] target (handle) @ref lutin.target.Target object.
	## @param[in] package_name (string) Package name (not the module name). Used to know where to install element in the staging.
	## @return (handle) @ref lutin.heritage.heritage.
	##
	# call here to build the module
	def build(self, target, package_name):
		# ckeck if not previously build
		if target.is_module_build(self._name) == True:
			if self._sub_heritage_list == None:
				self._local_heritage = heritage.heritage(self, target)
				debug.debug("plop " + str(self._local_heritage));
			return copy.deepcopy(self._sub_heritage_list)
		# create the package heritage
		self._local_heritage = heritage.heritage(self, target)
		if len(self._actions) != 0:
			debug.verbose("execute actions: " + str(len(self._actions)))
			for action in self._actions:
				action["action"](target, self, action["data"]);
		if	 package_name == None \
		   and (	self._type == 'BINARY'
				 or self._type == 'BINARY_DYNAMIC' \
				 or self._type == 'BINARY_STAND_ALONE' \
				 or self._type == 'PACKAGE' ) :
			# this is the endpoint binary ...
			package_name = self._name
			debug.debug("package name = " + package_name)
		else:
			pass
		# build dependency before
		list_sub_file_needed_to_build = []
		self._sub_heritage_list = heritage.HeritageList()
		# optionnal dependency :
		for dep, option, export, src_file, header_file, option_not_found in self._depends_optionnal:
			debug.verbose("try find optionnal dependency: '" + str(dep) + "'")
			inherit_list, isBuilt = target.build(dep, True, package_name=package_name)
			if isBuilt == True:
				self._local_heritage.add_depends(dep);
				self.add_flag(option[0], option[1], export=export);
				self.add_src_file(src_file)
				self.add_header_file(header_file)
			else:
				self.add_flag(option_not_found[0], option_not_found[1], export=export);
			# add at the heritage list :
			self._sub_heritage_list.add_heritage_list(inherit_list)
		for dep in self._depends:
			debug.debug("module: '" + str(self._name) + "'   request: '" + dep + "'")
			inherit_list = target.build(dep, False, package_name=package_name)
			# add at the heritage list :
			self._sub_heritage_list.add_heritage_list(inherit_list)
		# do sub library action for automatic generating ...
		local_type = self._type
		if self._type == 'LIBRARY_DYNAMIC':
			local_type = 'LIBRARY'
		if self._type == 'LIBRARY_STATIC':
			local_type = 'LIBRARY'
		if self._type == 'BINARY_DYNAMIC':
			local_type = 'BINARY'
		if self._type == 'BINARY_STAND_ALONE':
			local_type = 'BINARY'
		if local_type in target.action_on_state:
			for lvl in range(0,100):
				for level, action_name, action in target.action_on_state[local_type]:
					if level == lvl:
						debug.debug("level=" + str(level) + " Do Action : " + action_name)
						elem = action(target, self, package_name);
		# ----------------------------------------------------
		# -- Generic library help						   --
		# ----------------------------------------------------
		package_version_string = tools.version_to_string(self._package_prop["VERSION"]);
		if self._type == 'DATA':
			debug.print_element("Data", self._name, "-", package_version_string)
		elif self._type == 'PREBUILD':
			debug.print_element("Prebuild", self._name, "-", package_version_string)
		elif self._type == 'LIBRARY':
			debug.print_element("Library", self._name, "-", package_version_string)
		elif self._type == 'LIBRARY_DYNAMIC':
			debug.print_element("Library(dynamic)", self._name, "-", package_version_string)
		elif self._type == 'LIBRARY_STATIC':
			debug.print_element("Library(static)", self._name, "-", package_version_string)
		elif self._type == 'BINARY':
			debug.print_element("Binary(auto)", self._name, "-", package_version_string)
		elif self._type == 'BINARY_DYNAMIC':
			debug.print_element("Binary (dynamic)", self._name, "-", package_version_string)
		elif self._type == 'BINARY_STAND_ALONE':
			debug.print_element("Binary (stand alone)", self._name, "-", package_version_string)
		elif self._type == 'PACKAGE':
			debug.print_element("Package", self._name, "-", package_version_string)
		
		# list of all file to copy:
		copy_list={}
		# ---------------------------------------------------------------------------
		# -- install header (generated header files)							   --
		# ---------------------------------------------------------------------------
		generate_path = target.get_build_path_temporary_generate(self._name)
		include_path = target.get_build_path_include(self._name)
		have_only_generate_file = False
		if len(self._generate_file) > 0:
			debug.debug("install GENERATED headers / src ...")
			for elem_generate in self._generate_file:
				# write data in the generate path ... (all is generated at the same path) ...
				debug.debug("Create data: " + os.path.join(generate_path, elem_generate["filename"]))
				ret_write = tools.file_write_data(os.path.join(generate_path, elem_generate["filename"]), elem_generate["data"], only_if_new=True)
				if ret_write == True:
					debug.print_element("generate", self._name, "##", elem_generate["filename"])
				if elem_generate["type"] == "header":
					dst = os.path.join(include_path, elem_generate["filename"])
					copy_list[dst] = {"src":os.path.join(generate_path, elem_generate["filename"]),
									  "cmd_file":None,
									  "need_copy":ret_write}
					if elem_generate["install"] == True:
						have_only_generate_file = True
						# TODO : Do it better, we force the include path in the heritage to permit to have a correct inclusion ...
						self._local_heritage.include = target.get_build_path_include(self._name)
				elif elem_generate["type"] == "data":
					# data file to install:
					if elem_generate["install"] == True:
						self._files.append([os.path.join(generate_path, elem_generate["filename"]), elem_generate["filename"]])
				else:
					# add file to compile
					debug.warning("Add file to build : " + os.path.join(generate_path, elem_generate["filename"]) )
					self.add_src_file(os.path.join(generate_path, elem_generate["filename"]))
		if have_only_generate_file == True:
			self._add_path(generate_path)
		
		# ---------------------------------------------------------------------------
		# -- install header (do it first for extern lib and gcov better interface) --
		# ---------------------------------------------------------------------------
		debug.debug("install headers ...")
		for builder_name in self._header.keys():
			for file in self._header[builder_name]:
				src_path = os.path.join(self._origin_path, file["src"])
				if "multi-dst" in file:
					dst_path = os.path.join(include_path, file["multi-dst"])
					tools.copy_anything(src_path,
										dst_path,
										recursive=file["recursive"],
										force_identical=True,
										in_list=copy_list)
				else:
					dst_path = os.path.join(include_path, file["dst"])
					tools.copy_file(src_path,
									dst_path,
									force_identical=True,
									in_list=copy_list)
		#real copy files
		tools.copy_list(copy_list)
		# remove unneded files (NOT folder ...)
		tools.clean_directory(include_path, copy_list)
		# add the pat to the usable dirrectory
		if self._include_header_after == False:
			self._add_path(include_path)
		
		# ---------------------------------------------------------------------------
		# -- Sources compilation												   --
		# ---------------------------------------------------------------------------
		if	 self._type != 'PREBUILD' \
		   and self._type != 'PACKAGE':
			# build local sources in a specific order:
			for builder_name in self._ordered_builder:
				debug.verbose("Execute builder : " + builder_name);
				if builder_name not in self._src.keys():
					debug.verbose("    ==> nothing to do...");
					continue;
				for file in self._src[builder_name]:
					debug.verbose(" " + self._name + " <== " + file);
					fileExt = file.split(".")[-1]
					try:
						tmp_builder = builder.get_builder_named(builder_name);
						multithreading = tmp_builder.get_support_multithreading()
						if multithreading == False:
							multiprocess.pool_synchrosize()
						res_file = tmp_builder.compile(file,
													   package_name,
													   target,
													   self._sub_heritage_list,
													   flags = self._flags,
													   path = self._path,
													   name = self._name,
													   basic_path = self._origin_path,
													   module_src = self._src)
						if multithreading == False:
							multiprocess.pool_synchrosize()
						if res_file["action"] == "add":
							list_sub_file_needed_to_build.append(res_file["file"])
						elif res_file["action"] == "path":
							self._add_path(res_file["path"], type='c')
						else:
							debug.error("an not do action for : " + str(res_file))
					except ValueError:
						debug.warning(" UN-SUPPORTED file format:  '" + self._origin_path + "/" + file + "'")
			# now build the other :
			list_other = tools.filter_map(self._src, self._ordered_builder, invert=True)
			for builder_name in list_other.keys():
				debug.warning(" " + builder_name + " is unknown !! element not build:");
				for elem in self._src[builder_name]:
					debug.warning("    ==> " + elem);
			# when multiprocess available, we need to synchronize here ...
			multiprocess.pool_synchrosize()
		
		# ----------------------------------------------------
		# -- Generation point							   --
		# ----------------------------------------------------
		if self._type == 'PREBUILD':
			self._local_heritage.add_sources(self._src)
		elif	self._type == 'LIBRARY' \
			 or self._type == 'LIBRARY_DYNAMIC' \
			 or self._type == 'LIBRARY_STATIC':
			res_file_out = []
			if	self._type == 'LIBRARY' \
			   or self._type == 'LIBRARY_STATIC':
				try:
					tmp_builder = builder.get_builder_with_output("a");
					list_file = tools.filter_extention(list_sub_file_needed_to_build, tmp_builder.get_input_type())
					if len(list_file) > 0:
						res_file = tmp_builder.link(list_file,
													package_name,
													target,
													self._sub_heritage_list,
													flags = self._flags,
													name = self._name,
													basic_path = self._origin_path)
						self._local_heritage.add_lib_static(res_file)
				except ValueError:
					debug.error(" UN-SUPPORTED link format:  '.a'")
			if target.support_dynamic_link == True:
				if	self._type == 'LIBRARY' \
				   or self._type == 'LIBRARY_DYNAMIC':
					try:
						tmp_builder = builder.get_builder_with_output("so");
						list_file = tools.filter_extention(list_sub_file_needed_to_build, tmp_builder.get_input_type())
						if len(list_file) > 0:
							res_file = tmp_builder.link(list_file,
														package_name,
														target,
														self._sub_heritage_list,
														flags = self._flags,
														name = self._name,
														basic_path = self._origin_path)
							self._local_heritage.add_lib_dynamic(res_file)
					except ValueError:
						debug.error(" UN-SUPPORTED link format:  '.so'/'.dynlib'/'.dll'")
			try:
				tmp_builder = builder.get_builder_with_output("jar");
				list_file = tools.filter_extention(list_sub_file_needed_to_build, tmp_builder.get_input_type())
				if len(list_file) > 0:
					res_file = tmp_builder.link(list_file,
												package_name,
												target,
												self._sub_heritage_list,
												flags = self._flags,
												name = self._name,
												basic_path = self._origin_path)
					self._local_heritage.add_lib_interpreted('java', res_file)
			except ValueError:
				debug.error(" UN-SUPPORTED link format:  '.jar'")
		elif	self._type == 'BINARY' \
			 or self._type == 'BINARY_DYNAMIC' \
			 or self._type == 'BINARY_STAND_ALONE':
			shared_mode = False
			static_mode = True
			if "Android" in target.get_type():
				debug.warning("Android mode ...")
				# special case for android ...
				for elem in self._sub_heritage_list.src['src']:
					debug.warning("	" + elem[-4:])
					if elem[-4:] == '.jar':
						# abstract GUI interface ...
						shared_mode = True
						break;
			if target.support_dynamic_link == True:
				if self._type == 'BINARY_DYNAMIC':
					static_mode = False
			if shared_mode == True:
				try:
					tmp_builder = builder.get_builder_with_output("so");
					list_file = tools.filter_extention(list_sub_file_needed_to_build, tmp_builder.get_input_type())
					res_file = tmp_builder.link(list_file,
												package_name,
												target,
												self._sub_heritage_list,
												flags = self._flags,
												name = self._name,
												basic_path = self._origin_path,
												static = static_mode)
					self._local_heritage.add_sources(res_file)
				except ValueError:
					debug.error(" UN-SUPPORTED link format:  '.so'")
				try:
					tmp_builder = builder.get_builder_with_output("jar");
					list_file = tools.filter_extention(list_sub_file_needed_to_build, tmp_builder.get_input_type())
					if len(list_file) > 0:
						res_file = tmp_builder.link(list_file,
													package_name,
													target,
													self._sub_heritage_list,
													flags = self._flags,
													name = self._name,
													basic_path = self._origin_path)
						self._local_heritage.add_sources(res_file)
				except ValueError:
					debug.error("UN-SUPPORTED link format: '.jar'")
			else:
				# try to build the binary with dependency of .so and the standalone binary (Not package dependent)
				if static_mode == True:
					try:
						tmp_builder = builder.get_builder_with_output("bin");
						res_file = tmp_builder.link(list_sub_file_needed_to_build,
													package_name,
													target,
													self._sub_heritage_list,
													flags = self._flags,
													name = self._name,
													basic_path = self._origin_path,
													static = True)
						#self._local_heritage.add_sources(res_file)
					except ValueError:
						debug.error("UN-SUPPORTED link format: '.bin'")
				try:
					tmp_builder = builder.get_builder_with_output("bin");
					res_file = tmp_builder.link(list_sub_file_needed_to_build,
												package_name,
												target,
												self._sub_heritage_list,
												flags = self._flags,
												name = self._name,
												basic_path = self._origin_path,
												static = False)
					#self._local_heritage.add_sources(res_file)
				except ValueError:
					debug.error("UN-SUPPORTED link format: '.bin'")
		elif self._type == "PACKAGE":
			if "Android" in target.get_type():
				# special case for android wrapper:
				try:
					tmp_builder = builder.get_builder_with_output("so");
					list_file = tools.filter_extention(list_sub_file_needed_to_build, tmp_builder.get_input_type())
					res_file = tmp_builder.link(list_file,
												package_name,
												target,
												self._sub_heritage_list,
												flags = self._flags,
												name = "lib" + self._name,
												basic_path = self._origin_path)
					self._local_heritage.add_sources(res_file)
				except ValueError:
					debug.error("UN-SUPPORTED link format: '.so'")
				try:
					tmp_builder = builder.get_builder_with_output("jar");
					list_file = tools.filter_extention(list_sub_file_needed_to_build, tmp_builder.get_input_type())
					if len(list_file) > 0:
						res_file = tmp_builder.link(list_file,
													package_name,
													target,
													self._sub_heritage_list,
													flags = self._flags,
													name = self._name,
													basic_path = self._origin_path)
						self._local_heritage.add_sources(res_file)
				except ValueError:
					debug.error(" UN-SUPPORTED link format:  '.jar'")
			else:
				pass
				# TODO : Check this but I this this is not needed ==> a package can not have build stage ...
				"""
				try:
					tmp_builder = builder.get_builder_with_output("bin");
					res_file = tmp_builder.link(list_sub_file_needed_to_build,
												package_name,
												target,
												self._sub_heritage_list,
												flags = self._flags,
												name = self._name,
												basic_path = self._origin_path)
				except ValueError:
					debug.error(" UN-SUPPORTED link format:  'binary'")
				"""
		elif self._type == "DATA":
			debug.debug("Data package have noting to build... just install")
		else:
			debug.error("Did not known the element type ... (impossible case) type=" + self._type)
		
		# ----------------------------------------------------
		# -- install data								   --
		# ----------------------------------------------------
		debug.debug("install datas")
		copy_list={}
		self.image_to_build(target, copy_list)
		self.files_to_build(target, copy_list)
		self.paths_to_build(target, copy_list)
		#real copy files
		tools.copy_list(copy_list)
		# remove unneded files (NOT folder ...)
		tools.clean_directory(target.get_build_path_data(self._name, group = "in-shared"), copy_list)
		tools.clean_directory(target.get_build_path_data(self._name, group = "in-bin"), copy_list)
		
		# create local heritage specification
		self._local_heritage.auto_add_build_header()
		self._sub_heritage_list.add_heritage(self._local_heritage)
		
		# ----------------------------------------------------
		# -- create package								 --
		# ----------------------------------------------------
		if	self._type[:6] == 'BINARY' \
		   or self._type == 'PACKAGE':
			debug.verbose("Request creating of package : " + str(self._name))
			debug.extreme_verbose("Heritage : " + str(self._local_heritage))
			# TODO : Do package for library ...
			if target.end_generate_package == True:
				# generate the package with his properties ...
				if "Android" in target.get_type():
					self._sub_heritage_list.add_heritage(self._local_heritage)
				elif self._type == 'PACKAGE':
					self._sub_heritage_list.add_heritage(self._local_heritage)
				debug.extreme_verbose("HeritageList : " + str(self._sub_heritage_list))
				target.make_package(self._name, self._package_prop, os.path.join(self._origin_path, ".."), self._sub_heritage_list)
		# return local dependency ...
		return copy.deepcopy(self._sub_heritage_list)
	
	##
	## @brief Clean the build environement (in build, staging)
	## @param[in] self (handle) Class handle
	## @param[in] target (handle) Target object
	## @return (bool) True if clean is done
	##
	# call here to clean the module
	def clean(self, target):
		if self._type=='PREBUILD':
			# nothing to add ==> just dependence
			None
			return True
		elif	self._type=='LIBRARY' \
			 or self._type=='LIBRARY_DYNAMIC' \
			 or self._type=='LIBRARY_STATIC':
			# remove path of the lib ... for this targer
			pathbuild = target.get_build_path(self._name)
			debug.info("remove path : '" + pathbuild + "'")
			tools.remove_path_and_sub_path(pathbuild)
			return True
		elif	self._type == 'BINARY' \
			 or self._type == 'BINARY_DYNAMIC' \
			 or self._type == 'BINARY_STAND_ALONE' \
			 or self._type=='PACKAGE':
			# remove path of the lib ... for this targer
			pathbuild = target.get_build_path(self._name)
			debug.info("remove path : '" + pathbuild + "'")
			tools.remove_path_and_sub_path(pathbuild)
			pathStaging = target.get_staging_path(self._name)
			debug.info("remove path : '" + pathStaging + "'")
			tools.remove_path_and_sub_path(pathStaging)
			return True
		debug.error("Did not known the element type ... (impossible case) type=" + self._type)
		return False
	
	##
	## @brief Add a tools in dependency
	## @param[in] self (handle) Class handle
	## @param[in] list ([string,...] or string) Name(s) of the tools
	## @return None
	##
	def add_tools(self, list):
		tools.list_append_to(self._tools, list, True)
	
	##
	## @brief Add a dependency on this module
	## @param[in] self (handle) Class handle
	## @param[in] list ([string,...] or string) Name(s) of the modules dependency
	## @return None
	##
	def add_depend(self, list):
		tools.list_append_to(self._depends, list, True)
	
	##
	## @brief Add an optionnal dependency on this module
	## @param[in] self (handle) Class handle
	## @param[in] module_name (string) Name of the optionnal dependency
	## @param[in] compilation_flags ([string,string]) flag to add if dependency is found.
	## @param[in] compilation_flags_not_found ([string,string]) flag to add if dependency is NOT found.
	## @param[in] export (bool) export the flat that has been requested to add if module is present.
	## @param[in] src_file ([string,...]) File to compile if the dependecy if found.
	## @param[in] header_file ([string,...]) File to add in header if the dependecy if found.
	## @return None
	##
	def add_optionnal_depend(self, module_name, compilation_flags=None, export=False, src_file=[], header_file=[], compilation_flags_not_found=None):
		if compilation_flags == None:
			compilation_flags = ["", ""]
		if compilation_flags_not_found == None:
			compilation_flags_not_found = ["", ""]
		tools.list_append_and_check(self._depends_optionnal, [module_name, compilation_flags, export, src_file, header_file, compilation_flags_not_found], True)
	
	##
	## @brief Add a path to include when build
	## @param[in] self (handle) Class handle
	## @param[in] list ([string,...] or string) List of path to include (default: local path) only relative path...
	## @param[in] type (string) inclusion group name 'c', 'c++', 'java' ...
	## @param[in] export (bool) export the include path.
	## @return None
	##
	def add_path(self, list=".", type='c', export=False):
		if tools.get_type_string(list) == "list":
			add_list = []
			for elem in list:
				if	 len(elem) > 1 \
				   and elem[0] == '/':
					# unix case
					debug.warning(" add_path(" + str(list) + ")")
					debug.warning("[" + self._name + "] Not permited to add a path that start in / directory (only relative path) (compatibility until 2.x)")
					add_list.append(elem)
				elif	 len(elem) > 2 \
					 and elem[1] == ':':
					# windows case :
					debug.warning(" add_path(" + str(list) + ")")
					debug.warning("[" + self._name + "] Not permited to add a path that start in '" + elem[0] + ":' directory (only relative path) (compatibility until 2.x)")
					add_list.append(elem)
				if elem == ".":
					add_list.append(tools.get_current_path(self._origin_file))
				else:
					add_list.append(os.path.join(tools.get_current_path(self._origin_file), elem))
		else:
			if	 len(list) > 1 \
			   and list[0] == '/':
				# unix case
				debug.warning(" add_path(" + str(list) + ")")
				debug.warning("[" + self._name + "] Not permited to add a path that start in / directory (only relative path) (compatibility until 2.x)")
				add_list = list
			elif	 len(list) > 2 \
				 and list[1] == ':':
				# windows case :
				debug.warning(" add_path(" + str(list) + ")")
				debug.warning("[" + self._name + "] Not permited to add a path that start in '" + list[0] + ":' directory (only relative path) (compatibility until 2.x)")
				add_list = list
			elif list == ".":
				add_list = tools.get_current_path(self._origin_file)
			else:
				add_list = os.path.join(tools.get_current_path(self._origin_file), list)
		debug.verbose("Convert path : " + str(list) + " in " + str(add_list))
		self._add_path(add_list, type, export)
	
	##
	## @brief (INTERNAL API) Add a path to include when build
	## @param[in] self (handle) Class handle
	## @param[in] list ([string,...] or string) List of path to include (default: local path)
	## @param[in] type (string) inclusion group name 'c', 'c++', 'java' ...
	## @param[in] export (bool) export the include path.
	## @return None
	##
	def _add_path(self, list=".", type='c', export=False):
		if export == True:
			tools.list_append_to_2(self._path["export"], type, list)
		else:
			tools.list_append_to_2(self._path["local"], type, list)
	
	##
	## @brief Add compilation flags
	## @param[in] self (handle) Class handle
	## @param[in] type (string) inclusion group name 'c', 'c++', 'java' ...
	## @param[in] list ([string,...] or string) List of path to include
	## @param[in] export (bool) export the flag that has been requested to add if module is present.
	## @return None
	##
	def add_flag(self, type, list, export=False):
		if export == True:
			tools.list_append_to_2(self._flags["export"], type, list)
		else:
			tools.list_append_to_2(self._flags["local"], type, list)
	
	def add_link_model(self, base_path, libs, static=True, dynamic=True, export=False):
		pass
	##
	## @brief Set the compilation version of the 
	## @param[in] self (handle) Class handle
	## @param[in] compilator_type (string) type of compilator: ["c++", "c"]
	## @param[in] version (int) year of the C/C++ version [1989, 1990, 1999, 2003, 2011, 2014, 2017, ...]
	## @param[in] same_as_api (bool) export the vertion on the API (otherwise the API version is the lowest)
	## @param[in] gnu (bool) Force gnu interface
	## @return None
	##
	def compile_version(self, compilator_type, version, same_as_api=True, gnu=False):
		if	compilator_type == "c++" \
		   or compilator_type == "C++":
			cpp_version_list = [1999, 2003, 2011, 2014, 2017, 2020, 2023]
			if version not in cpp_version_list:
				debug.error("[" + self._name + "] Can not select CPP version : " + str(version) + " not in " + str(cpp_version_list))
			# select API version:
			api_version = 1999
			if same_as_api == True:
				api_version = version
			self._flags["local"]["c++-version"] = { "version":version,
													"gnu":gnu
												  }
			self._flags["export"]["c++-version"] = api_version
			if gnu == True and same_as_api == True:
				debug.debug("[" + self._name + "] Can not propagate the gnu extention of the CPP vesion for API");
		elif	compilator_type == "c" \
			 or compilator_type == "C":
			c_version_list = [1989, 1990, 1999, 2011, 2017, 2018]
			if version not in c_version_list:
				debug.error("[" + self._name + "] Can not select C version : " + str(version) + " not in " + str(c_version_list))
			# select API version:
			api_version = 1999
			if same_as_api == True:
				api_version = version
			self._flags["local"]["c-version"] = { "version":version,
												  "gnu":gnu
												}
			self._flags["export"]["c-version"] = api_version
			if gnu == True and same_as_api == True:
				debug.debug("[" + self._name + "] Can not propagate the gnu extension of the C version for API");
		else:
			debug.warning("[" + self._name + "] Can not set version of compilator:" + str(compilator_type));
	
	##
	## @brief Add source file to compile
	## @param[in] self (handle) Class handle
	## @param[in] list_values ([string,...] or string) File(s) to compile (auto detect the compiler to use...)
	## @param[in] builder_name (string) builder name
	## @return None
	##
	def add_src_file(self, list_values, builder_name=None):
		if type(list_values) == str:
			list_values = [list_values]
		if builder_name == None:
			for elem in list_values:
				extention = elem.split(".")[-1]
				builder_name = builder.find_builder_with_input_extention(extention);
				self.add_src_file(elem, builder_name)
		else:
			debug.extreme_verbose(" add_src_file_type  ==> " + str(self._src.keys()) + " with builder name " + str(builder_name));
			if builder_name not in self._src.keys():
				self._src[builder_name] = [];
			tools.list_append_to(self._src[builder_name], list_values, True);
	
	##
	## @brief Add all files in a specific path as source file to compile
	## @param[in] self (handle) Class handle
	## @param[in] base_path (string) Path where to search files
	## @param[in] regex (string) regular expression of the search
	## @param[in] recursive (bool) Search in resursive mode
	## @return None
	##
	def add_src_path(self, base_path, regex="*", recursive=False):
		if len(base_path) == 0:
			debug.error("[" + self.get_name() + "] ==> no path set for function add_src_path")
		if	base_path[0] == '/' \
		   or base_path[0] == '\\':
			debug.error("[" + self.get_name() + "] ==> use relative path for function add_src_path")
		list_of_file = tools.get_list_of_file_in_path(os.path.join(self._origin_path, base_path), regex=regex, recursive=recursive, remove_path=self._origin_path)
		if list_of_file == None:
			debug.warning("[" + self.get_name() + "] ==> Can not find any file : " + os.path.join(self._origin_path, base_path) + " " + regex)
			return
		debug.debug("[" + self.get_name() + "] add " + str(len(list_of_file)) + " file(s)")
		self.add_src_file(list_of_file)
	
	##
	## @brief An an header file in the install directory
	## @param[in] self (handle) Class handle
	## @param[in] list ([string,...] or string) List of element that is needed to install
	## @param[in] destination_path (string) Path to install the files (remove all the path of the file)
	## @param[in] clip_path (string) Remove a part of the path set in the list and install data in generic include path
	## @param[in] recursive (bool) when use regexp in file list ==> we can add recursive property
	##
	## @note see add_header_path for a simple integration
	##
	## @code
	##	  my_module.add_header_file([
	##		  'include/ewol/widget.h',
	##		  'include/ewol/context/context.h',
	##		  ])
	## @endcode
	## Here the user need to acces to the file wrote: @code #include <include/ewol/cotext/context.h> @endcode
	##
	## We can simplify it:
	## @code
	##	  my_module.add_header_file([
	##		  'include/ewol/widget.h',
	##		  'include/ewol/context/context.h',
	##		  ],
	##		  destination_path='ewol')
	## @endcode
	## Here the user need to acces to the file wrote: @code #include <ewol/context.h> @endcode ==> the internal path has been removed
	##
	## An other way is:
	## @code
	##	  my_module.add_header_file([
	##		  'include/ewol/widget.h',
	##		  'include/ewol/context/context.h',
	##		  ],
	##		  clip_path='include')
	## @endcode
	## Here the user need to acces to the file wrote: @code #include <ewol/context/context.h> @endcode ==> it just remove the include data
	##
	## With a copy all methode:
	## @code
	##	  my_module.add_header_file(
	##		  'include/*.h',
	##		  recursive=True)
	## @endcode
	## Here the user need to acces to the file wrote: @code #include <ewol/context/context.h> @endcode ==> it just remove the include data
	## 
	## @return None
	##
	def add_header_file(self, list, destination_path=None, clip_path=None, recursive=False, builder_name=None):
		if builder_name == None:
			builder_name = "*";
		if destination_path != None:
			debug.verbose("Change destination PATH: '" + str(destination_path) + "'")
		new_list = []
		if tools.get_type_string(list) == "string":
			list = [list]
		for elem in list:
			base = os.path.basename(elem)
			if destination_path != None:
				if clip_path != None:
					debug.error("can not use 'destination_path' and 'clip_path' at the same time ...");
				if	'*' in base \
				   or '[' in base \
				   or '(' in base:
					new_list.append({"src":elem,
									 "multi-dst":destination_path,
									 "recursive":recursive})
				else:
					new_list.append({"src":elem,
									 "dst":os.path.join(destination_path, base),
									 "recursive":recursive})
			else:
				if clip_path == None:
					if	'*' in base \
					   or '[' in base \
					   or '(' in base:
						new_list.append({"src":elem,
										 "multi-dst":"",
										 "recursive":recursive})
					else:
						new_list.append({"src":elem,
										 "dst":elem,
										 "recursive":recursive})
				else:
					if len(clip_path)>len(elem):
						debug.error("can not clip a path with not the same name: '" + clip_path + "' != '" + elem + "' (size too small)")
					if clip_path != elem[:len(clip_path)]:
						debug.error("can not clip a path with not the same name: '" + clip_path + "' != '" + elem[:len(clip_path)] + "'")
					out_elem = elem[len(clip_path):]
					while	 len(out_elem) > 0 \
						  and out_elem[0] == "/":
						out_elem = out_elem[1:]
					if	'*' in base \
					   or '[' in base \
					   or '(' in base:
						new_list.append({"src":elem,
										 "multi-dst":"",
										 "recursive":recursive})
					else:
						new_list.append({"src":elem,
										 "dst":out_elem,
										 "recursive":recursive})
		if builder_name not in self._header.keys():
			self._header[builder_name] = [];
		tools.list_append_to(self._header[builder_name], new_list, True)
	
	##
	## @brief An an header path in the install directory
	## @param[in] self (handle) Class handle
	## @param[in] base_path (string) Path where to search files
	## @param[in] regex (string) regular expression of the search
	## @param[in] clip_path (string) Remove a part of the path set in the list and install data in generic include path
	## @param[in] recursive (bool) Search in resursive mode
	## @param[in] destination_path (string) Path to install the files (remove all the path of the file)
	## @return None
	##
	def add_header_path(self, base_path, regex="*", clip_path=None, recursive=False, destination_path=None, builder_name=None):
		if	base_path[-1] == '/' \
		   or base_path[-1] == '\\':
			self.add_header_file(base_path + regex, clip_path=clip_path, recursive=recursive, destination_path=destination_path, builder_name=builder_name)
		else:
			self.add_header_file(base_path + "/" + regex, clip_path=clip_path, recursive=recursive, destination_path=destination_path, builder_name=builder_name)
	##
	## @brief Many library need to generate dynamic data file, use this to add dynamic generated files
	## @param[in] self (handle) Class handle
	## @param[in] data_file (string) Data of the file that is generated
	## @param[in] destination_path (string) Path where to install data
	## @param[in] install_element (bool) add the file in the include path and not only in the generate path
	## @note this does not rewrite the file if it is not needed
	## @return None
	##
	def add_generated_data_file(self, data_file, destination_path, install_element=False):
		self._generate_file.append({
			"type":"data",
			"data":data_file,
			"filename":destination_path,
			"install":install_element
			});
	##
	## @brief Many library need to generate dynamic file configuration, use this to generate your configuration and add it in the include path
	## @param[in] self (handle) Class handle
	## @param[in] data_file (string) Data of the file that is generated
	## @param[in] destination_path (string) Path where to install data
	## @param[in] install_element (bool) add the file in the include path and not only in the generate path
	## @note this does not rewrite the file if it is not needed
	## @return None
	##
	def add_generated_header_file(self, data_file, destination_path, install_element=False):
		self._generate_file.append({
			"type":"header",
			"data":data_file,
			"filename":destination_path,
			"install":install_element
			});
	##
	## @brief Many library need to generate dynamic file to compile, use this to create and add to build your files
	## @param[in] self (handle) Class handle
	## @param[in] data_file (string) Data of the file that is generated
	## @param[in] destination_path (string) Path where to install data
	## @note this does not rewrite the file if it is not needed
	## @return None
	##
	def add_generated_src_file(self, data_file, destination_path):
		self._generate_file.append({
			"type":"src",
			"data":data_file,
			"filename":destination_path,
			"install":False
			});
	
	##
	## @brief Add action to do for the module
	## @param[in] action (function handle) Function to call to execure action
	## @param[in] data (*) Data to set at the action function
	## @return None
	##
	def add_action(self, action, data=None, name=None):
		debug.verbose("add action : " + str(name))
		self._actions.append({
			"name":name,
			"action":action,
			"data":data
			})
	
	##
	## @brief copy image in the module datas
	## @param[in] self (handle) Class handle
	## @param[in] source (string) Source filename of the image
	## @param[in] destination (string) Destination filename in the image
	## @param[in] sizeX (int) new image width
	## @param[in] sizeY (int) new image height
	## @return None
	##
	def copy_image(self, source, destination='', sizeX=-1, sizeY=-1):
		self._image_to_copy.append([source, destination, sizeX, sizeY])
	
	##
	## @brief Copy the file in the module datas
	## @param[in] self (handle) Class handle
	## @param[in] source (string) filename of the souce to copy
	## @param[in] destination (string) Destination path to install data
	## @return None
	##
	def copy_file(self, source, destination='', group_folder="in-shared"):
		groups = ["in-shared", "in-bin"];
		if group_folder not in groups:
			debug.error("Can not add file in other group than " + str(groups) + " but require: " + str(group_folder))
		self._files.append([source, destination, group_folder])
	
	##
	## @brief Copy the path in the module datas
	## @param[in] self (handle) Class handle
	## @param[in] source (string) path of the souce to copy
	## @param[in] destination (string) Destination path to install data
	## @return None
	##
	def copy_path(self, source, destination='', group_folder="in-shared"):
		groups = ["in-shared", "in-bin"];
		if group_folder not in groups:
			debug.error("Can not add file in other group than " + str(groups) + " but require: " + str(group_folder))
		self._paths.append([source, destination, group_folder])
	
	##
	## @brief Print the list to help
	## @param[in] self (handle) Class handle
	## @param[in] description (string) main help string
	## @param[in] description ([string,...]) List of possibilities to display
	## @return None
	##
	def _print_list(self, description, input_list):
		if tools.get_type_string(input_list) == "list":
			if len(input_list) > 0:
				print('		' + str(description))
				for elem in input_list:
					print('			' + str(elem))
		else:
			print('		' + str(description))
			print('			' + str(input_list))
	
	##
	## @brief Display help of the module (dump)
	## @param[in] self (handle) Class handle
	## @return None
	##
	def display(self):
		print('-----------------------------------------------');
		print(' module : "' + self._name + "'");
		print('-----------------------------------------------');
		print('	type:"' + str(self._type) + "'");
		print('	file:"' + str(self._origin_file) + "'");
		print('	path:"' + str(self._origin_path) + "'");
		if "LICENSE" in self._package_prop.keys(): 
			print('	license:"' + str(self._package_prop["LICENSE"]) + "'");
		
		self._print_list('depends',self._depends);
		self._print_list('depends_optionnal', self._depends_optionnal);
		print('	action count=' + str(len(self._actions)) + str(self._actions));
		
		for element in self._flags["local"]:
			value = self._flags["local"][element];
			self._print_list('flags(' + str(element) + ')', value);
		
		for element in self._flags["export"]:
			value = self._flags["export"][element];
			self._print_list('flags export(' + str(element) + ')', str(value));
		if len(self._src.keys()) != 0:
			for key in self._src.keys():
				value = self._src[key];
				self._print_list('sources(' + key + ') ' + str(len(value)), value);
		if len(self._header.keys()) != 0:
			for key in self._header.keys():
				value = self._header[key];
				self._print_list('headers(' + key + ') ' + str(len(value)), [ iii['src'] for iii in value]);
		self._print_list('files', self._files);
		self._print_list('paths', self._paths);
		for element in self._path["local"]:
			value = self._path["local"][element];
			self._print_list('local path(' + str(element) + ') ' + str(len(value)), value);
		
		for element in self._path["export"]:
			value = self._path["export"][element];
			self._print_list('export path(' + str(element) + ') ' + str(len(value)), value);
		print('-----------------------------------------------')
		return True;
	
	def check_rules(self, type, rules):
		if	(	 (	type == 'LIBRARY' \
					  or type == 'LIBRARY_DYNAMIC' \
					  or type == 'LIBRARY_STATIC' ) \
				and "L" not in rules ) \
		   or (	 type == 'DATA' \
				and "D" not in rules ) \
		   or (	 type == 'PREBUILD'\
				and "P" not in rules ) \
		   or (	 type == 'PACKAGE'\
				and "K" not in rules) \
		   or (	 (	type == 'BINARY' \
					  or type == 'BINARY_DYNAMIC' \
					  or type == 'BINARY_STAND_ALONE')\
				and "B" not in rules ) :
			return True
		return False
	
	# TODO: Add to simplify the display the possibility to check if an element already depend in dependency of an element ???
	def dependency_generate(self, target, tmp_file, step, rules):
		debug.print_element("dot", "dependency.dot", "<<<", self._name)
		if self.check_rules(self._type, rules) == True:
			return
		if step == 1:
			if self._type == 'DATA':
				tmp_file.write('	node [\n');
				tmp_file.write('		shape=Mdiamond;\n');
				tmp_file.write('		style=filled;\n');
				tmp_file.write('		color=red;\n');
				tmp_file.write('		];\n');
			elif self._type == 'PREBUILD':
				tmp_file.write('	node [\n');
				tmp_file.write('		shape=square;\n');
				tmp_file.write('		style=filled;\n');
				tmp_file.write('		color=gray;\n');
				tmp_file.write('		];\n');
			elif	self._type == 'LIBRARY' \
				 or self._type == 'LIBRARY_DYNAMIC' \
				 or self._type == 'LIBRARY_STATIC':
				tmp_file.write('	node [\n');
				tmp_file.write('		shape=ellipse;\n');
				tmp_file.write('		style=filled;\n');
				tmp_file.write('		color=lightblue;\n');
				tmp_file.write('		];\n');
			elif	self._type == 'BINARY' \
				 or self._type == 'BINARY_DYNAMIC' \
				 or self._type == 'BINARY_STAND_ALONE':
				tmp_file.write('	node [\n');
				tmp_file.write('		shape=rectangle;\n');
				tmp_file.write('		style=filled;\n');
				tmp_file.write('		color=green;\n');
				tmp_file.write('		];\n');
			elif self._type == 'PACKAGE':
				return
			tmp_file.write('	' + copy.deepcopy(self._name).replace('-','_')+ ';\n');
		else:
			for elem in self._depends:
				debug.verbose("add depend on: " + elem);
				tmp_module = None
				try:
					tmp_module = target.get_module(elem)
				except:
					target.load_if_needed(elem, optionnal=True)
					try:
						tmp_module = target.get_module(elem)
					except:
						debug.verbose("	==> get error");
				if tmp_module == None:
					debug.verbose("	==> notFound");
					continue
				if self.check_rules(tmp_module._type, rules) == True:
					debug.verbose("	==> not in rules");
					continue
				tmp_file.write('	' + copy.deepcopy(self._name).replace('-','_') + ' -> ' + copy.deepcopy(elem).replace('-','_') + ';\n');
			for elem in self._depends_optionnal:
				elem = elem[0]
				debug.verbose("add depend on: " + elem);
				tmp_module = None
				try:
					tmp_module = target.get_module(elem)
				except:
					target.load_if_needed(elem, optionnal=True)
					try:
						tmp_module = target.get_module(elem)
					except:
						debug.verbose("	==> get error");
				if tmp_module == None:
					debug.verbose("	==> notFound");
					continue
				if self.check_rules(tmp_module._type, rules) == True:
					debug.verbose("	==> not in rules");
					continue
				tmp_file.write('	' + copy.deepcopy(self._name).replace('-','_') + ' -> ' + copy.deepcopy(elem).replace('-','_') + ';\n');
		"""
		tmp_file.write('	module_' + self._name.replace('-','_') + ' {\n');
		tmp_file.write('		style=filled;\n');
		tmp_file.write('		color=blue;\n');
		tmp_file.write('		label="' + self._name + '";\n');
		tmp_file.write('	}\n');
		"""
	
	##
	## @brief Get packaging property variable
	## @param[in] self (handle) Class handle
	## @param[in] name (string) Variable to get: "COMPAGNY_TYPE", "COMPAGNY_NAME", "ICON", "MAINTAINER", "SECTION", "PRIORITY", "DESCRIPTION", "VERSION", "VERSION_CODE", "NAME", "ANDROID_MANIFEST", "ANDROID_JAVA_FILES", "RIGHT", "ANDROID_RESOURCES", "ANDROID_APPL_TYPE", "ADMOD_ID", "APPLE_APPLICATION_IOS_ID", "LICENSE", "ANDROID_SIGN", "ADMOD_POSITION"
	## @return (string) Value assiciated at the package
	##
	def get_pkg(self, name):
		if name in self._package_prop:
			return copy.deepcopy(self._package_prop[name])
		return None
	
	##
	## @brief Set packaging variables
	## @param[in] self (handle) Class handle
	## @param[in] variable (string) Variable to set: "COMPAGNY_TYPE", "COMPAGNY_NAME", "ICON", "MAINTAINER", "SECTION", "PRIORITY", "DESCRIPTION", "VERSION", "VERSION_CODE", "NAME", "ANDROID_MANIFEST", "ANDROID_JAVA_FILES", "RIGHT", "ANDROID_RESOURCES", "ANDROID_APPL_TYPE", "ADMOD_ID", "APPLE_APPLICATION_IOS_ID", "LICENSE", "ANDROID_SIGN", "ADMOD_POSITION"
	## @param[in] value (string) Value assiciated at the package
	## @return None
	##
	def set_pkg(self, variable, value):
		if variable == "COMPAGNY_TYPE":
			#	com : Commercial
			#	net : Network??
			#	org : Organisation
			#	gov : Governement
			#	mil : Military
			#	edu : Education
			#	pri : Private
			#	museum : ...
			if value not in ["", "com", "net", "org", "gov", "mil", "edu", "pri", "museum"]:
				debug.error("can not set the value for this Input : '" + variable + "' : '" + value + "'")
			else:
				self._package_prop[variable] = value
				self._package_prop_default[variable] = False
		elif variable == "COMPAGNY_NAME":
			self._package_prop[variable] = value
			self._package_prop_default[variable] = False
			val2 = value.lower()
			val2 = val2.replace(' ', '')
			val2 = val2.replace('-', '')
			val2 = val2.replace('_', '')
			self._package_prop["COMPAGNY_NAME2"] = val2
			self._package_prop_default["COMPAGNY_NAME2"] = False
		elif variable == "ICON":
			if	 len(value) > 1 \
			   and value[0] == '/':
				# unix case
				debug.warning(" set_pkg('ICON', " + value + ")")
				debug.warning("[" + self._name + "] Not permited to add an ICON that start in / directory (only relative path) (compatibility until 2.x)")
				self._package_prop[variable] = value
			elif	 len(value) > 2 \
				 and value[1] == ':':
				# windows case :
				debug.warning(" set_pkg('ICON', " + value + ")")
				debug.warning("[" + self._name + "] Not permited to add a path that start in '" + value[0] + ":' directory (only relative path) (compatibility until 2.x)")
				self._package_prop[variable] = value
			else:
				self._package_prop[variable] = os.path.join(tools.get_current_path(self._origin_file), value)
			self._package_prop_default[variable] = False
		elif variable == "MAINTAINER":
			self._package_prop[variable] = value
			self._package_prop_default[variable] = False
		elif variable == "SECTION":
			# project section : (must be separate by coma
			#	refer to : http://packages.debian.org/sid/
			#		admin cli-mono comm database debian-installer
			#		debug doc editors electronics devel embedded
			#		fonts games gnome gnu-r gnustep graphics
			#		hamradio haskell httpd interpreters java
			#		kde kernel libdevel libs lisp localization
			#		mail math misc net news ocaml oldlibs otherosfs
			#		perl php python ruby science shells sound tex
			#		text utils vcs video virtual web x11 xfce zope ...
			self._package_prop[variable] = value
			self._package_prop_default[variable] = False
		elif variable == "PRIORITY":
			#list = ["required","important","standard","optional","extra"]
			#if isinstance(value, list):
			if value not in ["required", "important", "standard", "optional", "extra"]:
				debug.error("can not set the value for this Input : '" + variable + "' : '" + value + "'")
			else:
				self._package_prop[variable] = value
				self._package_prop_default[variable] = False
		elif variable == "ANDROID_SIGN":
			if	 len(value) > 1 \
			   and value[0] == '/':
				# unix case
				debug.warning(" set_pkg('ANDROID_SIGN', " + value + ")")
				debug.warning("[" + self._name + "] Not permited to add an ICON that start in / directory (only relative path) (compatibility until 2.x)")
				self._package_prop[variable] = value
			elif	 len(value) > 2 \
				 and value[1] == ':':
				# windows case :
				debug.warning(" set_pkg('ANDROID_SIGN', " + value + ")")
				debug.warning("[" + self._name + "] Not permited to add a path that start in '" + value[0] + ":' directory (only relative path) (compatibility until 2.x)")
				self._package_prop[variable] = value
			else:
				self._package_prop[variable] = os.path.join(tools.get_current_path(self._origin_file), value)
			self._package_prop_default[variable] = False
		elif variable in ["DESCRIPTION",
						  "VERSION",
						  "VERSION_CODE",
						  "NAME",
						  "ANDROID_MANIFEST",
						  "ANDROID_JAVA_FILES",
						  "RIGHT",
						  "ANDROID_RESOURCES",
						  "ANDROID_APPL_TYPE",
						  "ADMOD_ID",
						  "APPLE_APPLICATION_IOS_ID",
						  "LICENSE"]:
			self._package_prop[variable] = value
			self._package_prop_default[variable] = False
		elif variable == "ADMOD_POSITION":
			if value in ["top", "bottom"]:
				self._package_prop[variable] = value
				self._package_prop_default[variable] = False
			else:
				debug.error("not know pkg element : '" + variable + "' with value : '" + value + "' must be [top|bottom]")
		else:
			debug.error("not know pkg element : '" + variable + "'")
	
	##
	## @brief set a package config only if the config has not be change
	## @param[in] self (handle) Class handle
	## @param[in] variable (string) Variable to set: show @ref set_pkg
	## @param[in] value (string) Value assiciated at the package
	## @return None
	##
	def _pkg_set_if_default(self, variable, value):
		if self._package_prop_default[variable] == True:
			self.set_pkg(variable, value)
	
	##
	## @brief add an element in tha package property
	## @param[in] self (handle) Class handle
	## @param[in] variable (string) Variable to set: show @ref set_pkg
	## @param[in] value (string) Value assiciated at the package
	## @return None
	##
	def add_pkg(self, variable, value):
		if variable in self._package_prop:
			self._package_prop[variable].append(value)
		else:
			self._package_prop[variable] = [value]
	
	##
	## @brief Get the version of the module (getted in the global value)
	## @param[in] self (handle) Class handle
	## @return the list of version parameters
	##
	def get_version(self):
		return self._package_prop["VERSION"]
	

__module_list=[]
__start_module_name="_"

##
## @brief Import all File that start with env.get_build_system_base_name() + __start_module_name + XXX and register in the list of modules
## @param[in] path_list List of file that start with env.get_build_system_base_name() in the running worktree (Parse one time ==> faster)
## @return None
##
def import_path(path_list):
	global __module_list
	gld_base = env.get_gld_build_system_base_name()
	global_base = env.get_build_system_base_name()
	debug.debug("MODULE: Init with Files list:")
	for elem in path_list:
		sys.path.append(os.path.dirname(elem))
		# Get file name:
		filename = os.path.basename(elem)
		# Remove global base name:
		if filename[:len(gld_base)] == gld_base:
			# Remove .json at the end:
			filename = filename[len(gld_base):-5]
			# Check if it start with the local patern:
			if filename[:len(__start_module_name)] != __start_module_name:
				debug.extreme_verbose("MODULE:	 NOT-Integrate: '" + filename + "' from '" + elem + "' ==> rejected")
				continue
			# Remove local patern
			module_name = filename[len(__start_module_name):]
			debug.verbose("MODULE:	 Integrate: '" + module_name + "' from '" + elem + "'")
			__module_list.append([module_name, elem, False])
		elif filename[:len(global_base)] == global_base:
			# Remove .py at the end:
			filename = filename[len(global_base):-3]
			# Check if it start with the local patern:
			if filename[:len(__start_module_name)] != __start_module_name:
				debug.extreme_verbose("MODULE:	 NOT-Integrate: '" + filename + "' from '" + elem + "' ==> rejected")
				continue
			# Remove local patern
			module_name = filename[len(__start_module_name):]
			debug.verbose("MODULE:	 Integrate: '" + module_name + "' from '" + elem + "'")
			__module_list.append([module_name, elem, True])
	debug.verbose("New list module: ")
	for elem in __module_list:
		debug.verbose("	" + str(elem[0]))

##
## @brief Check if a module exist
## @param[in] target (handle) @ref lutin.target.Target handle
## @param[in] name (string) Name of the module
## @return (bool) Existance of the module in worktree
##
def exist(target, name):
	global __module_list
	for mod in __module_list:
		debug.verbose("check exist: " + name + " => " + mod[0]);
		if mod[0] == name:
			return True;
	return False

##
## @brief Load a module for a spefic @ref lutin.target.Target
## @param[in] target (handle) @ref lutin.target.Target handle
## @param[in] name (string) Name of the module
## @return (handle) @ref Module handle
##
def load_module(target, name):
	global __module_list
	#debug.warning("Load module: " + str(len(__module_list)) + " => " + str(__module_list));
	for mod in __module_list:
		if mod[0] == name:
			if mod[2]== False:
				# read GLD file
				the_module = moduleGLD.load_module_from_GLD(target, mod[0], os.path.dirname(mod[1]), mod[1])
				target.add_module(the_module)
				return the_module;
			else:
				# Import internal element
				sys.path.append(os.path.dirname(mod[1]))
				debug.verbose("import module : '" + env.get_build_system_base_name() + __start_module_name + name + "'")
				the_module_file = mod[1]
				the_module = __import__(env.get_build_system_base_name() + __start_module_name + name)
				# get basic module properties:
				property = get_module_option(os.path.dirname(mod[1]), the_module, name)
				# configure the module:
				if "configure" in dir(the_module):
					# create the module:
					tmp_element = Module(the_module_file, name, property["type"])
					# overwrite some package default property (if not set by user)
					if property["compagny-type"] != None:
						tmp_element._pkg_set_if_default("COMPAGNY_TYPE", property["compagny-type"])
					if property["compagny-name"] != None:
						tmp_element._pkg_set_if_default("COMPAGNY_NAME", property["compagny-name"])
					if property["maintainer"] != None:
						tmp_element._pkg_set_if_default("MAINTAINER", property["maintainer"])
					if property["name"] != None:
						tmp_element._pkg_set_if_default("NAME", property["name"])
					if property["description"] != None:
						tmp_element._pkg_set_if_default("DESCRIPTION", property["description"])
					if property["license"] != None:
						tmp_element._pkg_set_if_default("LICENSE", property["license"])
					if property["version"] != None:
						tmp_element._pkg_set_if_default("VERSION", property["version"])
					# call user to configure it:
					ret = the_module.configure(target, tmp_element)
					if ret == False:
						# the user request remove the capabilities of this module for this platform
						tmp_element = None
				else:
					debug.warning(" no function 'create' in the module : " + mod[0] + " from:'" + mod[1] + "'")
					continue
				"""
				if property["type"] == "":
					continue
				# configure the module:
				if "configure" in dir(the_module):
					tmp_element = module.Module(the_module_file, name, property["type"], property)
					ret = the_module.configure(target, tmp_element)
					if ret == True:
						debug.warning("configure done corectly : " + mod[0] + " from:'" + mod[1] + "'")
					else:
						debug.warning("configure NOT done corectly : " + mod[0] + " from:'" + mod[1] + "'")
				else:
					debug.warning(" no function 'configure' in the module : " + mod[0] + " from:'" + mod[1] + "'")
					continue
				"""
				# check if create has been done correctly
				if tmp_element == None:
					debug.debug("Request load module '" + name + "' not define for this platform")
				else:
					target.add_module(tmp_element)
					return tmp_element

##
## @brief List all module name
## @return ([string,...]) List of all module names
##
def list_all_module():
	global __module_list
	out = []
	for mod in __module_list:
		if mod[0] not in out:
			out.append(mod[0])
	out.sort()
	return out

##
## @brief List all module with specific filter name
## @param[in] filter (string) regular expression to filter the modules
## @return ([string,...]) List of all module names filter with needed element
##
def list_filtered_module(filter):
	list_of_all_module = list_all_module();
	regex = re.compile(filter)
	return [xxx for xxx in list_of_all_module if regex.match(xxx)]#list(filter(list_of_all_module,r.match))

##
## @brief List all module name whith their desc
## @return ([...,...]) List of all module option @ref get_module_option()
##
def list_all_module_with_desc():
	global __module_list;
	tmp_list = [];
	for mod in __module_list:
		sys.path.append(os.path.dirname(mod[1]));
		if mod[2] == False:
			try:
				data = json.load(open(mod[1],));
				property = moduleGLD.get_module_option_GLD(os.path.dirname(mod[1]), data, mod[0]);
				tmp_list.append(property);
			except json.decoder.JSONDecodeError as ex:
				debug.error("inconsistent file " + str(mod[1]) + " ==> " + str(ex))
				
		else:
			the_module = __import__(env.get_build_system_base_name() + __start_module_name + mod[0]);
			property = get_module_option(os.path.dirname(mod[1]), the_module, mod[0]);
			tmp_list.append(property);
	return tmp_list;



##
## @brief Get a specific module options
## @param[in] path (string) Pathof the module
## @param[in] the_module (handle) @ref Module handle
## @param[in] name (string) Name of the module
## @return a Map with the keys: "name", "description", "type", "sub-type", "license", "compagny-type", "compagny-name", "maintainer", "version", "version-id"
##
def get_module_option(path, the_module, name):
	type = None
	sub_type = None
	description = None
	license = None
	compagny_type = None
	compagny_name = None
	maintainer = None
	version = None
	version_id = None
	group_id = None
	
	list_of_function_in_factory = dir(the_module)
	
	if "get_type" in list_of_function_in_factory:
		type = the_module.get_type()
	else:
		debug.error(" function get_type() must be provided in the module: " + name)
	
	if "get_sub_type" in list_of_function_in_factory:
		sub_type = the_module.get_sub_type()
	
	if "get_desc" in list_of_function_in_factory:
		description = the_module.get_desc()
	
	if "get_licence" in list_of_function_in_factory:
		license = the_module.get_licence()
	
	if "get_compagny_type" in list_of_function_in_factory:
		compagny_type = the_module.get_compagny_type()
		#	com : Commercial
		#	net : Network??
		#	org : Organisation
		#	gov : Governement
		#	mil : Military
		#	edu : Education
		#	pri : Private
		#	museum : ...
		compagny_type_list = ["", "com", "net", "org", "gov", "mil", "edu", "pri", "museum"]
		if compagny_type not in compagny_type_list:
			debug.warning("[" + name + "] type of the company not normal: " + compagny_type + " not in " + str(compagny_type_list))
	
	if "get_compagny_name" in list_of_function_in_factory:
		compagny_name = the_module.get_compagny_name()
	
	if "get_maintainer" in list_of_function_in_factory:
		maintainer = tools.get_maintainer_from_file_or_direct(path, the_module.get_maintainer())
	
	if "get_version" in list_of_function_in_factory:
		version = tools.get_version_from_file_or_direct(path, the_module.get_version())
	
	if "get_version_id" in list_of_function_in_factory:
		version_id = the_module.get_version_id()
	if compagny_type != None:
		group_id = compagny_type;
		if compagny_name != None:
			group_id += "." + compagny_name
	elif compagny_name != None:
		group_id = compagny_name;
	
	return {
		   "name":name,
		   "description":description,
		   "type":type,
		   "sub-type":sub_type,
		   "license":license,
		   "license-file": None,
		   "compagny-type":compagny_type,
		   "compagny-name":compagny_name,
		   "group-id":group_id,
		   "maintainer":maintainer,
		   "version":version,
		   "version-id":version_id
		   }


