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
		self.set_help("CXX: Generic C++ library")
		self.set_valid(True)
		# no check needed ==> just add this:
		self.add_flag("c++","-D__STDCPP_GNU__")
		self.add_flag("c++-remove","-nostdlib")
		# force static link to prenvent many errors ...
		self.add_flag("link", [
		    "-static-libgcc",
		    "-static-libstdc++",
		    "-static"
		    ])
		self.add_flag("need-libstdc++", True)


