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
## Dynamic library builder
##
from lutin import multiprocess
from lutin import tools
from lutin import debug
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
## @brief Get builder input file type
## @return List of extention supported
##
def get_input_type():
	return ["class"]

##
## @brief Get builder output file type
## @return List of extention supported
##
def get_output_type():
	return ["jar"]

##
## @brief Get builder support multi-threading or not
## @return True Multithreading supported
## @return False Multithreading NOT supported
##
def get_support_multithreading():
	return False

##
## @brief Commands for running gcc to link a shared library.
##
def link(file, binary, target, depancy, flags, name, basic_path):
	file_src = file
	file_dst = os.path.join(target.get_build_path(name), name + ".jar")
	file_depend = file_dst + target.suffix_dependence
	file_cmd = file_dst + target.suffix_cmd_line
	file_warning = file_dst + target.suffix_warning
	
	#create command Line
	cmd = [
		target.jar,
		"cf", file_dst,
		]
	for file in file_src:
		path = ""
		for elem in ["org/", "com/"]:
			pos = file.find(elem);
			if pos > 0:
				path = file[:pos]
				file = file[pos:]
		cmd.append("-C")
		cmd.append(path)
		cmd.append(file)
	cmdLine=tools.list_to_str(cmd)
	"""
	# check the dependency for this file :
	if depend.need_re_package(file_dst, file_src, True, file_cmd, cmdLine) == False:
		return tmpList[1]
	"""
	tools.create_directory_of_file(file_dst)
	debug.print_element("jar", name, "==>", file_dst)
	multiprocess.run_command(cmdLine, store_output_file=file_warning)
	# write cmd line only after to prevent errors ...
	tools.store_command(cmdLine, file_cmd)
	#debug.print_element("SharedLib", self.name, "==>", tmpList[1])
	return file_dst



