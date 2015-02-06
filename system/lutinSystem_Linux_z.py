#!/usr/bin/python
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##

import lutinDebug as debug
import lutinSystem
import lutinTools as tools
import os

class System(lutinSystem.System):
	def __init__(self):
		lutinSystem.System.__init__(self)
		# create some HELP:
		self.help="Z : z library \n Can be install with the package:\n    - zlib1g-dev"
		# check if the library exist:
		if     not os.path.isfile("/usr/include/zlib.h"):
			# we did not find the library reqiested (just return) (automaticly set at false)
			return;
		self.valid = True
		# todo : create a searcher of the presence of the library:
		self.add_export_flag_CC(["-lz"])


