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
from . import tools
from . import env


__macro_list=[]
__start_macro_name="Macro_"

##
## @brief Import all File that start with env.get_build_system_base_name() + __start_macro_name + XXX and register in the list of Target
## @param[in] path_list ([string,...]) List of file that start with env.get_build_system_base_name() in the running worktree (Parse one time ==> faster)
##
def import_path(path_list):
	global __macro_list
	global_base = env.get_build_system_base_name()
	debug.debug("TARGET: Init with Files list:")
	for elem in path_list:
		sys.path.append(os.path.dirname(elem))
		# Get file name:
		filename = os.path.basename(elem)
		# Remove .py at the end:
		filename = filename[:-3]
		# Remove global base name:
		filename = filename[len(global_base):]
		# Check if it start with the local patern:
		if filename[:len(__start_macro_name)] != __start_macro_name:
			debug.extreme_verbose("MACRO:     NOT-Integrate: '" + filename + "' from '" + elem + "' ==> rejected")
			continue
		# Remove local patern
		target_name = filename[len(__start_macro_name):]
		debug.verbose("MACRO:     Integrate: '" + target_name + "' from '" + elem + "'")
		__macro_list.append([target_name, elem])
	debug.verbose("New list MACRO: ")
	for elem in __macro_list:
		debug.verbose("    " + str(elem[0]))

##
## @brief Load a specific target
##
def load_macro(name):
	global __macro_list
	debug.debug("load macro: " + name)
	if len(__macro_list) == 0:
		debug.error("No macro to compile !!!")
	debug.debug("list macro: " + str(__macro_list))
	for mod in __macro_list:
		if mod[0] == name:
			debug.verbose("add to path: '" + os.path.dirname(mod[1]) + "'")
			sys.path.append(os.path.dirname(mod[1]))
			debug.verbose("import macro : '" + env.get_build_system_base_name() + __start_macro_name + name + "'")
			the_macro = __import__(env.get_build_system_base_name() + __start_macro_name + name)
			return the_macro
	raise KeyError("No entry for : " + name)

def list_all_macro():
	global __macro_list
	tmp_list_name = []
	for mod in __macro_list:
		tmp_list_name.append(mod[0])
	return tmp_list_name
