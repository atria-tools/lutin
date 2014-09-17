#!/usr/bin/python
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##

# for path inspection:
import sys
import os
import inspect
import fnmatch
import lutinDebug as debug
import lutinEnv
import lutinModule
import lutinMultiprocess
import lutinArg

myLutinArg = lutinArg.LutinArg()
myLutinArg.add(lutinArg.ArgDefine("h", "help", desc="display this help"))
myLutinArg.add_section("option", "Can be set one time in all case")
myLutinArg.add(lutinArg.ArgDefine("v", "verbose", list=[["0","None"],["1","error"],["2","warning"],["3","info"],["4","debug"],["5","verbose"]], desc="display makefile debug level (verbose) default =2"))
myLutinArg.add(lutinArg.ArgDefine("C", "color", desc="display makefile output in color"))
myLutinArg.add(lutinArg.ArgDefine("f", "force", desc="Force the rebuild without checking the dependency"))
myLutinArg.add(lutinArg.ArgDefine("P", "pretty", desc="print the debug has pretty display"))
myLutinArg.add(lutinArg.ArgDefine("j", "jobs", haveParam=True, desc="Specifies the number of jobs (commands) to run simultaneously"))
myLutinArg.add(lutinArg.ArgDefine("s", "force-strip", desc="Force the stripping of the compile elements"))

myLutinArg.add_section("properties", "keep in the sequency of the cible")
myLutinArg.add(lutinArg.ArgDefine("t", "target", haveParam=True, desc="Select a target (by default the platform is the computer that compile this) To know list : 'lutin.py --list-target'"))
myLutinArg.add(lutinArg.ArgDefine("c", "compilator", list=[["clang",""],["gcc",""]], desc="Compile with clang or Gcc mode (by default gcc will be used)"))
myLutinArg.add(lutinArg.ArgDefine("m", "mode", list=[["debug",""],["release",""]], desc="Compile in release or debug mode (default release)"))
myLutinArg.add(lutinArg.ArgDefine("a", "arch", list=[["auto","Automatic choice"],["arm","Arm processer"],["x86","Generic PC : AMD/Intel"],["ppc","Power PC"]], desc="Architecture to compile"))
myLutinArg.add(lutinArg.ArgDefine("b", "bus", list=[["auto","Automatic choice"],["32","32 bits"],["64","64 bits"]], desc="Adressing size (Bus size)"))
myLutinArg.add(lutinArg.ArgDefine("r", "prj", desc="Use external project management (not build with lutin..."))
myLutinArg.add(lutinArg.ArgDefine("p", "package", desc="Disable the package generation (usefull when just compile for test on linux ...)"))
myLutinArg.add(lutinArg.ArgDefine("", "simulation", desc="simulater mode (availlable only for IOS)"))
myLutinArg.add(lutinArg.ArgDefine("", "list-target", desc="list all availlables targets ==> for auto completion"))
myLutinArg.add(lutinArg.ArgDefine("", "list-module", desc="list all availlables module ==> for auto completion"))

myLutinArg.add_section("cible", "generate in order set")
localArgument = myLutinArg.parse()

"""
	display the help of this makefile
"""
def usage():
	# generic argument displayed : 
	myLutinArg.display()
	print "		all"
	print "			build all (only for the current selected board) (bynary and packages)"
	print "		clean"
	print "			clean all (same as previous)"
	print "		dump"
	print "			Dump all the module dependency and properties"
	listOfAllModule = lutinModule.list_all_module_with_desc()
	for mod in listOfAllModule:
		print "		" + mod[0] + " / " + mod[0] + "-clean / " + mod[0] + "-dump"
		if mod[1] != "":
			print "			" + mod[1]
	print "	ex: " + sys.argv[0] + " all --target=Android all -t Windows -m debug all"
	exit(0)

