#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license MPL v2.0 (see license file)
##

import platform
import os
import zipfile
# Local import
from . import debug
from . import tools


def create_zip(path, outputFile):
	debug.debug("Create Zip : '" + outputFile + "'")
	tools.create_directory_of_file(outputFile)
	debug.debug("    from '" + str(path) + "'")
	if tools.get_type_string(path) == "string":
		path = [path]
	zf = zipfile.ZipFile(outputFile, mode='w')
	for elem in path:
		basePathlen = len(elem)
		for root, dirnames, filenames in os.walk(elem):
			# List all files :
			for filename in filenames:
				file = os.path.join(root, filename)
				debug.verbose("    ADD zip = " + str(file) + " ==> " +file[basePathlen:])
				zf.write(file, file[basePathlen:])
	zf.close()

def create_zip_file(files, base_output, outputFile):
	debug.debug("Create Zip : '" + outputFile + "'")
	tools.create_directory_of_file(outputFile)
	debug.debug("    from '" + str(files) + "'")
	if tools.get_type_string(files) == "string":
		files = [files]
	zf = zipfile.ZipFile(outputFile, mode='w')
	for elem in files:
		debug.verbose("    ADD zip = " + str(elem) + " ==> " + base_output + "/" + elem[len(os.path.dirname(elem)):])
		zf.write(elem, base_output + "/" + elem[len(os.path.dirname(elem)):])
	zf.close()
	

