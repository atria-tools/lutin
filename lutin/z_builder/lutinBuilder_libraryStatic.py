##
## Static library builder
##
from lutin import multiprocess
from lutin import tools
from lutin import debug
from lutin import depend
from lutin import env
import os

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
	return "linker"

##
## @brief Get builder input file type
## @return List of extention supported
##
def get_input_type():
	return ["o", "a"]

##
## @brief Get builder output file type
## @return List of extention supported
##
def get_output_type():
	return ["a"]

##
## @brief Commands for running ar.
##
def link(file, binary, target, depancy, name, basic_path):
	file_src, file_dst, file_depend, file_cmd, file_warning = target.generate_file(binary, name, basic_path, file, "lib-static")
	#$(Q)$(TARGET_AR) $(TARGET_GLOBAL_ARFLAGS) $(PRIVATE_ARFLAGS) $@ $(PRIVATE_ALL_OBJECTS)
	cmd = [
		target.ar
		]
	try:
		cmd.append(target.global_flags_ar)
	except:
		pass
	try:
		cmd.append(flags["local"]["link"])
	except:
		pass
	try:
		cmd.append(file_dst)
	except:
		pass
	try:
		cmd.append(file_src)
	except:
		pass
	cmdLine=tools.list_to_str(cmd)
	# check the dependency for this file :
	if     depend.need_re_package(file_dst, file_src, True, file_cmd, cmdLine) == False \
	   and depend.need_re_package(file_dst, depancy.src, False, file_cmd, cmdLine) == False:
		return file_dst
	tools.create_directory_of_file(file_dst)
	debug.print_element("StaticLib", name, "==>", file_dst)
	# explicitly remove the destination to prevent error ...
	if os.path.exists(file_dst) and os.path.isfile(file_dst):
		os.remove(file_dst)
	multiprocess.run_command(cmdLine, store_output_file=file_warning)
	#$(Q)$(TARGET_RANLIB) $@
	if target.ranlib != "":
		cmdLineRanLib=tools.list_to_str([
			target.ranlib,
			file_dst ])
		multiprocess.run_command(cmdLineRanLib, store_output_file=file_warning)
	# write cmd line only after to prevent errors ...
	tools.store_command(cmdLine, file_cmd)
	return file_dst
