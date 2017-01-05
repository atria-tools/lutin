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
		self.set_help("ALSA : Advanced Linux Sound Architecture\n Can be install with the package:\n    - libasound2-dev")
		# check if the library exist:
		if     not os.path.isfile("/usr/include/alsa/asoundlib.h") \
		   and not os.path.isfile("/usr/include/dssi/alsa/asoundlib.h"):
			# we did not find the library reqiested (just return) (automaticly set at false)
			return;
		self.set_valid(True)
		if env.get_isolate_system() == False:
			self.add_flag("link-lib", "asound")
		else:
			self.add_flag("link-lib", "asound")
			self.add_header_file([
			    "/usr/include/alsa/*",
			    ],
			    destination_path="alsa",
			    recursive=True)
			self.add_header_file([
			    "/usr/include/dssi/*",
			    ],
			    destination_path="dssi",
			    recursive=True)
			self.add_depend([
			    'c'
			    ])


