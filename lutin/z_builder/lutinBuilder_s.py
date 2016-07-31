#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##

##
## ASM builder
##
from lutin import multiprocess
from lutin import tools
from lutin import depend

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
	return ["s", "S"]

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
## @brief Commands for running gcc to compile a C file in object file.
##
def compile(file, binary, target, depancy, flags, path, name, basic_path, module_src):
	file_src = target.get_full_name_source(basic_path, file)
	file_cmd = target.get_full_name_cmd(name, basic_path, file)
	file_dst = target.get_full_name_destination(name, basic_path, file, get_output_type())
	file_depend = target.get_full_dependency(name, basic_path, file)
	file_warning = target.get_full_name_warning(name, basic_path, file)
	
	# create the command line befor requesting start:
	cmd = [
		target.cc,
		"-o", file_dst,
		target.arch,
		target.sysroot]
	for view in ["export", "local"]:
		try:
			cmd.append(tools.add_prefix("-I", path[view]["c"]))
		except:
			pass
	try:
		cmd.append(tools.add_prefix("-I", depancy.path["c"]))
	except:
		pass
	cmd.append(target.global_include_cc)
	try:
		cmd.append(target.global_flags["c"])
	except:
		pass
	try:
		cmd.append(depancy.flags["c"])
	except:
		pass
	for view in ["local", "export"]:
		try:
			cmd.append(flags[view]["c"])
		except:
			pass
	cmd.append("-c")
	cmd.append("-MMD")
	cmd.append("-MP")
	cmd.append(file_src)
	# Create cmd line
	cmdLine=tools.list_to_str(cmd)
	# check the dependency for this file :
	if depend.need_re_build(file_dst, file_src, file_depend, file_cmd, cmdLine) == False:
		return {"action":"add", "file":file_dst}
	tools.create_directory_of_file(file_dst)
	comment = ["s", name, "<==", file]
	# process element
	multiprocess.run_in_pool(cmdLine, comment, file_cmd, store_output_file=file_warning)
	return {"action":"add", "file":file_dst}
