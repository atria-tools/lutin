#!/usr/bin/python
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

mylutinArg = lutinArg.lutinArg()
mylutinArg.Add(lutinArg.argDefine("h", "help", desc="display this help"))
mylutinArg.AddSection("option", "Can be set one time in all case")
mylutinArg.Add(lutinArg.argDefine("v", "verbose", list=[["0","None"],["1","error"],["2","warning"],["3","info"],["4","debug"],["5","verbose"]], desc="Display makefile debug level (verbose) default =2"))
mylutinArg.Add(lutinArg.argDefine("C", "color", desc="Display makefile output in color"))
mylutinArg.Add(lutinArg.argDefine("f", "force", desc="Force the rebuild without checking the dependency"))
mylutinArg.Add(lutinArg.argDefine("P", "pretty", desc="print the debug has pretty display"))
mylutinArg.Add(lutinArg.argDefine("j", "jobs", haveParam=True, desc="Specifies the number of jobs (commands) to run simultaneously"))
mylutinArg.Add(lutinArg.argDefine("s", "force-strip", desc="Force the stripping of the compile elements"))

mylutinArg.AddSection("properties", "keep in the sequency of the cible")
mylutinArg.Add(lutinArg.argDefine("t", "target", list=[["Android",""],["Linux",""],["MacOs",""],["Windows",""]], desc="Select a target (by default the platform is the computer that compile this"))
mylutinArg.Add(lutinArg.argDefine("c", "compilator", list=[["clang",""],["gcc",""]], desc="Compile with clang or Gcc mode (by default gcc will be used)"))
mylutinArg.Add(lutinArg.argDefine("m", "mode", list=[["debug",""],["release",""]], desc="Compile in release or debug mode (default release)"))
mylutinArg.Add(lutinArg.argDefine("p", "package", desc="Disable the package generation (usefull when just compile for test on linux ...)"))

mylutinArg.AddSection("cible", "generate in order set")
localArgument = mylutinArg.Parse()

"""
	Display the help of this makefile
"""
def usage():
	# generic argument displayed : 
	mylutinArg.Display()
	print "		all"
	print "			Build all (only for the current selected board) (bynary and packages)"
	print "		clean"
	print "			Clean all (same as previous)"
	print "		dump"
	print "			Dump all the module dependency and properties"
	print "		doc"
	print "			Create documentation of all module that is mark as availlable on it"
	listOfAllModule = lutinModule.ListAllModuleWithDesc()
	for mod in listOfAllModule:
		print "		" + mod[0] + " / " + mod[0] + "-clean / " + mod[0] + "-dump" + mod[0] + "-doc"
		print "			" + mod[1]
	print "	ex: " + sys.argv[0] + " all --target=Android all -t Windows -m debug all"
	exit(0)

# preparse the argument to get the verbose element for debug mode
def parseGenericArg(argument,active):
	if argument.GetOptionName() == "help":
		#display help
		if active==False:
			usage()
		return True
	elif argument.GetOptionName()=="jobs":
		if active==True:
			lutinMultiprocess.SetCoreNumber(int(argument.GetArg()))
		return True
	elif argument.GetOptionName() == "verbose":
		if active==True:
			debug.SetLevel(int(argument.GetArg()))
		return True
	elif argument.GetOptionName() == "color":
		if active==True:
			debug.EnableColor()
		return True
	elif argument.GetOptionName() == "force":
		if active==True:
			lutinEnv.SetForceMode(True)
		return True
	elif argument.GetOptionName() == "pretty":
		if active==True:
			lutinEnv.SetPrintPrettyMode(True)
		return True
	elif argument.GetOptionName() == "force-strip":
		if active==True:
			lutinEnv.SetForceStripMode(True)
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
	#compilation base
	compilator="gcc"
	# build mode
	mode="release"
	# package generationMode
	generatePackage=True
	# load the default target :
	target = None
	actionDone=False
	# parse all argument
	for argument in localArgument:
		if True==parseGenericArg(argument, False):
			continue
		elif argument.GetOptionName() == "package":
			generatePackage=False
		elif argument.GetOptionName() == "compilator":
			if compilator!=argument.GetArg():
				debug.debug("change compilator ==> " + argument.GetArg())
				compilator=argument.GetArg()
				#remove previous target
				target = None
		elif argument.GetOptionName() == "target":
			# No check input ==> this will be verify automaticly chen the target will be loaded
			if targetName!=argument.GetArg():
				targetName=argument.GetArg()
				debug.debug("change target ==> " + targetName + " & reset mode : gcc&release")
				#reset properties by defauult:
				compilator="gcc"
				mode="release"
				generatePackage=True
				#remove previous target
				target = None
		elif argument.GetOptionName() == "mode":
			if mode!=argument.GetArg():
				mode = argument.GetArg()
				debug.debug("change mode ==> " + mode)
				#remove previous target
				target = None
		else:
			if argument.GetOptionName() != "":
				debug.warning("Can not understand argument : '" + argument.GetOptionName() + "'")
				usage()
			else:
				#load the target if needed :
				if target == None:
					target = lutinTarget.TargetLoad(targetName, compilator, mode, generatePackage)
				target.Build(argument.GetArg())
				actionDone=True
	# if no action done : we do "all" ...
	if actionDone==False:
		#load the target if needed :
		if target == None:
			target = lutinTarget.TargetLoad(targetName, compilator, mode, generatePackage)
		target.Build("all")
	# stop all started threads 
	lutinMultiprocess.UnInit()

"""
	When the user use with make.py we initialise ourself
"""
if __name__ == '__main__':
	debug.verbose("Use Make as a make stadard")
	sys.path.append(lutinTools.GetRunFolder())
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
					lutinModule.ImportPath(folder)
	Start()



