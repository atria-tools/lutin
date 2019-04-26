#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license MPL v2.0 (see license file)
##

import sys
import os
import inspect
import fnmatch
import datetime
# Local import
from realog import debug
from . import module
from . import tools
from . import env
##
## @brief System class represent the pre-build Module that are already install and accessible in the system environment
##
class System:
	##
	## @brief Constructor
	## @param[in] self (handle) Class handle
	## @return None
	##
	def __init__(self):
		self._valid=False;
		self._help="";
		self._export_depends=[]
		self._export_flags={}
		self._export_src=[]
		self._export_path=[]
		self._action_on_state={}
		self._headers=[]
		self._version=None
	
	##
	## @brief Set the help of this system Module
	## @param[in] self (handle) Class handle
	## @param[in] help (string) Help for the user
	## @return None
	##
	def set_help(self, help):
		self._help = help;
	
	##
	## @brief Get the help of this system Module
	## @param[in] self (handle) Class handle
	## @return (string) Help for the user
	##
	def get_help(self):
		return self._help;
	
	##
	## @brief Set validity state of the system Module
	## @param[in] self (handle) Class handle
	## @param[in] state (bool) New valididty state of the system module
	## @return None
	##
	def set_valid(self, state):
		self._valid = state
	
	##
	## @brief Get validity state of the system Module
	## @param[in] self (handle) Class handle
	## @return (bool) New valididty state of the system module
	##
	def get_valid(self):
		return self._valid
	
	##
	## @brief Add source element
	## @param[in] self (handle) Class handle
	## @param[in] list ([string,...]) List of all Files to add. ex: *.a, *.so ...
	## @return None
	##
	def add_sources(self, list):
		tools.list_append_to(self._export_src, list)
	
	##
	## @brief Add include path of the sources
	## @param[in] self (handle) Class handle
	## @param[in] list ([string,...]) List of all path to add in the -I include element
	## @return None
	##
	# todo : add other than C ...
	def add_path(self, list):
		tools.list_append_to(self._export_path, list)
	
	##
	## @brief Add a dependency on this module
	## @param[in] self (handle) Class handle
	## @param[in] list ([string,...] or string) Name(s) of the modules dependency
	## @return None
	##
	def add_depend(self, list):
		tools.list_append_to(self._export_depends, list, True)
	
	##
	## @brief Add compilation flags
	## @param[in] self (handle) Class handle
	## @param[in] type (string) inclusion group name 'c', 'c++', 'java' ...
	## @param[in] list ([string,...] or string) List of path to include
	## @return None
	##
	def add_flag(self, type, list):
		tools.list_append_to_2(self._export_flags, type, list)
	
	##
	## @brief Set version of the module
	## @param[in] self (handle) Class handle
	## @param[in] version_list ([int,...]) Ids of the version. ex: [1,2,5] or [0,8,"dev"]
	## @return None
	##
	def set_version(self, version_list):
		self._version = version_list
	
	## @copydoc lutin.module.Target.add_action
	def add_action(self, name_of_state="PACKAGE", level=5, name="no-name", action=None):
		if name_of_state not in self._action_on_state:
			self._action_on_state[name_of_state] = [[level, name, action]]
		else:
			self._action_on_state[name_of_state].append([level, name, action])
	
	## @copydoc lutin.module.Module.add_header_file
	def add_header_file(self, list, destination_path=None, clip_path=None, recursive=False):
		self._headers.append({
		  "list":list,
		  "dst":destination_path,
		  "clip":clip_path,
		  "recursive":recursive
		  })
	##
	## @brief Generate a string representing the class (for str(xxx))
	## @param[in] self (handle) Class handle
	## @return (string) string of str() convertion
	##
	def __repr__(self):
		return "{lutin.System}"
	
	##
	## @brief Configure a module with internal datas
	## @param[in] self (handle) Class handle
	## @param[in] target (handle) @ref lutin.module.Target handle
	## @param[in] module (handle) @ref lutin.module.Module handle
	## @return None
	##
	def configure_module(self, target, module):
		# add element flags to export
		for elem in self._export_flags:
			debug.verbose("add element :" + str(elem) + " elems=" + str(self._export_flags[elem]))
			module.add_flag(elem, self._export_flags[elem], export=True)
		# add module dependency
		if self._export_depends != []:
			module.add_depend(self._export_depends)
		# add exporting sources
		if self._export_src != []:
			module.add_src_file(self._export_src)
		# add export path
		if self._export_path != []:
			# no control on API
			module._add_path(self._export_path, export=True)
		# Export all actions ...
		for elem in self._action_on_state:
			level, name, action = self._action_on_state[elem]
			target.add_action(elem, level, name, action)
		for elem in self._headers:
			module.add_header_file(
			    elem["list"],
			    destination_path=elem["dst"],
			    clip_path=elem["clip"],
			    recursive=elem["recursive"])
		if self._version != None:
			module.set_pkg("VERSION", self._version);
		


