#!/usr/bin/python
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##

import os
import lutinDebug as debug
import lutinEnv as environement


def need_re_build(dst, src, dependFile=None, file_cmd="", cmdLine=""):
	debug.extreme_verbose("Resuest check of dependency of :")
	debug.extreme_verbose("		dst='" + str(dst) + "'")
	debug.extreme_verbose("		str='" + str(src) + "'")
	debug.extreme_verbose("		dept='" + str(dependFile) + "'")
	debug.extreme_verbose("		cmd='" + str(file_cmd) + "'")
	# if force mode selected ==> just force rebuild ...
	if environement.get_force_mode():
		debug.extreme_verbose("			==> must rebuild (force mode)")
		return True
	
	# check if the destination existed:
	if     dst != "" \
	   and dst != None \
	   and os.path.exists(dst) == False:
		debug.extreme_verbose("			==> must rebuild (dst does not exist)")
		return True
	if     dst != "" \
	   and dst != None \
	   and os.path.exists(src) == False:
		debug.warning("			==> unexistant file :'" + src + "'")
		return True
	# chek the basic date if the 2 files
	if     dst != "" \
	   and dst != None \
	   and os.path.getmtime(src) > os.path.getmtime(dst):
		debug.extreme_verbose("			==> must rebuild (source time greater)")
		return True
	
	if     dependFile != "" \
	   and dependFile != None \
	   and os.path.exists(dependFile) == False:
		debug.extreme_verbose("			==> must rebuild (no depending file)")
		return True
	
	if     file_cmd != "" \
	   and file_cmd != None:
		if os.path.exists(file_cmd) == False:
			debug.extreme_verbose("			==> must rebuild (no commandLine file)")
			return True
		# check if the 2 cmdline are similar :
		file2 = open(file_cmd, "r")
		firstAndUniqueLine = file2.read()
		if firstAndUniqueLine != cmdLine:
			debug.extreme_verbose("			==> must rebuild (cmdLines are not identical)")
			debug.extreme_verbose("				==> '" + cmdLine + "'")
			debug.extreme_verbose("				==> '" + firstAndUniqueLine + "'")
			file2.close()
			return True
		# the cmdfile is correct ...
		file2.close()
	
	if     dependFile != "" \
	   and dependFile != None:
		debug.extreme_verbose("			start parsing dependency file : '" + dependFile + "'")
		file = open(dependFile, "r")
		for curLine in file.readlines():
			# normal file : end with : ": \\n"
			curLine = curLine[:len(curLine)-1]
			# removing last \ ...
			if curLine[len(curLine)-1:] == '\\' :
				curLine = curLine[:len(curLine)-1]
			# remove white space : 
			#debug.verbose("				Line (read) : '" + curLine + "'");
			curLine = curLine.strip()
			#debug.verbose("				Line (strip) : '" + curLine + "'");
			
			testFile=""
			if curLine[len(curLine)-1:] == ':':
				debug.extreme_verbose("				Line (no check (already done) : '" + curLine + "'");
			elif    len(curLine) == 0 \
			     or curLine == '\\':
				debug.extreme_verbose("				Line (Not parsed) : '" + curLine + "'");
			else:
				testFile = curLine
				debug.extreme_verbose("				Line (might check) : '" + testFile + "'");
			# really check files:
			if testFile!="":
				debug.extreme_verbose("					==> test");
				if False==os.path.exists(testFile):
					debug.extreme_verbose("			==> must rebuild (a dependency file does not exist)")
					file.close()
					return True
				if os.path.getmtime(testFile) > os.path.getmtime(dst):
					debug.extreme_verbose("			==> must rebuild (a dependency file time is newer)")
					file.close()
					return True
		# close the current file :
		file.close()
	
	debug.extreme_verbose("			==> Not rebuild (all dependency is OK)")
	return False



def need_re_package(dst, srcList, mustHaveSrc, file_cmd="", cmdLine=""):
	debug.extreme_verbose("Resuest check of dependency of :")
	debug.extreme_verbose("		dst='" + dst + "'")
	debug.extreme_verbose("		src()=")
	for src in srcList:
		debug.verbose("			'" + src + "'")
	
	if mustHaveSrc==False and len(srcList)==0:
		return False
	
	# if force mode selected ==> just force rebuild ...
	if environement.get_force_mode():
		debug.extreme_verbose("			==> must re-package (force mode)")
		return True
	
	# check if the destination existed:
	if False==os.path.exists(dst):
		debug.extreme_verbose("			==> must re-package (dst does not exist)")
		return True
	# chek the basic date if the 2 files
	if len(srcList)==0:
		debug.extreme_verbose("			==> must re-package (no source ???)")
		return True
	for src in srcList:
		if os.path.getmtime(src) > os.path.getmtime(dst):
			debug.extreme_verbose("			==> must re-package (source time greater) : '" + src + "'")
			return True
	
	if ""!=file_cmd:
		if False==os.path.exists(file_cmd):
			debug.extreme_verbose("			==> must rebuild (no commandLine file)")
			return True
		# check if the 2 cmdline are similar :
		file2 = open(file_cmd, "r")
		firstAndUniqueLine = file2.read()
		if firstAndUniqueLine != cmdLine:
			debug.extreme_verbose("			==> must rebuild (cmdLines are not identical)")
			debug.extreme_verbose("				==> '" + cmdLine + "'")
			debug.extreme_verbose("				==> '" + firstAndUniqueLine + "'")
			file2.close()
			return True
		# the cmdfile is correct ...
		file2.close()
	
	debug.extreme_verbose("			==> Not re-package (all dependency is OK)")
	return False



