#!/usr/bin/python
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##
import os
import sys
# Local import
from . import target
from . import builder
from . import system
from . import host
from . import tools
from . import debug
from . import module

is_init = False

if is_init == False:
	debug.verbose("Use Make as a make stadard")
	sys.path.append(tools.get_run_folder())
	builder.import_path(tools.get_current_path(__file__))
	module.import_path(tools.get_current_path(__file__))
	system.import_path(tools.get_current_path(__file__))
	target.import_path(tools.get_current_path(__file__))
	
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


