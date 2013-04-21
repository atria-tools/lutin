#!/usr/bin/python
# for path inspection:
import sys
import os
import inspect
import fnmatch
import lutinDebug as debug
import lutinEnv


"""
	Display the help of this makefile
"""
def usage():
	print "usage:"
	print "	" + sys.argv[0] + " [options] [cible/properties] ..."
	print "		[help] display this help"
	print "	[option] : keep the last set"
	print "		[-h/--help]             Display this help and break"
	print "		[-v?/--verbose=?]       Display makefile debug level (verbose) default =2"
	print "		[-c/--color]            Display makefile output in color"
	print "		[-f/--force]            Force the rebuild without checking the dependency"
	print "	[properties] : keep in the sequency of the cible"
	print "		[-p=.../--platform=...] (Android/Linux/MacOs/Windows) Select a platform (by default the platform is the computer that compile this"
	print "		[-t/--tool]             (clang/gcc) Compile with clang or Gcc mode (by default gcc will be used)"
	print "		[-m=.../--mode=...]     (debug/release) Compile in release or debug mode (default release)"
	print "	[cible] : generate in order set"
	print "		[dump]                  Dump all the module dependency and properties"
	print "		[all]                   Build all (only for the current selected board) (bynary and packages)"
	print "		[clean]                 Clean all (same as previous)"
	print "		...                     You can add 'module name' with at end : -clean to clean only this element"
	print "	ex: " + sys.argv[0] + " all board=Android all board=Windows all help"
	exit(0)

# preparse the argument to get the erbose element for debug mode
def parseGenericArg(argument,active):
	if argument == "-h" or argument == "--help":
		#display help
		usage()
		return True
	elif argument[:2] == "-v":
		if active==True:
			if len(argument)==2:
				debug.SetLevel(5)
			else:
				debug.SetLevel(int(argument[2:]))
		return True
	elif argument[:9] == "--verbose":
		if active==True:
			if len(argument)==9:
				debug.SetLevel(5)
			else:
				if argument[:10] == "--verbose=":
					debug.SetLevel(int(argument[10:]))
				else:
					debug.SetLevel(int(argument[9:]))
		return True
	elif argument == "-c" or argument == "--color":
		if active==True:
			debug.EnableColor()
		return True
	elif argument == "-f" or argument == "--force":
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
import lutinModule as module
import lutinHost as host
import lutinTools
import lutinHost as host
import lutinList as buildList

import lutinTargetLinux


"""
	Run everything that is needed in the system
"""
def Start():
	target = lutinTargetLinux.TargetLinux("gcc", "debug")
	actionDone=False
	# parse all argument
	for argument in sys.argv[1:]:
		if True==parseGenericArg(argument, False):
			None # nothing to do ...
		elif argument[:11] == "--platform=" or argument[:3] == "-p=":
			tmpArg=""
			if argument[:3] == "-p=":
				tmpArg=argument[3:]
			else:
				tmpArg=argument[11:]
			# TODO ...
		elif argument[:7] == "--mode=" or argument[:3] == "-m=":
			tmpArg=""
			if argument[:3] == "-m=":
				tmpArg=argument[3:]
			else:
				tmpArg=argument[11:]
			if "debug"==tmpArg:
				lutinEnv.SetDebugMode(1)
			elif "release"==tmpArg:
				lutinEnv.SetDebugMode(0)
			else:
				debug.error("not understand build mode : '" + val + "' can be [debug/release]")
				lutinEnv.SetDebugMode(0)
		elif argument[:7] == "--tool=" or argument[:3] == "-t=":
			tmpArg=""
			if argument[:3] == "-t=":
				tmpArg=argument[3:]
			else:
				tmpArg=argument[11:]
			lutinEnv.SetCompileMode(tmpArg)
		else:
			target.Build(argument)
			actionDone=True
	# if no action done : we do "all" ...
	if actionDone==False:
		target.Build("all")

"""
	When the user use with make.py we initialise ourself
"""
if __name__ == '__main__':
	debug.verbose("Use Make as a make stadard")
	sys.path.append(lutinTools.GetRunFolder())
	debug.verbose(" try to impoert module 'lutinBase.py'")
	__import__("lutinBase")
	Start()



