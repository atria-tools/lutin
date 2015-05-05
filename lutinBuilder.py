#!/usr/bin/python
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##

import sys
import os
import inspect
import fnmatch
import lutinDebug as debug
import lutinHeritage as heritage
import datetime
import lutinTools
import lutinModule
import lutinSystem
import lutinImage
import lutinHost

##
## constitution of dictionnary:
##     - "type": "compiler", "linker"
##     - "in": input type file
##     - "out": extention of the files
##     - "builder": pointer on the element
##
builder_list=[]
__start_builder_name="lutinBuilder_"


def import_path(path):
	global builder_list
	matches = []
	debug.debug('BUILDER: Start find sub File : "%s"' %path)
	for root, dirnames, filenames in os.walk(path):
		tmpList = fnmatch.filter(filenames, __start_builder_name + "*.py")
		# Import the module :
		for filename in tmpList:
			debug.debug('BUILDER:     Find a file : "%s"' %os.path.join(root, filename))
			#matches.append(os.path.join(root, filename))
			sys.path.append(os.path.dirname(os.path.join(root, filename)) )
			builder_name = filename.replace('.py', '')
			the_builder = __import__(builder_name)
			builder_list.append({"name":builder_name,
			                     "element":the_builder
			                    })
			debug.debug('BUILDER:     type=' + the_builder.getType() + " in=" + str(the_builder.getInputType()) + " out=" + str(the_builder.getOutputType()))

# we must have call all import before ...
def init():
	global builder_list
	debug.debug('BUILDER: Initialize all ...')
	for element in builder_list:
		if element["element"] != None:
			element["element"].init()

def getBuilder(input_type):
	global builder_list
	for element in builder_list:
		if element["element"] != None:
			if input_type in element["element"].getInputType():
				return element["element"]
	# we can not find the builder ...
	debug.error("Can not find builder for type : '" + str(input_type) + "'")
	return None

