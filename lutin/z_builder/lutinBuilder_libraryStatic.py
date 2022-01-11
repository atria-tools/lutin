#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license MPL v2.0 (see license file)
##

##
## Static library builder
##
from lutin import multiprocess
from lutin import tools
from realog import debug
from lutin import depend
from lutin import env
import os

##
## Initialize the builder, if needed ... to get dependency between builder (for example)
##
def init():
	pass

##
## Get the current builder type.
## Return the type of builder
##
def get_type():
	return "linker"

##
## @brief get the order of the current builder
## @return the string that define the build order
##
def get_order():
	return 1000

##
## @brief Get builder input file type
## @return List of extention supported
##
def get_input_type():
	return ["o", "a"]

##
## @brief Get builder output file type
## @return List of extention supported
##
def get_output_type():
	return ["a"]

##
## @brief Get builder support multi-threading or not
## @return True Multithreading supported
## @return False Multithreading NOT supported
##
def get_support_multithreading():
	return False

##
## @brief Commands for running ar.
##
def link(file, binary, target, depancy, flags, name, basic_path):
	file_src = file
	file_dst = target.get_build_file_static(name)
	file_depend = file_dst + target.suffix_dependence
	file_cmd = file_dst + target.suffix_cmd_line
	file_warning = file_dst + target.suffix_warning
	
	debug.extreme_verbose("file_dst     = " + file_dst)
	debug.extreme_verbose("file_depend  = " + file_depend)
	debug.extreme_verbose("file_cmd     = " + file_cmd)
	debug.extreme_verbose("file_warning = " + file_warning)
	
	# set ccache interface:
	compilator_ccache = ""
	if env.get_ccache() == True:
		compilator_ccache = "ccache"
	cmd = [
		compilator_ccache,
		target.ar
		]
	try:
		cmd.append(target.global_flags["ar"])
	except:
		pass
	try:
		cmd.append(flags["local"]["link"])
	except:
		pass
	try:
		cmd.append(file_dst)
	except:
		pass
	try:
		cmd.append(file_src)
	except:
		pass
	cmdLine=tools.list_to_str(cmd)
	# check the dependency for this file :
	if     depend.need_re_package(file_dst, file_src, True, file_cmd, cmdLine) == False \
	   and depend.need_re_package(file_dst, depancy.src, False, file_cmd, cmdLine) == False:
		return file_dst
	
	tools.create_directory_of_file(file_dst)
	debug.print_element("StaticLib", name, "==>", os.path.relpath(file_dst))
	# explicitly remove the destination to prevent error ...
	if os.path.exists(file_dst) and os.path.isfile(file_dst):
		os.remove(file_dst)
	multiprocess.run_command(cmdLine, store_output_file=file_warning)
	#$(Q)$(TARGET_RANLIB) $@
	if target.ranlib != "":
		cmdLineRanLib=tools.list_to_str([
			target.ranlib,
			file_dst ])
		multiprocess.run_command(cmdLineRanLib, store_output_file=file_warning)
	# write cmd line only after to prevent errors ...
	tools.store_command(cmdLine, file_cmd)
	return file_dst
