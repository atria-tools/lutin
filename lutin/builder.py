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
from . import debug
from . import heritage
from . import env

##
## constitution of dictionnary:
##     - "type": "compiler", "linker"
##     - "in": input type file
##     - "out": extention of the files
##     - "builder": pointer on the element
##
builder_list=[]
__start_builder_name="Builder_"

##
## @brief Import all File that start with env.get_build_system_base_name() + __start_builder_name + XXX and register in the list of Builder
## @param[in] path_list ([string,...]) List of file that start with env.get_build_system_base_name() in the running worktree (Parse one time ==> faster)
##
def import_path(path_list):
	global builder_list
	global_base = env.get_build_system_base_name()
	debug.debug("BUILDER: Init with Files list:")
	for elem in path_list:
		sys.path.append(os.path.dirname(elem))
		# Get file name:
		filename = os.path.basename(elem)
		# Remove .py at the end:
		filename = filename[:-3]
		base_file_name = filename
		# Remove global base name:
		filename = filename[len(global_base):]
		# Check if it start with the local patern:
		if filename[:len(__start_builder_name)] != __start_builder_name:
			debug.extreme_verbose("BUILDER:     Integrate: '" + filename + "' from '" + elem + "' ==> rejected")
			continue
		# Remove local patern
		builder_name = filename[len(__start_builder_name):]
		debug.verbose("BUILDER:     Integrate: '" + builder_name + "' from '" + elem + "'")
		the_builder = __import__(base_file_name)
		builder_list.append({"name":builder_name,
		                     "element":the_builder
		                    })
		debug.debug('BUILDER:     type=' + the_builder.get_type() + " in=" + str(the_builder.get_input_type()) + " out=" + str(the_builder.get_output_type()))
	debug.verbose("List of BUILDER: ")
	for elem in builder_list:
		debug.verbose("    " + str(elem["name"]))


##
## @brief All builder are common (no target or comilator dependency). We need to load all of them when start lutin
##
def init():
	global builder_list
	debug.debug('BUILDER: Initialize all ...')
	for element in builder_list:
		if element["element"] != None:
			element["element"].init()

##
## @brief Get a builder tool with specifiying the input type (like cpp, S ...)
## @param[in] input_type (string) extention file that can be compile
##
def get_builder(input_type):
	global builder_list
	for element in builder_list:
		if element["element"] != None:
			if input_type in element["element"].get_input_type():
				return element["element"]
	# we can not find the builder ...
	debug.error("Can not find builder for type : '" + str(input_type) + "'")
	raise ValueError('type error :' + str(input_type))

##
## @brief Get a builder tool with specifiying the output type (like .exe, .jar ...)
## @param[in] input_type (string) extention file that can be generated
##
def get_builder_with_output(output_type):
	global builder_list
	for element in builder_list:
		if element["element"] != None:
			if output_type in element["element"].get_output_type():
				return element["element"]
	# we can not find the builder ...
	debug.error("Can not find builder for type : '" + str(output_type) + "'")
	raise ValueError('type error :' + str(output_type))
