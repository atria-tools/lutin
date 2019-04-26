#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license MPL v2.0 (see license file)
##

from realog import debug
from lutin import system
from lutin import tools
from lutin import env
import os

class System(system.System):
	def __init__(self, target):
		system.System.__init__(self)
		# create some HELP:
		self.set_help("pthread : Generic multithreading system\n Can be install with the package:\n    - pthread-dev")
		# check if the library exist:
		"""
		if     not os.path.isfile("/usr/include/pthread.h"):
			# we did not find the library reqiested (just return) (automaticly set at false)
			return;
		"""
		self.set_valid(True)
		# todo : create a searcher of the presence of the library:
		self.add_flag("link-lib", "pthread")
		self.add_depend([
		    'c'
		    ])
		if env.get_isolate_system() == True:
			self.add_header_file([
			    "/usr/include/sched.h",
			    "/usr/include/pthread.h"
			    ],
			    clip_path="/usr/include/")
			self.add_header_file([
			    "/usr/include/pthread/*",
			    ],
			    destination_path="pthread",
			    recursive=True)
			self.add_header_file([
			    "/usr/include/pthread/*",
			    ],
			    destination_path="",
			    recursive=True)
	


