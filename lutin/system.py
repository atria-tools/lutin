#!/usr/bin/python
# -*- coding: utf-8 -*-
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
from . import module
from . import tools
from . import env

class System:
	def __init__(self):
		self.valid=False;
		self.help="";
		self.export_depends=[]
		self.export_flags={}
		self.export_src=[]
		self.export_path=[]
		self.action_on_state={}
	
	def add_export_sources(self, list):
		tools.list_append_to(self.export_src, list)
	
	# todo : add other than C ...
	def add_export_path(self, list):
		tools.list_append_to(self.export_path, list)
	
	def add_module_depend(self, list):
		tools.list_append_to(self.export_depends, list, True)
	
	def add_export_flag(self, type, list):
		tools.list_append_to_2(self.export_flags, type, list)
	
	def add_action(self, name_of_state="PACKAGE", level=5, name="no-name", action=None):
		if name_of_state not in self.action_on_add_src_filestate:
			self.action_on_state[name_of_state] = [[level, name, action]]
		else:
			self.action_on_state[name_of_state].append([level, name, action])
	
	def __repr__(self):
		return "{lutin.System}"



def create_module_from_system(target, dict):
	myModule = module.Module(dict["path"], dict["name"], 'PREBUILD')
	# add element flags to export
	for elem in dict["system"].export_flags:
		debug.verbose("add element :" + str(elem) + " elems=" + str(dict["system"].export_flags[elem]))
		myModule.add_export_flag(elem, dict["system"].export_flags[elem])
	# add module dependency
	myModule.add_module_depend(dict["system"].export_depends)
	# add exporting sources
	myModule.add_src_file(dict["system"].export_src)
	# add export path
	myModule.add_export_path(dict["system"].export_path)
	# Export all actions ...
	for elem in dict["system"].action_on_state:
		level, name, action = dict["system"].action_on_state[elem]
		target.add_action(elem, level, name, action)
	
	return myModule




# Dictionnaire of Target name
#   inside table of ["Name of the lib", "path of the lib", boolean loaded, module loaded]
system_list={}
__start_system_name="System_"

def import_path(path_list):
	global system_list
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
		if system_type in system_list:
			system_list[system_type].append({"name":system_name,
			                               "path":elem,
			                               "system":None,
			                               "loaded":False,
			                               "exist":False,
			                               "module":None})
		else:
			system_list[system_type] = [{"name":system_name,
			                           "path":elem,
			                           "system":None,
			                           "loaded":False,
			                           "exist":False,
			                           "module":None}]
	debug.verbose("New list system: ")
	for elem in system_list:
		debug.verbose("    " + str(elem))
		for val in system_list[elem]:
			debug.verbose("        " + str(val["name"]))


def display():
	global system_list
	for elementName in system_list:
		debug.info("SYSTEM:     Integrate system: '" + elementName +"'")
		for data in system_list[elementName]:
			debug.info("SYSTEM:    '" + data["name"] +"' in " + data["path"])

def exist(lib_name, target_name, target) :
	global system_list
	debug.verbose("exist= " + lib_name + " in " + target_name)
	if target_name not in system_list:
		return False
	for data in system_list[target_name]:
		if data["name"] == lib_name:
			# we find it in the List ==> need to check if it is present in the system :
			if data["loaded"] == False:
				debug.verbose("add to path: '" + os.path.dirname(data["path"]) + "'")
				sys.path.append(os.path.dirname(data["path"]))
				debug.verbose("import system : '" + data["name"] + "'")
				theSystem = __import__(env.get_build_system_base_name() + __start_system_name + target_name + "_" + data["name"])
				#create the system module
				try:
					debug.verbose("SYSTEM: request: " + data["name"])
					data["system"] = theSystem.System(target)
					data["exist"] = data["system"].valid
				except:
					debug.warning("Not find: '" + data["name"] + "' ==> get exception")
			return data["exist"]
	return False

def load(target, lib_name, target_name):
	global system_list
	if target_name not in system_list:
		debug.error("you must call this function after checking of the system exist() !1!")
	for data in system_list[target_name]:
		if data["name"] == lib_name:
			if data["exist"] == False:
				debug.error("you must call this function after checking of the system exist() !2!")
			if data["module"] == None:
				# create a module from the system interface...
				data["module"] = create_module_from_system(target, data)
				data["loaded"] = True
			target.add_module(data["module"])
			return

