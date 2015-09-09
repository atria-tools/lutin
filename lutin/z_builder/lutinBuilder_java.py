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
	return ["java"]

##
## @brief Get builder output file type
## @return List of extention supported
##
def get_output_type():
	return ["class"]

##
## @brief Commands for running gcc to compile a C++ file in object file.
##
def compile(file, binary, target, depancy, flags, path, name, basic_path):
	file_src = target.get_full_name_source(basic_path, file)
	file_cmd = target.get_full_name_cmd(name, basic_path, file)
	file_dst = target.get_full_name_destination(name, basic_path, file, get_output_type(), remove_suffix=True)
	file_depend = target.get_full_dependency(name, basic_path, file)
	file_warning = target.get_full_name_warning(name, basic_path, file)
	# create the command line befor requesting start:
	cmd = [
		target.java,
		"-d", target.get_build_path(name)
		]
	# add source dependency:
	list_sources_path = []
	for view in ["export", "local"]:
		try:
			list = path[view]["java"]
			for elem in list:
				list_sources_path.append(elem)
		except:
			pass
	if len(list_sources_path) > 0:
		cmd.append("-sourcepath")
		out = ""
		for elem in list_sources_path:
			if len(out) > 0:
				out += ":"
			out += elem
		cmd.append(out)
	class_extern = []
	upper_jar = tools.filter_extention(depancy.src, ["jar"])
	#debug.warning("ploppppp = " + str(upper_jar))
	for elem in upper_jar:
		class_extern.append(elem)
	if len(class_extern) > 0:
		cmd.append("-classpath")
		out = ""
		for elem in class_extern:
			if len(out) > 0:
				out += ":"
			out += elem
		cmd.append(out)
	
	cmd.append(file_src)
	# Create cmd line
	cmdLine=tools.list_to_str(cmd)
	
	# check the dependency for this file :
	if depend.need_re_build(file_dst, file_src, file_depend, file_cmd, cmdLine) == False:
		return {"action":"add", "file":file_dst}
	tools.create_directory_of_file(file_dst)
	comment = ["java", name, "<==", file]
	#process element
	multiprocess.run_in_pool(cmdLine, comment, file_cmd, store_output_file=file_warning)
	return {"action":"add", "file":file_dst}