# preparse the argument to get the verbose element for debug mode
def parseGenericArg(argument,active):
	if argument.get_option_nName() == "help":
		#display help
		if active==False:
			usage()
		return True
	if argument.get_option_nName() == "list-module":
		if active==False:
			listOfModule = lutinModule.list_all_module()
			retValue = ""
			for moduleName in listOfModule:
				if retValue != "":
					retValue += " "
				retValue += moduleName
			print retValue
			exit(0)
		return True
	if argument.get_option_nName() == "list-target":
		if active==False:
			listOfTarget = lutinTarget.list_all_target()
			retValue = ""
			for targetName in listOfTarget:
				if retValue != "":
					retValue += " "
				retValue += targetName
			print retValue
			exit(0)
		return True
	elif argument.get_option_nName()=="jobs":
		if active==True:
			lutinMultiprocess.set_core_number(int(argument.get_arg()))
		return True
	elif argument.get_option_nName() == "verbose":
		if active==True:
			debug.set_level(int(argument.get_arg()))
		return True
	elif argument.get_option_nName() == "color":
		if active==True:
			debug.enable_color()
		return True
	elif argument.get_option_nName() == "force":
		if active==True:
			lutinEnv.set_force_mode(True)
		return True
	elif argument.get_option_nName() == "pretty":
		if active==True:
			lutinEnv.set_print_pretty_mode(True)
		return True
	elif argument.get_option_nName() == "force-strip":
		if active==True:
			lutinEnv.set_force_strip_mode(True)
		return True
	return False

# parse default unique argument:
if __name__ == "__main__":
	for argument in localArgument:
		parseGenericArg(argument, True)

# now import other standard module (must be done here and not before ...
import lutinTarget
import lutinHost
import lutinTools

"""
	Run everything that is needed in the system
"""
def Start():
	#available target : Linux / MacOs / Windows / Android ...
	targetName=lutinHost.OS
	config = {
	             "compilator":"gcc",
	             "mode":"release",
	             "bus-size":"auto",
	             "arch":"auto",
	             "generate-package":True,
	             "simulation":False,
	             "extern-build":False
	          }
	# load the default target :
	target = None
	actionDone=False
	# parse all argument
	for argument in localArgument:
		if True==parseGenericArg(argument, False):
			continue
		elif argument.get_option_nName() == "package":
			config["generate-package"]=False
		elif argument.get_option_nName() == "simulation":
			config["simulation"]=True
		elif argument.get_option_nName() == "prj":
			config["extern-build"]=True
		elif argument.get_option_nName() == "bus":
			config["bus-size"]=argument.get_arg()
		elif argument.get_option_nName() == "arch":
			config["arch"]=argument.get_arg()
		elif argument.get_option_nName() == "compilator":
			if config["compilator"] != argument.get_arg():
				debug.debug("change compilator ==> " + argument.get_arg())
				config["compilator"] = argument.get_arg()
				#remove previous target
				target = None
		elif argument.get_option_nName() == "target":
			# No check input ==> this will be verify automaticly chen the target will be loaded
			if targetName!=argument.get_arg():
				targetName=argument.get_arg()
				debug.debug("change target ==> '" + targetName + "' & reset mode : gcc&release")
				#reset properties by defauult:
				config = {
				             "compilator":"gcc",
				             "mode":"release",
				             "bus-size":"auto",
				             "arch":"auto",
				             "generate-package":True,
				             "simulation":False,
				             "extern-build":False
				          }
				#remove previous target
				target = None
		elif argument.get_option_nName() == "mode":
			if config["mode"]!=argument.get_arg():
				config["mode"] = argument.get_arg()
				debug.debug("change mode ==> " + config["mode"])
				#remove previous target
				target = None
		else:
			if argument.get_option_nName() != "":
				debug.warning("Can not understand argument : '" + argument.get_option_nName() + "'")
				usage()
			else:
				#load the target if needed :
				if target == None:
					target = lutinTarget.load_target(targetName, config)
				target.build(argument.get_arg())
				actionDone=True
	# if no action done : we do "all" ...
	if actionDone==False:
		#load the target if needed :
		if target == None:
			target = lutinTarget.load_target(targetName, config)
		target.build("all")
	# stop all started threads 
	lutinMultiprocess.un_init()

"""
	When the user use with make.py we initialise ourself
"""
if __name__ == '__main__':
	debug.verbose("Use Make as a make stadard")
	sys.path.append(lutinTools.get_run_folder())
	debug.verbose(" try to impoert module 'lutinBase.py'")
	if os.path.exists("lutinBase.py" )==True:
		__import__("lutinBase")
	else:
		debug.debug("missing file lutinBase.py ==> loading subPath...");
		# Import all sub path without out and archive
		for folder in os.listdir("."):
			if os.path.isdir(folder)==True:
				if     folder.lower()!="android" \
				   and folder.lower()!="archive" \
				   and folder.lower()!="out" :
					debug.debug("Automatic load path: '" + folder + "'")
					lutinModule.import_path(folder)
					lutinTarget.import_path(folder)
	Start()



