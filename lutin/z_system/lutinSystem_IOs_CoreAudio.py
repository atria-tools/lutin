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
		self.set_help("CoreAudio : Ios interface for audio (all time present, just system interface)")
		self.set_valid(True)
		# todo : create a searcher of the presence of the library:
		self.add_flag("link", "-framework CoreAudio")
		self.add_flag("link", "-framework AudioToolbox")


