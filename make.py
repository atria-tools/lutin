#!/usr/bin/python
# for path inspection:
import sys
import os
import inspect
import fnmatch
sys.path.append(os.path.dirname(__file__) + "/corePython/" )
import debug
# preparse the argument to get the erbose element for debug mode
for argument in sys.argv:
	if argument == "verbose":
		debug.SetLevel(5)

# now import other standard module
import module
import host
import buildTools
import host
import buildList


"""
	Display the help of this makefile
"""
def HelpDisplay():
	print "usage:"
	print "	" + sys.argv[0] + " [help] [dump] [all] [clean] [board=...] [clang/gcc] [debug/release] [check] [verbose] [color]"
	print "		[help] display this help"
	print "		[dump] dump all the module dependency"
	print "		[all] build all (only for the current selected board)"
	print "		[clean] clean all (same as previous)"
	print "		[board=...] select a board (by default the board is the computer that compile this"
	print "		[clang/gcc] Compile with clang or Gcc mode (by default gcc will be used)"
	print "		[debug/release] compile in release or debug mode (default release)"
	print "		[check] Check if all dependency are resolved"
	print "		[verbose] display makefile debug"
	print "		[color] display makefile output in color"
	print "		you can add 'module name' with at end : -clean to clean only this element"
	print "	ex: " + sys.argv[0] + " all board=Android all board=Windows all help"
	exit(0)

"""
	Run everything that is needed in the system
"""
def Start():
	# parse all argument
	if len(sys.argv)==1:
		#by default we build all binary for the current board
		buildList.Build("all")
	else:
		for argument in sys.argv[1:]:
			if argument == "help":
				#display help
				HelpDisplay()
			elif argument == "all":
				#build all the board
				buildList.Build("all")
			elif argument == "dump":
				module.Dump()
			elif argument == "verbose":
				# nothing to do ...
				None
			else:
				buildList.Build(argument)
	

"""
	When the user use with make.py we initialise ourself
"""
if __name__ == '__main__':
	debug.verbose("Use Make as a make stadard")
	sys.path.append(buildTools.GetRunFolder())
	debug.verbose(" try to impoert module 'Makefile.py'")
	__import__("Makefile")
	Start()



