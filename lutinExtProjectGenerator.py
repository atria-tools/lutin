#!/usr/bin/python
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
		
	