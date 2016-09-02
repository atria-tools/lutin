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
		self.help = "OpenGL: Generic graphic library"
		self.valid = True
		# no check needed ==> just add this:
		self.add_module_depend([
		    'c',
		    'X11'
		    ])
		self.add_export_flag('link-lib', 'GL')
		if env.get_isolate_system() == True:
				self.add_header_file([
			    "/usr/include/GL/*"
			    ],
			    destination_path="GL",
			    recursive=True)
		
		"""
		if target.name=="Linux":
			
		elif target.name=="Android":
			my_module.add_export_flag('link-lib', "GLESv2")
		elif target.name=="Windows":
			my_module.add_module_depend([
			    "glew"
			    ])
		elif target.name=="MacOs":
			my_module.add_export_flag('link', [
			    "-framework OpenGL"])
		elif target.name=="IOs":
			my_module.add_export_flag('link', [
			    "-framework OpenGLES"
			    ])
		"""


