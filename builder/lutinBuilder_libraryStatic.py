##
## Static library builder
##

##
## Get the current builder type.
## Return the type of builder
##
def getType():
	return "linker"

##
## @brief Commands for running ar.
##
def link(self, file, binary, target, depancy, libName=""):
	if libName == "":
		libName = self.name
	file_src, file_dst, file_depend, file_cmd = target.generate_file(binary, libName,self.originFolder,file,"lib-static")
	#$(Q)$(TARGET_AR) $(TARGET_GLOBAL_ARFLAGS) $(PRIVATE_ARFLAGS) $@ $(PRIVATE_ALL_OBJECTS)
	cmdLine=lutinTools.list_to_str([
		target.ar,
		target.global_flags_ar,
		self.flags_ar,
		file_dst,
		file_src])#,
		#depancy.src])
	
	# check the dependency for this file :
	if     dependency.need_re_package(file_dst, file_src, True, file_cmd, cmdLine) == False \
	   and dependency.need_re_package(file_dst, depancy.src, False, file_cmd, cmdLine) == False:
		return file_dst
	lutinTools.create_directory_of_file(file_dst)
	debug.print_element("StaticLib", libName, "==>", file_dst)
	# explicitly remove the destination to prevent error ...
	if os.path.exists(file_dst) and os.path.isfile(file_dst):
		os.remove(file_dst)
	lutinMultiprocess.run_command(cmdLine)
	#$(Q)$(TARGET_RANLIB) $@
	if target.ranlib != "":
		cmdLineRanLib=lutinTools.list_to_str([
			target.ranlib,
			file_dst ])
		lutinMultiprocess.run_command(cmdLineRanLib)
	# write cmd line only after to prevent errors ...
	lutinMultiprocess.store_command(cmdLine, file_cmd)
	return file_dst
