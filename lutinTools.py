#!/usr/bin/python
import os
import shutil
import errno
import lutinDebug as debug
import fnmatch
import lutinMultiprocess
import lutinDepend as dependency


"""
	
"""
def get_run_folder():
	return os.getcwd()

"""
	
"""
def get_current_path(file):
	return os.path.dirname(os.path.realpath(file))

def create_directory_of_file(file):
	folder = os.path.dirname(file)
	try:
		os.stat(folder)
	except:
		os.makedirs(folder)


def remove_folder_and_sub_folder(path):
	if os.path.isdir(path):
		debug.verbose("remove folder : '" + path + "'")
		shutil.rmtree(path)

def remove_file(path):
	if os.path.isfile(path):
		os.remove(path)

def file_size(path):
	if not os.path.isfile(path):
		return 0
	statinfo = os.stat(path)
	return statinfo.st_size

def file_read_data(path):
	if not os.path.isfile(path):
		return ""
	file = open(path, "r")
	data_file = file.read()
	file.close()
	return data_file

def file_write_data(path, data):
	file = open(path, "w")
	file.write(data)
	file.close()

def list_to_str(list):
	if type(list) == type(str()):
		return list + " "
	else:
		result = ""
		# mulyiple imput in the list ...
		for elem in list:
			result += list_to_str(elem)
		return result

def add_prefix(prefix,list):
	if type(list) == type(None):
		return ""
	if type(list) == type(str()):
		return prefix+list
	else:
		if len(list)==0:
			return ''
		else:
			result=[]
			for elem in list:
				result.append(prefix+elem)
			return result

def copy_file(src, dst, cmd_file=None, force=False):
	if os.path.exists(src) == False:
		debug.error("Request a copy a file that does not existed : '" + src + "'")
	cmd_line = "copy \"" + src + "\" \"" + dst + "\""
	if     force == False \
	   and dependency.need_re_build(dst, src, file_cmd=cmd_file , cmdLine=cmd_line) == False:
		return
	debug.print_element("copy file", src, "==>", dst)
	create_directory_of_file(dst)
	shutil.copyfile(src, dst)
	lutinMultiprocess.store_command(cmd_line, cmd_file)


def copy_anything(src, dst):
	tmpPath = os.path.dirname(os.path.realpath(src))
	tmpRule = os.path.basename(src)
	for root, dirnames, filenames in os.walk(tmpPath):
		tmpList = filenames
		if len(tmpRule)>0:
			tmpList = fnmatch.filter(filenames, tmpRule)
		# Import the module :
		for cycleFile in tmpList:
			#for cycleFile in filenames:
			#debug.info("Might copy : '" + tmpPath+cycleFile + "' ==> '" + dst + "'")
			copy_file(tmpPath+"/"+cycleFile,dst+"/"+cycleFile)


def copy_anything_target(target, src, dst):
	tmpPath = os.path.dirname(os.path.realpath(src))
	tmpRule = os.path.basename(src)
	for root, dirnames, filenames in os.walk(tmpPath):
		tmpList = filenames
		if len(tmpRule)>0:
			tmpList = fnmatch.filter(filenames, tmpRule)
		# Import the module :
		for cycleFile in tmpList:
			#for cycleFile in filenames:
			#debug.info("Might copy : '" + tmpPath+cycleFile + "' ==> '" + dst + "'")
			target.add_file_staging(tmpPath+"/"+cycleFile,dst+"/"+cycleFile)
