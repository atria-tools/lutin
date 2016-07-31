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
## C builder
##
from lutin import multiprocess
from lutin import tools
from lutin import debug
from lutin import depend

# C version:
default_version = 1989
default_version_gnu = False

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
	return ["c", "C"]

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
		cmd.append(get_version_compilation_flags(flags, depancy.flags))
	except:
		pass
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
	comment = ["c", name, "<==", file]
	# process element
	multiprocess.run_in_pool(cmdLine, comment, file_cmd, store_output_file=file_warning)
	return {"action":"add", "file":file_dst}


def get_version_compilation_flags(flags, dependency_flags):
	try:
		version_local = flags["local"]["c-version"]["version"]
	except:
		version_local = default_version
	try:
		dependency_version = dependency_flags["c-version"]
	except:
		dependency_version = default_version
	try:
		is_gnu = flags["local"]["c-version"]["gnu"]
	except:
		is_gnu = default_version_gnu
	
	version = max(version_local, dependency_version)
	if version == 2011:
		if is_gnu ==True:
			out = ["-std=gnu11", "-D__C_VERSION__=2011"]
		else:
			out = ["-std=c11", "-D__C_VERSION__=1989"]
	elif version == 1999:
		if is_gnu ==True:
			out = ["-std=gnu99", "-D__C_VERSION__=1999"]
		else:
			out = ["-std=c99", "-D__C_VERSION__=1989"]
	elif version == 1990:
		if is_gnu ==True:
			out = ["-std=gnu90", "-D__C_VERSION__=1990"]
		else:
			out = ["-std=c90", "-D__C_VERSION__=1989"]
	else:
		if is_gnu ==True:
			out = ["-std=gnu89", "-D__C_VERSION__=1989"]
		else:
			out = ["-std=c89", "-D__C_VERSION__=1989"]
	return out
