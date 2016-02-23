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
	return ["o", "a"]

##
## @brief Get builder output file type
## @return List of extention supported
##
def get_output_type():
	return ["so", "dynlib", "dll"]

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
def link(file, binary, target, depancy, flags, name, basic_path, static=False):
	file_src, file_dst, file_depend, file_cmd, file_warning = target.generate_file(binary, name, basic_path, file, "lib-shared")
	list_static = []
	list_dynamic = []
	if static == True:
		#get all parent static libs
		list_static = depancy.src['static']
		# get only parent shared that is not static
		for elem in depancy.src['dynamic']:
			lib_name = elem[:-len(target.suffix_lib_dynamic)] + target.suffix_lib_static
			if lib_name not in depancy.src['static']:
				list_dynamic.append(elem)
	else:
		#get all parent dynamic libs
		list_dynamic = depancy.src['dynamic']
		# get only parent shared that is not static
		for elem in depancy.src['static']:
			lib_name = elem[:-len(target.suffix_lib_static)] + target.suffix_lib_dynamic
			if lib_name not in depancy.src['dynamic']:
				list_static.append(elem)
	#create command Line
	cmd = []
	# a specific case to not depend on the libstdc++ automaticly added by the G++ or clang++ compilator ==> then need to compile with GCC or CLANG if use libcxx from llvm or other ...
	if     "need-libstdc++" in depancy.flags \
	   and depancy.flags["need-libstdc++"] == True:
		cmd.append(target.xx)
	else:
		cmd.append(target.cc)
	
	cmd.append(["-o", file_dst])
	try:
		cmd.append(target.global_sysroot)
	except:
		pass
	try:
		cmd.append(target.arch)
	except:
		pass
	cmd.append("-shared")
	try:
		cmd.append(file_src)
	except:
		pass
	for view in ["local", "export"]:
		if view not in flags:
			continue
		for type in ["link", "link-dynamic"]:
			if type in flags[view]:
				cmd.append(flags[view][type])
	for type in ["link", "link-dynamic"]:
		if type in depancy.flags:
			cmd.append(depancy.flags[type])
	for type in ["link", "link-dynamic"]:
		if type in target.global_flags:
			cmd.append(target.global_flags[type])
	if 'src' in depancy.src:
		cmd.append(tools.filter_extention(depancy.src['src'], get_input_type()))
	try:
		cmd.append(list_static)
	except:
		pass
	try:
		for elem in list_dynamic:
			lib_path = os.path.dirname(elem)
			lib_name = elem[len(lib_path)+len(target.prefix_lib)+1:-len(target.suffix_lib_dynamic)]
			cmd.append("-L" + lib_path)
			cmd.append("-l" + lib_name)
		if     target.name != "MacOs" \
		   and target.name != "Android":
			if len(list_dynamic) > 0:
				cmd.append("-Wl,-R$ORIGIN/../lib/")
	except:
		pass
	for view in ["local", "export"]:
		if view not in flags:
			continue
		for type in ["link-lib"]:
			if type in flags[view]:
				cmd.append([("-l" + sss).replace("-l/", "/") for sss in flags[view][type] ])
	for type in ["link-lib"]:
		if type in depancy.flags:
			cmd.append([("-l" + sss).replace("-l/", "/") for sss in depancy.flags[type] ])
	for type in ["link-lib"]:
		if type in target.global_flags:
			cmd.append([("-l" + sss).replace("-l/", "/") for sss in target.global_flags[type] ])
	cmdLine=tools.list_to_str(cmd)
	# check the dependency for this file :
	if     depend.need_re_package(file_dst, file_src, True, file_cmd, cmdLine) == False \
	   and depend.need_re_package(file_dst, depancy.src, False, file_cmd, cmdLine) == False:
		return file_dst
	tools.create_directory_of_file(file_dst)
	debug.print_element("SharedLib", name, "==>", os.path.relpath(file_dst))
	multiprocess.run_command(cmdLine, store_output_file=file_warning)
	# strip the output file:
	if    target.config["mode"] == "release" \
	   or env.get_force_strip_mode() == True:
		# get the file size of the non strip file
		originSize = tools.file_size(file_dst);
		debug.print_element("SharedLib(strip)", name, "", "")
		if target.name == "MacOs":
			cmdLineStrip=tools.list_to_str([
				target.strip,
				"-u",
				file_dst])
		else:
			cmdLineStrip=tools.list_to_str([
				target.strip,
				file_dst])
		multiprocess.run_command(cmdLineStrip, store_output_file=file_warning)
		# get the stip size of the binary
		stripSize = tools.file_size(file_dst)
		debug.debug("file reduce size : " + str(originSize/1024) + "ko ==> " + str(stripSize/1024) + "ko")
	# write cmd line only after to prevent errors ...
	tools.store_command(cmdLine, file_cmd)
	#debug.print_element("SharedLib", self.name, "==>", tmpList[1])
	return file_dst
