#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##

import platform
import os
import zipfile
# Local import
from . import debug
from . import tools


def create_zip(path, outputFile):
	debug.debug("Create Zip : '" + outputFile + "'")
	debug.debug("    from '" + path + "'")
	basePathlen = len(path)
	zf = zipfile.ZipFile(outputFile, mode='w')
	for root, dirnames, filenames in os.walk(path):
		# List all files :
		for filename in filenames:
			file = os.path.join(root, filename)
			debug.verbose("    ADD zip = " + str(file))
			zf.write(file, file[basePathlen:])
	zf.close()
	

