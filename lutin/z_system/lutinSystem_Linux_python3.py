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
		self.set_help("Python3 library \n Can be install with the package:\n    - zlib1g-dev")
		# check if the library exist:
		for version in ["3.7", "3.8", "3.9", "3.10", "3.11", "3.12"]:
			if os.path.isdir("/usr/include/python" + version):
				self.set_valid(True)
				# todo : create a searcher of the presence of the library:
				self.add_flag("link-lib", "python" + version);
				if env.get_isolate_system() == True:
					self.add_header_file(self, "/usr/include/python" + version + "/*", clip_path="/usr/include/", recursive=True);
				else:
					self.add_path("/usr/include/python" + version + "/");
				return;



