##
## Objective-C builder
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
	return ["m", "M"]

##
## @brief Commands for running gcc to compile a m file in object file.
##
def compile(self, file, binary, target, depancy):
	file_src, file_dst, file_depend, file_cmd = target.file_generate_object(binary,self.name,self.originFolder,file)
	# create the command line befor requesting start:
	cmdLine=lutinTools.list_to_str([
		target.cc,
		"-o", file_dst ,
		target.arch,
		target.sysroot,
		target.global_include_cc,
		lutinTools.add_prefix("-I",self.export_path),
		lutinTools.add_prefix("-I",self.local_path),
		lutinTools.add_prefix("-I",depancy.path),
		self.get_c_version_compilation_flags(depancy.flags_cc_version),
		target.global_flags_cc,
		target.global_flags_m,
		depancy.flags_cc,
		depancy.flags_m,
		self.flags_m,
		self.flags_cc,
		self.export_flags_m,
		self.export_flags_cc,
		"-c -MMD -MP",
		"-x objective-c",
		file_src])
	# check the dependency for this file :
	if False==dependency.need_re_build(file_dst, file_src, file_depend, file_cmd, cmdLine):
		return file_dst
	lutinTools.create_directory_of_file(file_dst)
	comment = ["m", self.name, "<==", file]
	#process element
	lutinMultiprocess.run_in_pool(cmdLine, comment, file_cmd)
	return file_dst

