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
		self.set_help("python numpy library")
		# check if the library exist:
		for version in ["3.7", "3.8", "3.9", "3.10", "3.11", "3.12"]:
			if os.path.isdir("/usr/lib/python" + version + "/site-packages/numpy/core/include"):
				self.set_valid(True)
				# todo : create a searcher of the presence of the library:
				self.add_flag("link-lib", "python" + version);
				if env.get_isolate_system() == True:
					self.add_header_file(self, "/usr/lib/python" + version + "/site-packages/numpy/core/include/*", clip_path="/usr/lib/python" + version + "/site-packages/numpy/core/include/", recursive=True);
				else:
					self.add_path("/usr/lib/python" + version + "/site-packages/numpy/core/include/");
				return;



