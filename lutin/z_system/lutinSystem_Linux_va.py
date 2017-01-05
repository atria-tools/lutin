#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license MPL v2.0 (see license file)
##

from lutin import debug
from lutin import system
from lutin import tools
from lutin import env
import os

class System(system.System):
	def __init__(self, target):
		system.System.__init__(self)
		# create some HELP:
		self.set_help("va : Video Acceleration")
		# check if the library exist:
		if not os.path.isfile("/usr/include/va/va.h"):
			# we did not find the library reqiested (just return) (automaticly set at false)
			return;
		# No check ==> on the basic std libs:
		self.set_valid(True)
		self.add_depend([
		    'X11'
		    ])
		self.add_flag("link-lib", ["va", "va-drm", "va-x11"])
		if env.get_isolate_system() == True:
			#self.add_flag("link-lib", "xns")
			self.add_header_file([
			    "/usr/include/va/*"
			    ],
			    destination_path="va",
			    recursive=True)
		



