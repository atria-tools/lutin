#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
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
		self.help="JACK : Jack Low-Latency Audio Server\n Can be install with the package:\n    - libjack-jackd2-dev (new)\n    - libjack-dev (old)"
		# check if the library exist:
		if     not os.path.isfile("/usr/include/jack/jack.h"):
			# we did not find the library reqiested (just return) (automaticly set at false)
			return;
		self.valid = True
		self.add_depend([
		    'uuid',
		    'c'
		    ])
		self.add_flag("link-lib", "jack")
		if env.get_isolate_system() == True:
			self.add_header_file([
			    "/usr/include/jack/*",
			    ],
			    destination_path="jack",
			    recursive=True)


