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
		self.set_help("SDL: SDL Gui abstraction")
		# check if the library exist:
		if     not os.path.isfile("/usr/include/SDL/SDL.h"):
			# we did not find the library reqiested (just return) (automaticly set at false)
			return;
		self.set_valid(True)
		self.add_depend([
		    'opengl',
		    'c'
		    ])
		self.add_flag("link-lib", "SDL")
		if env.get_isolate_system() == True:
			self.add_header_file([
			    "/usr/include/SDL/*",
			    ],
			    destination_path="SDL",
			    recursive=True)
			self.add_header_file([
			    "/usr/include/SDL/*",
			    ],
			    destination_path="",
			    recursive=True)