##
## @brief Create a @ref lutin.module.Module for the system list elements
## @param[in] target (handle) @ref lutin.target.Target handle
## @param[in] name (string) Name of the system module
##
def create_module_from_system(target, dict):
	my_module = module.Module(dict["path"], dict["name"], 'PREBUILD')
	dict["system"].configure_module(target, my_module)
	return my_module




# Dictionnaire of Target name
#   inside table of ["Name of the lib", "path of the lib", boolean loaded, module loaded]
__system_list={}
__start_system_name="System_"

##
## @brief Import all File that start with env.get_build_system_base_name() + __start_system_name + XXX and register in the list of System
## @param[in] path_list ([string,...]) List of file that start with env.get_build_system_base_name() in the running worktree (Parse one time ==> faster)
##
def import_path(path_list):
	global __system_list
	global_base = env.get_build_system_base_name()
	debug.debug("SYSTEM: Init with Files list:")
	for elem in path_list:
		sys.path.append(os.path.dirname(elem))
		# Get file name:
		filename = os.path.basename(elem)
		# Remove .py at the end:
		filename = filename[:-3]
		# Remove global base name:
		filename = filename[len(global_base):]
		# Check if it start with the local patern:
		if filename[:len(__start_system_name)] != __start_system_name:
			debug.extreme_verbose("SYSTEM:     NOT-Integrate: '" + filename + "' from '" + elem + "' ==> rejected")
			continue
		# Remove local patern
		system_name = filename[len(__start_system_name):]
		system_type, system_name = system_name.split('_')
		debug.verbose("SYSTEM:     Integrate: '" + system_type + "':'" + system_name + "' from '" + elem + "'")
		if system_type in __system_list:
			__system_list[system_type].append({"name":system_name,
			                                   "path":elem,
			                                   "system":None,
			                                   "loaded":False,
			                                   "exist":False,
			                                   "module":None})
		else:
			__system_list[system_type] = [{"name":system_name,
			                               "path":elem,
			                               "system":None,
			                               "loaded":False,
			                               "exist":False,
			                               "module":None}]
	debug.verbose("New list system: ")
	for elem in __system_list:
		debug.verbose("    " + str(elem))
		for val in __system_list[elem]:
			debug.verbose("        " + str(val["name"]))

##
## @brief Display all the system binary that can be used
##
def display():
	global __system_list
	for elementName in __system_list:
		debug.info("SYSTEM:     Integrate system: '" + elementName +"'")
		for data in __system_list[elementName]:
			debug.info("SYSTEM:    '" + data["name"] +"' in " + data["path"])

##
## @brief Check if a system Module is availlable for a specific target
## @param[in] lib_name (string) Name of the Library
## @param[in] list_target_name ([string,...]) list of name of the target (ordered by request order)
## @param[in] target (handle) Handle on the @ref Target build engine
## @return (bool) find the system lib or not
##
def exist(lib_name, list_target_name, target) :
	global __system_list
	debug.verbose("exist= " + lib_name + " in " + str(list_target_name))
	find_target = False
	for target_name in list_target_name:
		if target_name in __system_list:
			find_target = True
	if find_target == False:
		return False
	for target_name in reversed(list_target_name):
		if target_name not in __system_list:
			continue
		for data in __system_list[target_name]:
			if data["name"] == lib_name:
				# we find it in the List ==> need to check if it is present in the system :
				if data["loaded"] == False:
					debug.verbose("add to path: '" + os.path.dirname(data["path"]) + "'")
					sys.path.append(os.path.dirname(data["path"]))
					debug.verbose("import system : '" + data["name"] + "'")
					the_system = __import__(env.get_build_system_base_name() + __start_system_name + target_name + "_" + data["name"])
					#create the system module
					debug.verbose("SYSTEM: request: " + str(data["name"]))
					if "System" in dir(the_system):
						data["system"] = the_system.System(target)
						data["exist"] = data["system"].get_valid()
						"""
						if data["exist"] == False:
							debug.warning("Can not Import: '" + data["name"] + "' ==> disabled")
						"""
					else:
						debug.warning("Not find: '" + data["name"] + "' ==> get exception")
				return data["exist"]
	return False

##
## @brief Load a system Module for a specific target
## @param[in] target (handle) Handle on the @ref Target build engine
## @param[in] lib_name (string) Name of the Library
## @param[in] list_target_name ([string,...]) list of name of the target (ordered by request order)
## @return None
##
def load(target, lib_name, list_target_name):
	global __system_list
	find_target = False
	for target_name in list_target_name:
		if target_name in __system_list:
			find_target = True
	if find_target == False:
		debug.error("you must call this function after checking of the system exist() !1!")
		return
	for target_name in reversed(list_target_name):
		if target_name not in __system_list:
			continue
		for data in __system_list[target_name]:
			if data["name"] == lib_name:
				if data["exist"] == False:
					debug.error("you must call this function after checking of the system exist() !2!")
				if data["module"] == None:
					# create a module from the system interface...
					data["module"] = create_module_from_system(target, data)
					data["loaded"] = True
				target.add_module(data["module"])
				return

