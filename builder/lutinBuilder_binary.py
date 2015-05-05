##
## Executable/binary builder
##

##
## Initialize the builder, if needed ... to get dependency between builder (for example)
##
def init():
	pass

##
## Get the current builder type.
## Return the type of builder
##
def getType():
	return "linker"


##
## @brief Get builder input file type
## @return List of extention supported
##
def getInputType():
	return ["o"]

##
## @brief Get builder output file type
## @return List of extention supported
##
def getOutputType():
	return ["", "exe"]


##
## @brief Commands for running gcc to link an executable.
##
def link(file, binary, target, depancy, libName=""):
	if libName=="":
		libName = self.name
	file_src, file_dst, file_depend, file_cmd = target.generate_file(binary, libName,self.originFolder,file,"bin")
	#create comdLine : 
	cmdLine=lutinTools.list_to_str([
		target.xx,
		target.arch,
		target.sysroot,
		target.global_sysroot,
		"-o", file_dst,
		file_src,
		depancy.src,
		self.flags_ld,
		depancy.flags_ld,
		target.global_flags_ld])
	# check the dependency for this file :
	if     dependency.need_re_package(file_dst, file_src, True, file_cmd, cmdLine) == False \
	   and dependency.need_re_package(file_dst, depancy.src, False, file_cmd, cmdLine) == False:
		return file_dst
	lutinTools.create_directory_of_file(file_dst)
	debug.print_element("Executable", libName, "==>", file_dst)
	
	lutinMultiprocess.run_command(cmdLine)
	if    target.config["mode"] == "release"\
	   or lutinEnv.get_force_strip_mode() == True:
		# get the file size of the non strip file
		originSize = lutinTools.file_size(file_dst);
		debug.print_element("Executable(strip)", libName, "", "")
		cmdLineStrip=lutinTools.list_to_str([
			target.strip,
			file_dst])
		lutinMultiprocess.run_command(cmdLineStrip)
		# get the stip size of the binary
		stripSize = lutinTools.file_size(file_dst)
		debug.debug("file reduce size : " + str(originSize/1024) + "ko ==> " + str(stripSize/1024) + "ko")
	# write cmd line only after to prevent errors ...
	lutinMultiprocess.store_command(cmdLine, file_cmd)
	