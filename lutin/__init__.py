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
	sys.path.append(tools.get_run_path())
	builder.import_path(tools.get_current_path(__file__))
	module.import_path(tools.get_current_path(__file__))
	system.import_path(tools.get_current_path(__file__))
	target.import_path(tools.get_current_path(__file__))
	
	debug.debug("missing file lutinBase.py ==> loading subPath...");
	# Import all sub path without out and archive
	for path in os.listdir("."):
		if os.path.isdir(path)==True:
			if     path.lower()!="android" \
			   and path.lower()!="archive" \
			   and path.lower()!="out" :
				debug.debug("Automatic load path: '" + path + "'")
				builder.import_path(path)
				module.import_path(path)
				system.import_path(path)
				target.import_path(path)
	
	builder.init()
	
	is_init = True


