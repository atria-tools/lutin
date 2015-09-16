##
## C++ builder
##
from lutin import multiprocess
from lutin import tools
from lutin import debug
from lutin import depend
# C++ default version:
default_version = 1999
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
	return ["cpp", "CPP", "cxx", "CXX", "xx", "XX", "CC", "cc"]

##
## @brief Get builder output file type
## @return List of extention supported
##
def get_output_type():
	return ["o"]

##
## @brief Commands for running gcc to compile a C++ file in object file.
##
def compile(file, binary, target, depancy, flags, path, name, basic_path, module_src):
	file_src = target.get_full_name_source(basic_path, file)
	file_cmd = target.get_full_name_cmd(name, basic_path, file)
	file_dst = target.get_full_name_destination(name, basic_path, file, get_output_type())
	file_depend = target.get_full_dependency(name, basic_path, file)
	file_warning = target.get_full_name_warning(name, basic_path, file)
	# create the command line befor requesting start:
	cmd = [
		target.xx,
		"-o", file_dst,
		target.arch,
		target.sysroot,
		target.global_include_cc
		]
	for view in ["export", "local"]:
		for type in ["c", "c++"]:
			try:
				cmd.append(tools.add_prefix("-I",path[view][type]))
			except:
				pass
	for type in ["c", "c++"]:
		try:
			cmd.append(tools.add_prefix("-I",depancy.path[type]))
		except:
			pass
	try:
		cmd.append(get_version_compilation_flags(flags, depancy.flags))
	except:
		pass
	try:
		cmd.append(target.global_flags_cc)
	except:
		pass
	try:
		cmd.append(target.global_flags_xx)
	except:
		pass
	for type in ["c", "c++"]:
		try:
			cmd.append(depancy.flags[type])
		except:
			pass
	for view in ["local", "export"]:
		for type in ["c", "c++"]:
			try:
				cmd.append(flags[view][type])
			except:
				pass
	cmd.append(["-c", "-MMD", "-MP"])
	cmd.append(file_src)
	# Create cmd line
	cmdLine=tools.list_to_str(cmd)
	# check the dependency for this file :
	if depend.need_re_build(file_dst, file_src, file_depend, file_cmd, cmdLine) == False:
		return {"action":"add", "file":file_dst}
	tools.create_directory_of_file(file_dst)
	comment = ["c++", name, "<==", file]
	#process element
	multiprocess.run_in_pool(cmdLine, comment, file_cmd, store_output_file=file_warning)
	return {"action":"add", "file":file_dst}

def get_version_compilation_flags(flags, dependency_flags):
	try:
		version_local = flags["local"]["c++-version"]["version"]
	except:
		version_local = default_version
	try:
		dependency_version = dependency_flags["c++-version"]
	except:
		dependency_version = default_version
	try:
		is_gnu = flags["local"]["c++-version"]["gnu"]
	except:
		is_gnu = default_version_gnu
	
	version = max(version_local, dependency_version)
	if version == 2014:
		debug.error("not supported flags for X14 ...");
		if is_gnu == True:
			out = ["-std=gnu++14", "-D__CPP_VERSION__=2014"]
		else:
			out = ["-std=c++14", "-D__CPP_VERSION__=2014"]
	elif version == 2011:
		if is_gnu == True:
			out = ["-std=gnu++11", "-D__CPP_VERSION__=2011"]
		else:
			out = ["-std=c++11", "-D__CPP_VERSION__=2011"]
	elif version == 2003:
		if is_gnu == True:
			out = ["-std=gnu++03", "-D__CPP_VERSION__=2003"]
		else:
			out = ["-std=c++03", "-D__CPP_VERSION__=2003"]
	else:
		if is_gnu == True:
			out = ["-std=gnu++98", "-D__CPP_VERSION__=1999"]
		else:
			out = ["-std=c++98", "-D__CPP_VERSION__=1999"]
	return out
