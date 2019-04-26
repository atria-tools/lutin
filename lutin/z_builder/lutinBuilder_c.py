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
## C builder
##
from lutin import multiprocess
from lutin import tools
from realog import debug
from lutin import depend
from lutin import env

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
	
	# set ccache interface:
	compilator_ccache = ""
	if env.get_ccache() == True:
		compilator_ccache = "ccache"
	# create the command line befor requesting start:
	cmd = [
		compilator_ccache,
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
	list_flags = [];
	if "c" in target.global_flags:
		list_flags.append(target.global_flags["c"])
	if "c" in depancy.flags:
		list_flags.append(depancy.flags["c"])
	for view in ["local", "export"]:
		if view in flags:
			if "c" in flags[view]:
				list_flags.append(flags[view]["c"])
	# get blacklist of flags
	list_flags_blacklist = [];
	if "c-remove" in target.global_flags:
		list_flags_blacklist.append(target.global_flags["c-remove"])
	if "c-remove" in depancy.flags:
		list_flags_blacklist.append(depancy.flags["c-remove"])
	for view in ["local", "export"]:
		if view in flags:
			if "c-remove" in flags[view]:
				list_flags_blacklist.append(flags[view]["c-remove"])
	# apply blacklisting of data and add it on the cmdLine
	clean_flags = tools.remove_element(list_flags, list_flags_blacklist)
	#debug.warning("plop " + str(list_flags_blacklist) + "       " + str(list_flags) + "  --> " + str(clean_flags) )
	cmd.append(clean_flags);
	
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
	if version == 2018:
		if is_gnu ==True:
			out = ["-std=gnu18", "-D__C_VERSION__=2018"]
		else:
			out = ["-std=c18", "-D__C_VERSION__=2018"]
	elif version == 2017:
		if is_gnu ==True:
			out = ["-std=gnu17", "-D__C_VERSION__=2017"]
		else:
			out = ["-std=c17", "-D__C_VERSION__=2017"]
	elif version == 2011:
		if is_gnu ==True:
			out = ["-std=gnu11", "-D__C_VERSION__=2011"]
		else:
			out = ["-std=c11", "-D__C_VERSION__=2011"]
	elif version == 1999:
		if is_gnu ==True:
			out = ["-std=gnu99", "-D__C_VERSION__=1999"]
		else:
			out = ["-std=c99", "-D__C_VERSION__=1999"]
	elif version == 1990:
		if is_gnu ==True:
			out = ["-std=gnu90", "-D__C_VERSION__=1990"]
		else:
			out = ["-std=c90", "-D__C_VERSION__=1990"]
	else:
		if is_gnu ==True:
			out = ["-std=gnu89", "-D__C_VERSION__=1989"]
		else:
			out = ["-std=c89", "-D__C_VERSION__=1989"]
	return out
