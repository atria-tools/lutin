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

def create_dependency_files(target, src, heritage_src, basic_path):
	depend = []
	for elem in src:
		extention = elem.split('.')[-1]
		if    extention == 'jar' \
		   or extention == 'java':
			debug.extreme_verbose("add java depedence ... " + elem)
			depend.append(target.get_full_name_source(basic_path, elem))
	
	for elem in heritage_src:
		extention = elem.split('.')[-1]
		if    extention == 'jar' \
		   or extention == 'java':
			debug.extreme_verbose("add java depedence ... " + elem)
			depend.append(elem)
	return depend

##
## @brief Commands for running gcc to compile a C++ file in object file.
##
def compile(file, binary, target, depancy, flags, path, name, basic_path, module_src):
	# file_src = target.get_full_name_source(basic_path, file)
	file_cmd = target.get_full_name_cmd(name, basic_path, file)
	# file_dst = target.get_full_name_destination(name, basic_path, file, get_output_type())
	file_depend = target.get_full_dependency(name, basic_path, file)
	file_warning = target.get_full_name_warning(name, basic_path, file)
	depend_files = create_dependency_files(target, module_src, depancy.src['src'], basic_path)
	# create the command line befor requesting start:
	cmd = [
		target.javah,
		"-d", target.get_build_path(name) + target.path_generate_code
		]
	
	if debug.get_level() >= 5:
		cmd.append("-verbose")
	
	cmd.append("-classpath")
	cmd.append(target.get_build_path_object(name))
	class_to_build = file[:-6]
	cmd.append(class_to_build)
	# Create cmd line
	cmd_line = tools.list_to_str(cmd)
	
	file_dst = target.get_build_path(name) + "/generate_header/" + class_to_build.replace(".", "_") + ".h"
	# check the dependency for this file :
	if depend.need_re_build(file_dst, None, file_depend, file_cmd, cmd_line) == False:
		return {"action":"path", "path":target.get_build_path(name) + target.path_generate_code}
	#tools.create_directory_of_file(file_dst)
	comment = ["javah", class_to_build.replace(".", "_") + ".h", "<==", class_to_build]
	#process element
	multiprocess.run_in_pool(cmd_line,
	                         comment,
	                         file_cmd,
	                         store_output_file = file_warning,
	                         depend_data = {"file":file_depend,
	                                        "data":depend_files})
	debug.verbose("file= " + file_dst)
	#return file_dst
	return {"action":"path", "path":target.get_build_path(name) + target.path_generate_code}

