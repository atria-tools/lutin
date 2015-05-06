##
## Executable/binary builder
##
import lutinMultiprocess
import lutinTools
import lutinDebug as debug
import lutinDepend as dependency
import lutinEnv
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
	return ["o"]

##
## @brief Get builder output file type
## @return List of extention supported
##
def get_output_type():
	return ["", "exe", "bin"]


##
## @brief Commands for running gcc to link an executable.
##
def link(file, binary, target, depancy, name, basic_folder):
	file_src, file_dst, file_depend, file_cmd = target.generate_file(binary, name, basic_folder, file, "bin")
	#create comdLine :
	cmd = [
		target.xx
		]
	try:
		cmd.append(target.arch)
	except:
		pass
	try:
		cmd.append(target.sysroot)
	except:
		pass
	try:
		cmd.append(target.global_sysroot)
	except:
		pass
	try:
		cmd.append(["-o", file_dst])
	except:
		pass
	try:
		cmd.append(file_src)
	except:
		pass
	try:
		cmd.append(depancy.src)
	except:
		pass
	try:
		cmd.append(flags["local"]["link"])
	except:
		pass
	try:
		cmd.append(depancy.flags["link"])
	except:
		pass
	try:
		cmd.append(target.global_flags_ld)
	except:
		pass
	cmdLine=lutinTools.list_to_str(cmd)
	# check the dependency for this file :
	if     dependency.need_re_package(file_dst, file_src, True, file_cmd, cmdLine) == False \
	   and dependency.need_re_package(file_dst, depancy.src, False, file_cmd, cmdLine) == False:
		return file_dst
	lutinTools.create_directory_of_file(file_dst)
	debug.print_element("Executable", name, "==>", file_dst)
	
	lutinMultiprocess.run_command(cmdLine)
	if    target.config["mode"] == "release"\
	   or lutinEnv.get_force_strip_mode() == True:
		# get the file size of the non strip file
		originSize = lutinTools.file_size(file_dst);
		debug.print_element("Executable(strip)", name, "", "")
		cmdLineStrip=lutinTools.list_to_str([
			target.strip,
			file_dst])
		lutinMultiprocess.run_command(cmdLineStrip)
		# get the stip size of the binary
		stripSize = lutinTools.file_size(file_dst)
		debug.debug("file reduce size : " + str(originSize/1024) + "ko ==> " + str(stripSize/1024) + "ko")
	# write cmd line only after to prevent errors ...
	lutinMultiprocess.store_command(cmdLine, file_cmd)
	