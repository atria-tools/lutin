##
## Objective-C builder
##
import lutinMultiprocess
import lutinTools
import lutinBuilder
import lutinDebug as debug
import lutinDepend as dependency

local_ref_on_builder_c = None

##
## Initialize the builder, if needed ... to get dependency between builder (for example)
##
def init():
	global local_ref_on_builder_c
	debug.debug("m builder get dependency on the C builder")
	local_ref_on_builder_c = lutinBuilder.get_builder("c")

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
	file_src, file_dst, file_depend, file_cmd = target.file_generate_object(binary, name, basic_folder, file)
	# create the command line befor requesting start:
	cmd = [
		target.cc,
		"-o", file_dst ,
		target.arch,
		target.sysroot,
		target.global_include_cc]
	try:
		cmd.append(lutinTools.add_prefix("-I",path["export"]))
	except:
		pass
	try:
		cmd.append(lutinTools.add_prefix("-I",path["local"]))
	except:
		pass
	try:
		cmd.append(lutinTools.add_prefix("-I",depancy.path))
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
	try:
		cmd.append(depancy.flags["c"])
	except:
		pass
	try:
		cmd.append(depancy.flags["m"])
	except:
		pass
	try:
		cmd.append(flags["local"]["c"])
	except:
		pass
	try:
		cmd.append(flags["local"]["m"])
	except:
		pass
	try:
		cmd.append(flags["export"]["c"])
	except:
		pass
	try:
		cmd.append(flags["export"]["m"])
	except:
		pass
	cmd.append("-c -MMD -MP")
	cmd.append("-x objective-c")
	cmd.append(file_src)
	# Create cmd line
	cmdLine=lutinTools.list_to_str(cmd)
	# check the dependency for this file :
	if False==dependency.need_re_build(file_dst, file_src, file_depend, file_cmd, cmdLine):
		return file_dst
	lutinTools.create_directory_of_file(file_dst)
	comment = ["m", name, "<==", file]
	#process element
	lutinMultiprocess.run_in_pool(cmdLine, comment, file_cmd)
	return file_dst

