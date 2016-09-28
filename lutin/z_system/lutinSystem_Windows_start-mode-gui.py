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

## With inluding this module you start your application in mode 'windows' instead of "console" 
class System(system.System):
	def __init__(self, target):
		system.System.__init__(self)
		# create some HELP:
		self.set_help("gui: this is not a library, this is a hook to enable graphic interface in windows (not console mode)")
		self.set_valid(True)
		self.add_flag('link', '-mwindows')
		# by default we have -mconsole then no need to remove -mconsole
		


