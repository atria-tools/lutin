##
## C++ builder
##

##
## Get the current builder type.
## Return the type of builder
##
def getType():
	return "compiler"

##
## @brief Get builder file type
## @return List of extention supported
##
def getBuildType():
	return ["cpp", "CPP", "cxx", "CXX", "xx", "XX", "CC", "cc"]


##
## @brief Commands for running gcc to compile a C++ file in object file.
##
def compile(self, file, binary, target, depancy):
	file_src, file_dst, file_depend, file_cmd = target.file_generate_object(binary,self.name,self.originFolder,file)
	
	# create the command line befor requesting start:
	cmdLine=lutinTools.list_to_str([
		target.xx,
		"-o", file_dst,
		target.arch,
		target.sysroot,
		target.global_include_cc,
		lutinTools.add_prefix("-I",self.export_path),
		lutinTools.add_prefix("-I",self.local_path),
		lutinTools.add_prefix("-I",depancy.path),
		self.get_xx_version_compilation_flags(depancy.flags_xx_version),
		target.global_flags_cc,
		target.global_flags_xx,
		depancy.flags_cc,
		depancy.flags_xx,
		self.flags_xx,
		self.flags_cc,
		self.export_flags_xx,
		self.export_flags_cc,
		" -c -MMD -MP",
		file_src])
	# check the dependency for this file :
	if False==dependency.need_re_build(file_dst, file_src, file_depend, file_cmd, cmdLine):
		return file_dst
	lutinTools.create_directory_of_file(file_dst)
	comment = ["c++", self.name, "<==", file]
	#process element
	lutinMultiprocess.run_in_pool(cmdLine, comment, file_cmd)
	return file_dst
