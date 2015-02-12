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
		self.help="CoreAudio : MacOs interface for audio (all time present, just system interface)"
		self.valid = True
		# todo : create a searcher of the presence of the library:
		self.add_export_flag_LD("-framework CoreAudio")

