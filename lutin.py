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

"""
	Display the help of this makefile
"""
def usage():
	print "usage:"
	print "	" + sys.argv[0] + " [options] [cible/properties] ..."
	print "		[help] display this help"
	print "	[option] : keep the last set"
	print "		-h / --help"
	print "			Display this help and break"
	print "		-v / -v? / --verbose=?"
	print "			Display makefile debug level (verbose) default =2"
	print "				0 : None"
	print "				1 : error"
	print "				2 : warning"
	print "				3 : info"
	print "				4 : debug"
	print "				5 : verbose"
	print "		-c / --color"
	print "			Display makefile output in color"
	print "		-f / --force"
	print "			Force the rebuild without checking the dependency"
	print "		-j= / --jobs"
	print "			Specifies the number of jobs (commands) to run simultaneously."
	print "	[properties] : keep in the sequency of the cible"
	print "		-t=... / --target=..."
	print "			(Android/Linux/MacOs/Windows) Select a target (by default the platform is the computer that compile this"
	print "		-C= / --compilator="
	print "			(clang/gcc) Compile with clang or Gcc mode (by default gcc will be used)"
	print "		-m=... / --mode=..."
	print "			(debug/release) Compile in release or debug mode (default release)"
	print "	[cible] : generate in order set"
	print "		all"
	print "			Build all (only for the current selected board) (bynary and packages)"
	print "		clean"
	print "			Clean all (same as previous)"
	print "		dump"
	print "			Dump all the module dependency and properties"
	listOfAllModule = lutinModule.ListAllModuleWithDesc()
	for mod in listOfAllModule:
		print "		" + mod[0] + " / " + mod[0] + "-clean / " + mod[0] + "-dump"
		print "			" + mod[1]
	print "	ex: " + sys.argv[0] + " all board=Android all board=Windows all help"
	exit(0)

# preparse the argument to get the erbose element for debug mode
def parseGenericArg(argument,active):
	if    argument == "-h" \
	   or argument == "--help":
		#display help
		if active==False:
			usage()
		return True
	elif    argument[:3] == "-j=" \
	     or argument[:2] == "-j" \
	     or argument[:7] == "--jobs=":
		if active==True:
			val = "1"
			if argument[:3] == "-j=":
				val = argument[3:]
			elif argument[:2] == "-j":
				if len(argument) == 2:
					val = "1"
				else:
					val = argument[2:]
			else:
				val = argument[7:]
			lutinMultiprocess.SetCoreNumber(int(val))
		return True
	elif    argument[:3] == "-v=" \
	     or argument[:2] == "-v" \
	     or argument[:10] == "--verbose=" \
	     or argument[:9] == "--verbose":
		if active==True:
			val = "5"
			if argument[:3] == "-v=":
				val = argument[3:]
			elif argument[:2] == "-v":
				if len(argument) == 2:
					val = "5"
				else:
					val = argument[2:]
			else:
				if len(argument) == 9:
					val = "5"
				else:
					val = argument[10:]
			debug.SetLevel(int(val))
		return True
	elif    argument == "-c" \
	     or argument == "--color":
		if active==True:
			debug.EnableColor()
		return True
	elif    argument == "-f" \
	     or argument == "--force":
		if active==True:
			lutinEnv.SetForceMode(True)
		return True
	return False

# parse default unique argument:
if __name__ == "__main__":
	sys.path.append(os.path.dirname(__file__) + "/corePython/" )
	for argument in sys.argv:
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
	# load the default target :
	target = None
	actionDone=False
	# parse all argument
	for argument in sys.argv[1:]:
		if True==parseGenericArg(argument, False):
			None # nothing to do ...
		elif argument[:13] == "--compilator=" or argument[:3] == "-C=":
			tmpArg=""
			if argument[:3] == "-C=":
				tmpArg=argument[3:]
			else:
				tmpArg=argument[13:]
			# check input ...
			if tmpArg=="gcc" or tmpArg=="clang":
				if compilator!=tmpArg:
					debug.debug("change compilator ==> " + tmpArg)
					compilator=tmpArg
					#remove previous target
					target = None
			else:
				debug.error("Set --compilator/-C: '" + tmpArg + "' but only availlable : [gcc/clang]")
		elif argument[:9] == "--target=" or argument[:3] == "-t=":
			tmpArg=""
			if argument[:3] == "-t=":
				tmpArg=argument[3:]
			else:
				tmpArg=argument[9:]
			# No check input ==> this will be verify automaticly chen the target will be loaded
			if targetName!=tmpArg:
				debug.debug("change target ==> " + tmpArg + " & reset mode : gcc&release")
				targetName=tmpArg
				#reset properties by defauult:
				compilator="gcc"
				mode="release"
				#remove previous target
				target = None
		elif argument[:7] == "--mode=" or argument[:3] == "-m=":
			tmpArg=""
			if argument[:3] == "-m=":
				tmpArg=argument[3:]
			else:
				tmpArg=argument[11:]
			if "debug"==tmpArg or "release"==tmpArg:
				if mode!=tmpArg:
					debug.debug("change mode ==> " + tmpArg)
					mode = tmpArg
					#remove previous target
					target = None
			else:
				debug.error("Set --mode/-m: '" + tmpArg + "' but only availlable : [debug/release]")
		else:
			#load the target if needed :
			if target == None:
				target = lutinTarget.TargetLoad(targetName, compilator, mode)
			target.Build(argument)
			actionDone=True
	# if no action done : we do "all" ...
	if actionDone==False:
		#load the target if needed :
		if target == None:
			target = lutinTarget.TargetLoad(targetName, compilator, mode)
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
	__import__("lutinBase")
	Start()



