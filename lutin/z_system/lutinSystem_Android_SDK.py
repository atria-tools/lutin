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
		self.set_help("SDK: Android SDK basic interface java")
		# jar file:
		jar_file_path=os.path.join(target.path_sdk, "platforms", "android-" + str(target.board_id), "android.jar")
		# TODO : Check if the android sdk android.jar is present ...
		self.set_valid(True)
		# todo : create a searcher of the presence of the library:
		self.add_sources(jar_file_path)
		self.add_flag("link-lib", "dl")
		self.add_flag("link-lib", "log")
		self.add_flag("link-lib", "android")


