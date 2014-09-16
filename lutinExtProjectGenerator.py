#!/usr/bin/python
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##

import lutinDebug as debug
import datetime
import lutinTools
import lutinModule

class ExtProjectGenerator:
	def __init__(self, extType):
		self.extType = extType
		self.name = "emptyName"
		#This is a distionnaty of all groups :
		self.groups = {}
		
	