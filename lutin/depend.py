#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license MPL v2.0 (see license file)
##
import os
# Local import
from . import debug
from . import env

def _create_directory_of_file(file):
	path = os.path.dirname(file)
	try:
		os.stat(path)
	except:
		os.makedirs(path)

def _file_write_data(path, data):
	file = open(path, "w")
	file.write(data)
	file.close()

def _file_size(path):
	if not os.path.isfile(path):
		return 0
	statinfo = os.stat(path)
	return statinfo.st_size

def _file_read_data(path, binary=False):
	if not os.path.isfile(path):
		return ""
	if binary == True:
		file = open(path, "rb")
	else:
		file = open(path, "r")
	data_file = file.read()
	file.close()
	return data_file

##
## @brief Creata a dependency file with a list of files
## @param[in] depend_file (string) filename to store a dependency data
## @param[in] list_files ([string,...]) List of file that depend the current element
##
def create_dependency_file(depend_file, list_files):
	data = ""
	for elem in list_files:
		data += elem + "\n"
	_create_directory_of_file(depend_file)
	_file_write_data(depend_file, data)

# Buffer with the whole list of file check access ==> time cache of file
_list_of_file_time = {}

def clear_cache_file_date():
	global _list_of_file_time
	_list_of_file_time = {}

def file_get_time(file_name):
	global _list_of_file_time
	if file_name in _list_of_file_time:
		return _list_of_file_time[file_name]
	local_time = os.path.getmtime(file_name)
	_list_of_file_time[file_name] = local_time
	return local_time

def file_exist(file_name):
	global _list_of_file_time
	if file_name in _list_of_file_time:
		return True
	if os.path.exists(file_name) == False:
		return False
	# we update the date ==> permit to not do an other acces on file
	local_time = os.path.getmtime(file_name)
	_list_of_file_time[file_name] = local_time
	return True

##
## @brief Check if all dependency of a file and dependency file is correct or not
## @param[in] dst (string) File that will be generated
## @param[in] src (string) Source File needed to generate the 'dst'
## @param[in] depend_file (string) Dependency file that contain all file that the src depending
## @param[in] file_cmd (string) Filename of where is store the cmdline to generate the 'dst'
## @param[in] cmd_line (string) Command line that will be use to generate the 'dst'
## @param[in] force_identical (string) for copy file this check if the src and dst are identical
## @return (bool) True: something change ==> need to rebuild, False otherwise
##
def need_re_build(dst, src, depend_file=None, file_cmd="", cmd_line="", force_identical=False):
	debug.extreme_verbose("Request check of dependency of :")
	debug.extreme_verbose("		dst='" + str(dst) + "'")
	debug.extreme_verbose("		src='" + str(src) + "'")
	debug.extreme_verbose("		dept='" + str(depend_file) + "'")
	debug.extreme_verbose("		cmd='" + str(file_cmd) + "'")
	debug.extreme_verbose("		force_identical='" + str(force_identical) + "'")
	# if force mode selected ==> just force rebuild ...
	if env.get_force_mode():
		debug.extreme_verbose("			==> must rebuild (force mode)")
		return True
	
	# check if the destination existed:
	if     dst != "" \
	   and dst != None \
	   and file_exist(dst) == False:
		debug.extreme_verbose("			==> must rebuild (dst does not exist)")
		return True
	if     src != "" \
	   and src != None \
	   and file_exist(src) == False:
		debug.warning("			==> unexistant file :'" + src + "'")
		return True
	# Check the basic date if the 2 files
	if     dst != "" \
	   and dst != None \
	   and src != "" \
	   and src != None \
	   and file_get_time(src) > file_get_time(dst):
		debug.extreme_verbose("			==> must rebuild (source time greater)")
		return True
	
	if     depend_file != "" \
	   and depend_file != None \
	   and file_exist(depend_file) == False:
		debug.extreme_verbose("			==> must rebuild (no depending file)")
		return True
	
	if     file_cmd != "" \
	   and file_cmd != None:
		if file_exist(file_cmd) == False:
			debug.extreme_verbose("			==> must rebuild (no commandLine file)")
			return True
		# check if the 2 cmd_line are similar :
		file2 = open(file_cmd, "r")
		first_and_unique_line = file2.read()
		if first_and_unique_line != cmd_line:
			debug.extreme_verbose("			==> must rebuild (cmd_lines are not identical)")
			debug.extreme_verbose("				==> '" + cmd_line + "'")
			debug.extreme_verbose("				==> '" + first_and_unique_line + "'")
			file2.close()
			return True
		# the cmdfile is correct ...
		file2.close()
	
	if     depend_file != "" \
	   and depend_file != None:
		debug.extreme_verbose("			start parsing dependency file : '" + depend_file + "'")
		file = open(depend_file, "r")
		for cur_line in file.readlines():
			# normal file : end with : ": \\n"
			cur_line = cur_line[:len(cur_line)-1]
			# removing last \ ...
			if cur_line[len(cur_line)-1:] == '\\' :
				cur_line = cur_line[:len(cur_line)-1]
			# remove white space : 
			#debug.verbose("				Line (read) : '" + cur_line + "'");
			cur_line = cur_line.strip()
			#debug.verbose("				Line (strip) : '" + cur_line + "'");
			
			test_file=""
			if cur_line[len(cur_line)-1:] == ':':
				debug.extreme_verbose("				Line (no check (already done) : '" + cur_line + "'");
			elif    len(cur_line) == 0 \
			     or cur_line == '\\':
				debug.extreme_verbose("				Line (Not parsed) : '" + cur_line + "'");
			else:
				test_file = cur_line
				debug.extreme_verbose("				Line (might check) : '" + test_file + "'");
			# really check files:
			if test_file != "":
				debug.extreme_verbose("					==> test");
				if file_exist(test_file) == False:
					debug.extreme_verbose("			==> must rebuild (a dependency file does not exist)")
					file.close()
					return True
				if file_get_time(test_file) > file_get_time(dst):
					debug.extreme_verbose("			==> must rebuild (a dependency file time is newer)")
					file.close()
					return True
		# close the current file :
		file.close()
	# check the 2 files are identical:
	if force_identical == True:
		# check if the 2 cmd_line are similar:
		size_src = _file_size(src)
		size_dst = _file_size(dst)
		if size_src != size_dst:
			debug.extreme_verbose("			Force Rewrite not the same size     size_src=" + str(size_src) + " != size_dest=" + str(size_dst))
			return True
		data_src = _file_read_data(src, binary=True)
		data_dst = _file_read_data(dst, binary=True)
		if data_src != data_dst:
			debug.extreme_verbose("			Force Rewrite not the same data")
			return True
	
	debug.extreme_verbose("			==> Not rebuild (all dependency is OK)")
	return False

