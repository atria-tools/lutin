#!/usr/bin/python
# for path inspection:
import inspect
import os
import fnmatch
import sys

"""
	
"""
class module:
	"""
	Module class represent all system needed for a specific
		module like 
			- type (bin/lib ...)
			- dependency
			- flags
			- files
			- ...
	"""
	def __init__(self, file, moduleName, moduleType):
		## Remove all variable to prevent error of multiple deffinition of the module ...
		self.originFile=''
		self.originFolder=''
		# type of the module:
		self.type='LIBRARY'
		# Name of the module
		self.name=''
		# Dependency list:
		self.depends=[]
		# export PATH
		self.export_path=[]
		self.export_flags_ld=[]
		# list of all flags:
		self.flags_ld=[]
		self.flags_cc=[]
		self.flags_xx=[]
		self.flags_m=[]
		self.flags_mm=[]
		self.flags_s=[]
		# sources list:
		self.src=[]
		# copy files and folders:
		self.files=[]
		self.folders=[]
		## end of basic INIT ...
		if moduleType == 'BINARY' or moduleType == 'LIBRARY' or moduleType == 'PACKAGE':
			self.type=moduleType
		else :
			print 'for module "%s"' %moduleName
			print '    ==> error : "%s" ' %moduleType
			raise 'Input value error'
		self.originFile = file;
		self.originFolder = GetCurrentPath(self.originFile)
		self.name=moduleName
	
	def AppendToInternalList(self, listout, list):
		if type(list) == type(str()):
			listout.append(list)
		else:
			# mulyiple imput in the list ...
			for elem in list:
				listout.append(elem)
	
	def AddModuleDepend(self, list):
		self.AppendToInternalList(self.depends, list)
	
	def AddExportPath(self, list):
		self.AppendToInternalList(self.export_path, list)
	
	def AddExportflag_LD(self, list):
		self.AppendToInternalList(self.export_flags_ld, list)
	
	# add the link flag at the module
	def CompileFlags_LD(self, list):
		self.AppendToInternalList(self.flags_ld, list)
	
	def CompileFlags_CC(self, list):
		self.AppendToInternalList(self.flags_cc, list)
	
	def CompileFlags_XX(self, list):
		self.AppendToInternalList(self.flags_xx, list)
	
	def CompileFlags_M(self, list):
		self.AppendToInternalList(self.flags_m, list)
	
	def CompileFlags_MM(self, list):
		self.AppendToInternalList(self.flags_mm, list)
	
	def CompileFlags_S(self, list):
		self.AppendToInternalList(self.flags_s, list)
	
	def AddSrcFile(self, list):
		self.AppendToInternalList(self.src, list)
	
	def CopyFile(self, src, dst):
		self.files.append([src,dst])
	
	def CopyFolder(self, src, dst):
		self.folders.append([src,dst])
	
	def PrintList(self, description, list):
		if len(list) > 0:
			print '        %s' %description
			for elem in list:
				print '            %s' %elem
	
	def Display(self):
		print '-----------------------------------------------'
		print ' package : "%s"' %self.name
		print '-----------------------------------------------'
		print '    type:"%s"' %self.type
		print '    file:"%s"' %self.originFile
		print '    folder:"%s"' %self.originFolder
		self.PrintList('depends',self.depends)
		self.PrintList('flags_ld',self.flags_ld)
		self.PrintList('flags_cc',self.flags_cc)
		self.PrintList('flags_xx',self.flags_xx)
		self.PrintList('flags_m',self.flags_m)
		self.PrintList('flags_mm',self.flags_mm)
		self.PrintList('flags_s',self.flags_s)
		self.PrintList('src',self.src)
		self.PrintList('files',self.files)
		self.PrintList('folders',self.folders)
		self.PrintList('export_path',self.export_path)
		self.PrintList('export_flags_ld',self.export_flags_ld)

# the list of all module is named : moduleList
moduleList = []

"""
	
"""
def AddModule(newModule):
	moduleList.append(newModule)

"""
	
"""
def Dump():
	print 'Dump [START]'
	if 'moduleList' in globals():
		for mod in moduleList:
			mod.Display()
	else:
		print ' ==> no module added ...'
	print 'Dump [END]'

"""
	
"""
def GetCurrentPath(file):
	return os.path.dirname(os.path.realpath(file))

"""
	
"""
def GetRunFolder():
	return os.getcwd()

def ImportPath(path):
	matches = []
	print 'Start find sub File : "%s"' %path
	for root, dirnames, filenames in os.walk(path):
		tmpList = fnmatch.filter(filenames, '*_Linux.py')
		tmpList += fnmatch.filter(filenames, '*_Generic.py')
		tmpList += fnmatch.filter(filenames, '*_MacOs.py')
		tmpList += fnmatch.filter(filenames, '*_Android.py')
		# TODO : Limit path at 1 for every file
		
		# TODO : Test if Specific board exist and after generic
		
		# Import the module :
		for filename in tmpList:
			print '    Find a file : "%s"' %os.path.join(root, filename)
			#matches.append(os.path.join(root, filename))
			sys.path.append(os.path.dirname(os.path.join(root, filename)) )
			moduleName = filename.replace('.py', '')
			print 'try load : %s' %moduleName
			__import__(moduleName)
			# note : Better to do a module system ==> proper ...


"""
	Run everything that is needed in the system
"""
def Automatic():
	print "automatic [start]"
	Dump()
	print "automatic [stop]"

print "999999999999999999999999999999999999999999"

if __name__ == '__main__':
	print "Use Make as a make stadard"
	sys.path.append(GetRunFolder())
	print " try to impoert module 'Makefile.py'"
	__import__("Makefile")
	Automatic()
