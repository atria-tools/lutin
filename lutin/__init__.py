#!/usr/bin/python

import os
import sys

# now import other standard module (must be done here and not before ...
from . import target
from . import builder
from . import system
from . import host
from . import tools
from . import debug
from . import module

is_init = False

if is_init == False:
	"""
		When the user use with make.py we initialise ourself
	"""
	debug.verbose("Use Make as a make stadard")
	sys.path.append(tools.get_run_folder())
	
	debug.debug("missing file lutinBase.py ==> loading subPath...");
	# Import all sub path without out and archive
	for folder in os.listdir("."):
		if os.path.isdir(folder)==True:
			if     folder.lower()!="android" \
			   and folder.lower()!="archive" \
			   and folder.lower()!="out" :
				debug.debug("Automatic load path: '" + folder + "'")
				builder.import_path(folder)
				module.import_path(folder)
				system.import_path(folder)
				target.import_path(folder)
	
	builder.init()
	
	is_init = True


