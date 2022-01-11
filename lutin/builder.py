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
	gld_base = env.get_gld_build_system_base_name()
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
		if filename[:len(gld_base)] == gld_base:
			filename = filename[len(gld_base):]
			# Check if it start with the local patern:
			if filename[:len(__start_builder_name)] != __start_builder_name:
				debug.extreme_verbose("BUILDER:     NOT-Integrate: '" + filename + "' from '" + elem + "' ==> rejected")
				continue
			continue
		elif filename[:len(global_base)] == global_base:
			filename = filename[len(global_base):]
			# Check if it start with the local patern:
			if filename[:len(__start_builder_name)] != __start_builder_name:
				debug.extreme_verbose("BUILDER:     NOT-Integrate: '" + filename + "' from '" + elem + "' ==> rejected")
				continue
			# Remove local patern
			builder_name = filename[len(__start_builder_name):]
			debug.verbose("BUILDER:     Integrate: '" + builder_name + "' from '" + elem + "'")
			the_builder = __import__(base_file_name)
			builder_list.append({"name":builder_name,
			                     "order":the_builder.get_order(),
			                     "element":the_builder
			                    })
			debug.debug('BUILDER:     type=' + the_builder.get_type() + " order=" + str(the_builder.get_order()) + " in=" + str(the_builder.get_input_type()) + " out=" + str(the_builder.get_output_type()))
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
## @brief Get a builder tool with specifying the input type (like cpp, S ...)
## @param[in] input_type (string) extension file that can be compile
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
## @brief Get a builder tool with his name
## @param[in] name (string) name of the builder
##
def get_builder_named(name):
	global builder_list
	for element in builder_list:
		if element["name"] == name:
			return element["element"]
	# we can not find the builder ...
	debug.error("Can not find builder for type : '" + str(input_type) + "'")
	raise ValueError('type error :' + str(input_type))

##
## @brief get all the builder with extension to detect automaticly mode to compile
## @return a map with the key name of the builder, and a table of extension files
##
def get_full_builder_extention():
	global builder_list
	out = {};
	for element in builder_list:
		if element["element"] != None:
			out[element["name"]] = element["element"].get_input_type();
	return out;

##
## @brief get all the builder in the common order build
## @return a list with the ordered builder names
##
def get_ordered_builder_list():
	global builder_list
	table = {};
	for element in builder_list:
		table[element["order"]] = element["name"];
	out = []
	for key in sorted(table.keys()):
		out.append(table[key]);
	debug.extreme_verbose("builder ordered=" + str(table));
	debug.extreme_verbose("    ==> " + str(out));
	return out;

def find_builder_with_input_extention(extension):
	extention_map = get_full_builder_extention();
	for builder_name in get_ordered_builder_list():
		debug.extreme_verbose("builder_name: " + str(extension) + " in " + str(extention_map[builder_name]));
		if extension in extention_map[builder_name]:
			return builder_name;
	debug.warning("does not find the builder: for extension: " + str(extension))
	return "?";

##
## @brief Get a builder tool with specifying the output type (like .exe, .jar ...)
## @param[in] input_type (string) extension file that can be generated
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
