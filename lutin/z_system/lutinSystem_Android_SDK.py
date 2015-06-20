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
		self.help="SDK: Android SDK basic interface java\n"
		self.valid = True
		# todo : create a searcher of the presence of the library:
		self.add_export_SRC(target.folder_sdk + "/platforms/android-" + str(target.boardId) + "/android.jar")


