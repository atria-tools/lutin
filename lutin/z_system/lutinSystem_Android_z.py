#!/usr/bin/python
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
		self.set_help("Z : z library \n Can be install with the package:\n    - zlib1g-dev")
		# check if the library exist:
		if not os.path.isfile("/usr/include/zlib.h"):
			# we did not find the library reqiested (just return) (automaticly set at false)
			return;
		self.set_valid(True)
		# todo : create a searcher of the presence of the library:
		self.add_flag("link-lib", "z")


