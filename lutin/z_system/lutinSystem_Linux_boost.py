#!/usr/bin/python
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
		self.help="BOOST : Boost interface (need when we have not all c++ feature\n Can be install with the package:\n    - libboost-all-dev"
		# check if the library exist:
		if not os.path.isfile("/usr/include/boost/chrono.hpp"):
			# we did not find the library reqiested (just return) (automaticly set at false)
			return;
		self.valid = True
		# todo : create a searcher of the presence of the library:
		self.add_export_flag("link", [
		    "-lboost_system",
		    "-lboost_thread",
		    "-lboost_chrono"
		    ])
		


