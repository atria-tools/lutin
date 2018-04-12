#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license MPL v2.0 (see license file)
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
		self.set_help("mysql: My sql interface (microsoft) or mariadB interface.")
		# check if the library exist:
		if     not os.path.isfile("/usr/include/mysql/mysql.h"):
			# we did not find the library reqiested (just return) (automaticly set at false)
			return;
		self.set_valid(True)
		# todo : create a searcher of the presence of the library:
		self.add_flag("link-lib", "mysqlclient")
		self.add_flag("link-lib", "ssl")
		self.add_depend([
		    'pthread',
		    'z',
		    'm',
		    #'ssl',
		    'crypto'
		    ])
		if env.get_isolate_system() == True:
			self.add_header_file([
			    "/usr/include/mysql/"
			    ],
			    clip_path="/usr/include/mysql/")
		else:
			self.add_path("/usr/include/mysql/");



