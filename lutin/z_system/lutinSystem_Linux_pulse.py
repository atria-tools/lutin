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
		self.set_help("PULSE : The Linux PulseAudio\n Can be install with the package:\n    - libpulse-dev")
		# check if the library exist:
		if     not os.path.isfile("/usr/include/pulse/pulseaudio.h"):
			# we did not find the library reqiested (just return) (automaticly set at false)
			return;
		dst_data = tools.file_read_data("/usr/include/pulse/version.h")
		lines = dst_data.split("\n")
		patern = "#define pa_get_headers_version() (\""
		version = None
		for line in lines:
			if line[:len(patern)] == patern:
				#Find the version line
				version = line[len(patern)]
				version2 = line[len(patern)+2]
				debug.verbose("detect version '" + version + "'")
				break;
		if version == None:
			debug.warning("Can not det version of Pulseaudio ... ==> remove it")
			return
		self.set_version([int(version),int(version2)])
		self.set_valid(True)
		self.add_depend([
		    'c'
		    ])
		if env.get_isolate_system() == False:
			self.add_flag("link-lib", [
			    "pulse-simple",
			    "pulse"
			    ])
		else:
			# todo : create a searcher of the presence of the library:
			self.add_flag("link-lib", [
			    "pulsecommon-" + version + ".0",
			    "pulse-mainloop-glib",
			    "pulse-simple",
			    "pulse"
			    ])
			self.add_flag("link", "-L/usr/lib/pulseaudio")
			self.add_header_file([
			    "/usr/include/pulse/*",
			    ],
			    destination_path="pulse",
			    recursive=True)


