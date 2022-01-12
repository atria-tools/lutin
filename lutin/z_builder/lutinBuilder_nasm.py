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
## C++ builder
##
from lutin import multiprocess
from lutin import tools
from realog import debug
from lutin import depend
from lutin import env

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
	return "compiler"

##
## @brief Get builder input file type
## @return List of extention supported
##
def get_input_type():
	return [];#["s"]

##
## @brief get the order of the current builder
## @return the string that define the build order
##
def get_order():
	return 200

##
## @brief Get builder output file type
## @return List of extention supported
##
def get_output_type():
	return ["o"]

##
## @brief Get builder support multi-threading or not
## @return True Multithreading supported
## @return False Multithreading NOT supported
##
def get_support_multithreading():
	return True


##
## @brief Commands for running gcc to compile a C++ file in object file.
##
def compile(file, binary, target, depancy, flags, path, name, basic_path, module_src):
	file_src = target.get_full_name_source(basic_path, file)
	file_cmd = target.get_full_name_cmd(name, basic_path, file)
	file_dst = target.get_full_name_destination(name, basic_path, file, get_output_type())
	file_depend = target.get_full_dependency(name, basic_path, file)
	file_warning = target.get_full_name_warning(name, basic_path, file)
	# set ccache interface:
	compilator_ccache = ""
	if env.get_ccache() == True:
		compilator_ccache = "ccache"
	# create the command line before requesting start:
	cmd = [
		compilator_ccache,
		"nasm",
		"-o", file_dst,
		"-f", "elf64",
		target.sysroot
		]
	for view in ["export", "local"]:
		for type in ["nasm"]:
			try:
				cmd.append(tools.add_prefix("-I",path[view][type]))
			except:
				pass
	for type in ["nasm"]:
		try:
			cmd.append(tools.add_prefix("-I",depancy.path[type]))
		except:
			pass
	cmd.append(target.global_include_cc)
	list_flags = [];
	if "nasm" in target.global_flags:
		list_flags.append(target.global_flags["nasm"])
	for view in ["local", "export"]:
		if view in flags:
			for type in ["nasm"]:
				if type in flags[view]:
					list_flags.append(flags[view][type])
	# get blacklist of flags
	list_flags_blacklist = [];
	if "nasm-remove" in target.global_flags:
		list_flags_blacklist.append(target.global_flags["nasm-remove"])
	for type in ["nasm-remove"]:
		if type in depancy.flags:
			list_flags_blacklist.append(depancy.flags[type])
	for view in ["local", "export"]:
		if view in flags:
			for type in ["c-nasm"]:
				if type in flags[view]:
					list_flags_blacklist.append(flags[view][type])
	# apply blacklisting of data and add it on the cmdLine
	clean_flags = tools.remove_element(list_flags, list_flags_blacklist)
	#debug.warning("plop " + str(list_flags_blacklist) + "       " + str(list_flags) + "  --> " + str(clean_flags) )
	cmd.append(clean_flags);
	cmd.append(["-DPIC"])
	cmd.append(["-MP"])
	cmd.append(file_src)
	# Create cmd line
	cmdLine = tools.list_to_str(cmd)
	# check the dependency for this file :
	if depend.need_re_build(file_dst, file_src, file_depend, file_cmd, cmdLine) == False:
		return {"action":"add", "file":file_dst}
	tools.create_directory_of_file(file_dst)
	comment = ["nasm", name, "<==", file]
	#process element
	multiprocess.run_in_pool(cmdLine, comment, file_cmd, store_output_file=file_warning)
	return {"action":"add", "file":file_dst}


