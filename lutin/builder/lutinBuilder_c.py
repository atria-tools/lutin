##
## C builder
##
import lutinMultiprocess
import lutinTools
import lutinDebug as debug
import lutinDepend as dependency

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
## @brief Commands for running gcc to compile a C file in object file.
##
def compile(file, binary, target, depancy, flags, path, name, basic_folder):
	file_src, file_dst, file_depend, file_cmd = target.file_generate_object(binary, name, basic_folder,file)
	
	# create the command line befor requesting start:
	cmd = [
		target.cc,
		"-o", file_dst,
		target.arch,
		target.sysroot,
		target.global_include_cc]
	try:
		cmd.append(lutinTools.add_prefix("-I", path["export"]))
	except:
		pass
	try:
		cmd.append(lutinTools.add_prefix("-I", path["local"]))
	except:
		pass
	try:
		cmd.append(lutinTools.add_prefix("-I", depancy.path))
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
		cmd.append(depancy.flags["c"])
	except:
		pass
	try:
		cmd.append(flags["local"]["c"])
	except:
		pass
	try:
		cmd.append(flags["export"]["c"])
	except:
		pass
	cmd.append("-c")
	cmd.append("-MMD")
	cmd.append("-MP")
	cmd.append(file_src)
	# Create cmd line
	cmdLine=lutinTools.list_to_str(cmd)
	# check the dependency for this file :
	if dependency.need_re_build(file_dst, file_src, file_depend, file_cmd, cmdLine) == False:
		return file_dst
	lutinTools.create_directory_of_file(file_dst)
	comment = ["c", name, "<==", file]
	# process element
	lutinMultiprocess.run_in_pool(cmdLine, comment, file_cmd)
	return file_dst


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
	if version == 2011:
		if is_gnu ==True:
			out = ["-std=gnu11", "-D__C_VERSION__=2011"]
		else:
			out = ["-std=c11", "-D__C_VERSION__=1989"]
	elif version == 1999:
		if is_gnu ==True:
			out = ["-std=gnu99", "-D__C_VERSION__=1999"]
		else:
			out = ["-std=c99", "-D__C_VERSION__=1989"]
	elif version == 1990:
		if is_gnu ==True:
			out = ["-std=gnu90", "-D__C_VERSION__=1990"]
		else:
			out = ["-std=c90", "-D__C_VERSION__=1989"]
	else:
		if is_gnu ==True:
			out = ["-std=gnu89", "-D__C_VERSION__=1989"]
		else:
			out = ["-std=c89", "-D__C_VERSION__=1989"]
	return out
