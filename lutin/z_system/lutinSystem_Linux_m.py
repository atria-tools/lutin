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
import os

class System(system.System):
	def __init__(self, target):
		system.System.__init__(self)
		# create some HELP:
		self.help="M : m library \n base of std libs (availlagle in GNU C lib and bionic"
		# No check ==> on the basic std libs:
		self.valid = True
		# todo : create a searcher of the presence of the library:
		self.add_export_flag("link-lib", "m")
		self.add_module_depend([
		    'c'
		    ])
		self.add_header_file([
		    "/usr/include/math.h"
		    ],
		    clip_path="/usr/include",
		    recursive=False)



