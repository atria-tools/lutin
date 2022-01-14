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
		self.set_help("zstd : ???")
		# No check ==> on the basic std libs:
		self.set_valid(True)
		# todo : create a searcher of the presence of the library:
		self.add_flag("link-lib", "zstd")
		if env.get_isolate_system() == True:
			self.add_header_file([
			    "/usr/include/zstd_error.h",
			    "/usr/include/zstd.h"
			    ],
			    clip_path="/usr/include",
			    recursive=False)



