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
import datetime
import lutinTools
import lutinModule as module
import lutinImage
import lutinHost

class System:
	def __init__(self):
		self.valid=False;
		self.help="";
		self.include_cc=[]
		self.export_flags_cc=[]
		self.export_flags_xx=[]
		self.export_flags_mm=[]
		self.export_flags_m=[]
		self.export_flags_ar=[]
		self.export_flags_ld=[]
		self.export_flags_ld_shared=[]
		self.export_libs_ld=[]
		self.export_libs_ld_shared=[]
		
	def append_and_check(self, listout, newElement, order):
		for element in listout:
			if element==newElement:
				return
		listout.append(newElement)
		if True==order:
			listout.sort()
	
	def append_to_internalList(self, listout, list, order=False):
		if type(list) == type(str()):
			self.append_and_check(listout, list, order)
		else:
			# mulyiple imput in the list ...
			for elem in list:
				self.append_and_check(listout, elem, order)
	
	def add_export_flag_LD(self, list):
		self.append_to_internalList(self.export_flags_ld, list)
	
	def add_export_flag_CC(self, list):
		self.append_to_internalList(self.export_flags_cc, list)
	
	def add_export_flag_XX(self, list):
		self.append_to_internalList(self.export_flags_xx, list)
	
	def add_export_flag_M(self, list):
		self.append_to_internalList(self.export_flags_m, list)
	
	def add_export_flag_MM(self, list):
		self.append_to_internalList(self.export_flags_mm, list)
	
	



def createModuleFromSystem(target, dict):
	myModule = module.Module(dict["path"], dict["name"], 'PREBUILD')
	
	myModule.add_export_flag_LD(dict["system"].export_flags_cc)
	myModule.add_export_flag_XX(dict["system"].export_flags_xx)
	myModule.add_export_flag_M(dict["system"].export_flags_m)
	myModule.add_export_flag_MM(dict["system"].export_flags_mm)
	# add the currrent module at the 
	return myModule




# Dictionnaire of Target name
#   inside table of ["Name of the lib", "path of the lib", boolean loaded, module loaded]
systemList={}
__startSystemName="lutinSystem_"


def import_path(path):
	global targetList
	matches = []
	debug.debug('Start find sub File : "%s"' %path)
	for root, dirnames, filenames in os.walk(path):
		tmpList = fnmatch.filter(filenames, __startSystemName + "*.py")
		# Import the module :
		for filename in tmpList:
			debug.verbose('    Find a file : "%s"' %os.path.join(root, filename))
			sys.path.append(os.path.dirname(os.path.join(root, filename)) )
			systemName = filename.replace('.py', '')
			systemName = systemName.replace(__startSystemName, '')
			targetType, systemName = systemName.split('_')
			debug.debug("integrate system: '" + targetType + "':'" + systemName + "' from '" + os.path.join(root, filename) + "'")
			if targetType in systemList:
				systemList[targetType].append({"name":systemName,
				                               "path":os.path.join(root, filename),
				                               "system":None,
				                               "loaded":False,
				                               "exist":False,
				                               "module":None})
			else:
				systemList[targetType] = [{"name":systemName,
				                           "path":os.path.join(root, filename),
				                           "system":None,
				                           "loaded":False,
				                           "exist":False,
				                           "module":None}]

def display():
	global systemList
	for elementName in systemList:
		debug.info("integrate system: '" + elementName +"'")
		for data in systemList[elementName]:
			debug.info("    '" + data["name"] +"' in " + data["path"])


def exist(lib_name, target_name) :
	global systemList
	if target_name not in systemList:
		return False
	for data in systemList[target_name]:
		if data["name"] == lib_name:
			# we find it in the List ==> need to check if it is present in the system :
			if data["loaded"] == False:
				debug.verbose("add to path: '" + os.path.dirname(data["path"]) + "'")
				sys.path.append(os.path.dirname(data["path"]))
				debug.verbose("import system : '" + data["name"] + "'")
				theSystem = __import__(__startSystemName + target_name + "_" + data["name"])
				#create the system module
				data["system"] = theSystem.System()
				data["exist"] = data["system"].valid
			return data["exist"]
	return False

def load(target, lib_name, target_name):
	global systemList
	if target_name not in systemList:
		debug.error("you must call this function after checking of the system exist() !1!")
	for data in systemList[target_name]:
		if data["name"] == lib_name:
			if data["exist"] == False:
				debug.error("you must call this function after checking of the system exist() !2!")
			if data["module"] == None:
				# create a module from the system interface...
				data["module"] = createModuleFromSystem(target, data)
				data["loaded"] = True
			target.add_module(data["module"])
			return

