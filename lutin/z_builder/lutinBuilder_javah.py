##
## Java builder
##
from lutin import multiprocess
from lutin import tools
from lutin import debug
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
	return ["javah"]

##
## @brief Get builder output file type
## @return List of extention supported
##
def get_output_type():
	return ["h"]

##
## @brief Commands for running gcc to compile a C++ file in object file.
##
def compile(file, binary, target, depancy, flags, path, name, basic_folder):
	# file_src = target.get_full_name_source(basic_folder, file)
	file_cmd = target.get_full_name_cmd(name, basic_folder, file)
	# file_dst = target.get_full_name_destination(name, basic_folder, file, get_output_type())
	file_depend = target.get_full_dependency(name, basic_folder, file)
	
	
	# create the command line befor requesting start:
	cmd = [
		target.javah,
		"-d", target.get_build_folder(name) + target.folder_generate_code
		]
	
	if debug.get_level() >= 5:
		cmd.append("-verbose")
	
	cmd.append("-classpath")
	cmd.append(target.get_build_folder(name))
	class_to_build = file[:-6]
	cmd.append(class_to_build)
	# Create cmd line
	cmdLine=tools.list_to_str(cmd)
	
	file_dst = target.get_build_folder(name) + "/tmp_header/" + class_to_build.replace(".", "_") + ".h"
	# check the dependency for this file :
	#if depend.need_re_build(file_dst, file_src, file_depend, file_cmd, cmdLine) == False:
	#	return file_dst
	#tools.create_directory_of_file(file_dst)
	comment = ["javah", class_to_build.replace(".", "_") + ".h", "<==", class_to_build]
	#process element
	multiprocess.run_in_pool(cmdLine, comment, file_cmd)
	debug.verbose("file= " + file_dst)
	#return file_dst
	return {"action":"path", "path":target.get_build_folder(name) + target.folder_generate_code}

