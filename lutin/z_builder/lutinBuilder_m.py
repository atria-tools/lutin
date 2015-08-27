##
## Objective-C builder
##
from lutin import multiprocess
from lutin import tools
from lutin import builder
from lutin import debug
from lutin import depend

local_ref_on_builder_c = None

##
## Initialize the builder, if needed ... to get dependency between builder (for example)
##
def init():
	global local_ref_on_builder_c
	debug.debug("m builder get dependency on the C builder")
	local_ref_on_builder_c = builder.get_builder("c")

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
	return ["m", "M"]

##
## @brief Get builder output file type
## @return List of extention supported
##
def get_output_type():
	return ["o"]

##
## @brief Commands for running gcc to compile a m file in object file.
##
def compile(file, binary, target, depancy, flags, path, name, basic_folder):
	file_src = target.get_full_name_source(basic_folder, file)
	file_cmd = target.get_full_name_cmd(name, basic_folder, file)
	file_dst = target.get_full_name_destination(name, basic_folder, file, get_output_type())
	file_depend = target.get_full_dependency(name, basic_folder, file)
	file_warning = target.get_full_name_warning(name, basic_folder, file)
	# create the command line befor requesting start:
	cmd = [
		target.cc,
		"-o", file_dst ,
		target.arch,
		target.sysroot,
		target.global_include_cc]
	for view in ["export", "local"]:
		for type in ["c", "m"]:
			try:
				cmd.append(tools.add_prefix("-I",path[view][type]))
			except:
				pass
	for type in ["c", "m"]:
		try:
			cmd.append(tools.add_prefix("-I",depancy.path[type]))
		except:
			pass
	try:
		cmd.append(local_ref_on_builder_c.get_version_compilation_flags(flags, depancy.flags))
	except:
		pass
	try:
		cmd.append(target.global_flags_cc)
	except:
		pass
	try:
		cmd.append(target.global_flags_m)
	except:
		pass
	for type in ["c", "m"]:
		try:
			cmd.append(depancy.flags[type])
		except:
			pass
	for view in ["local", "export"]:
		for type in ["c", "m"]:
			try:
				cmd.append(flags[view][type])
			except:
				pass
	cmd.append("-c -MMD -MP")
	cmd.append("-x objective-c")
	cmd.append(file_src)
	# Create cmd line
	cmdLine=tools.list_to_str(cmd)
	# check the dependency for this file :
	if False==depend.need_re_build(file_dst, file_src, file_depend, file_cmd, cmdLine):
		return {"action":"add", "file":file_dst}
	tools.create_directory_of_file(file_dst)
	comment = ["m", name, "<==", file]
	#process element
	multiprocess.run_in_pool(cmdLine, comment, file_cmd, store_output_file=file_warning)
	return {"action":"add", "file":file_dst}