##
## @brief 
## @param[in] dst (string) File that will be generated
## @param[in] src_list ([string,...]) Source file list needed to generate the 'dst'
## @param[in] must_have_src (bool) All sources must be present
## @param[in] file_cmd (string) Filename of where is store the cmdline to generate the 'dst'
## @param[in] cmd_line (string) Command line that will be use to generate the 'dst'
## @return (bool) True: Need to regenerate the package, False otherwise
##
def need_re_package(dst, src_list, must_have_src, file_cmd="", cmd_line=""):
	debug.extreme_verbose("Request check of dependency of :")
	debug.extreme_verbose("		dst='" + str(dst) + "'")
	compleate_list = []
	debug.extreme_verbose("		src:")
	if type(src_list) == str:
		compleate_list.append(src_list)
		debug.extreme_verbose("			'" + src_list + "'")
	elif type(src_list) == list:
		for src in src_list:
			compleate_list.append(src)
			debug.extreme_verbose("			'" + str(src) + "'")
	elif type(src_list) == dict:
		for key in src_list:
			debug.extreme_verbose("			'" + str(key) + "'")
			for src in src_list[key]:
				compleate_list.append(src)
				debug.extreme_verbose("				'" + str(src) + "'")
	
	if     must_have_src == False \
	   and len(compleate_list) == 0:
		return False
	
	# if force mode selected ==> just force rebuild ...
	if env.get_force_mode():
		debug.extreme_verbose("			==> must re-package (force mode)")
		return True
	
	# check if the destination existed:
	if file_exist(dst) == False:
		debug.extreme_verbose("			==> must re-package (dst does not exist)")
		return True
	# chek the basic date if the 2 files
	if len(compleate_list) == 0:
		debug.extreme_verbose("			==> must re-package (no source ???)")
		return True
	for src in compleate_list:
		if file_get_time(src) > file_get_time(dst):
			debug.extreme_verbose("			==> must re-package (source time greater) : '" + src + "'")
			return True
	
	if ""!=file_cmd:
		if False==file_exist(file_cmd):
			debug.extreme_verbose("			==> must rebuild (no commandLine file)")
			return True
		# check if the 2 cmd_line are similar :
		file2 = open(file_cmd, "r")
		first_and_unique_line = file2.read()
		if first_and_unique_line != cmd_line:
			debug.extreme_verbose("			==> must rebuild (cmd_lines are not identical)")
			debug.extreme_verbose("				==> '" + cmd_line + "'")
			debug.extreme_verbose("				==> '" + first_and_unique_line + "'")
			file2.close()
			return True
		# the cmdfile is correct ...
		file2.close()
	
	debug.extreme_verbose("			==> Not re-package (all dependency is OK)")
	return False



