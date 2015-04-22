#!/usr/bin/python
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##
import lutinDebug as debug
import lutinTools as tools
import platform
import os
import zipfile


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
	
"""
print('creating archive')
zf = zipfile.ZipFile('zipfile_write.zip', mode='w')
try:
	print('adding README.md')
	zf.write('README.md')
finally:
	print('closing')
	zf.close()
"""

