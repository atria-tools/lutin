#!/usr/bin/python
import sys
import lutinDebug as debug



class heritage:
	def __init__(self, module):
		## Remove all variable to prevent error of multiple definition
		# all the parameter that the upper classe need when build
		self.flags_ld=[]
		self.flags_cc=[]
		self.flags_xx=[]
		self.flags_m=[]
		self.flags_mm=[]
		# sources list:
		self.src=[]
		self.path=[]
		# update is set at true when data are newly created ==> force upper element to update
		self.hasBeenUpdated=False
		
		if type(module) != type(None):
			# all the parameter that the upper classe need when build
			self.flags_ld=module.export_flags_ld
			self.flags_cc=module.export_flags_cc
			self.flags_xx=module.export_flags_xx
			self.flags_m=module.export_flags_m
			self.flags_mm=module.export_flags_mm
			self.path=module.export_path
	
	def AppendAndCheck(self, listout, newElement):
		for element in listout:
			if element==newElement:
				return
		listout.append(newElement)
	
	def AppendToInternalList(self, listout, list):
		if type(list) == type(str()):
			self.AppendAndCheck(listout, list)
		else:
			# mulyiple imput in the list ...
			for elem in list:
				self.AppendAndCheck(listout, elem)
	
	def AddFlag_LD(self, list):
		self.AppendToInternalList(self.flags_ld, list)
	
	def AddFlag_CC(self, list):
		self.AppendToInternalList(self.flags_cc, list)
	
	def AddFlag_XX(self, list):
		self.AppendToInternalList(self.flags_xx, list)
	
	def AddFlag_M(self, list):
		self.AppendToInternalList(self.flags_m, list)
	
	def AddFlag_MM(self, list):
		self.AppendToInternalList(self.flags_mm, list)
	
	def AddImportPath(self, list):
		self.AppendToInternalList(self.path, list)
	
	def AddSources(self, list):
		self.AppendToInternalList(self.src, list)
	
	def NeedUpdate(self, list):
		self.hasBeenUpdated=True
	
	def AddSub(self, other):
		if type(other) == type(None):
			debug.verbose("input of the heriatege class is None !!!")
			return
		if other.hasBeenUpdated==True:
			self.hasBeenUpdated = True
		self.AddFlag_LD(other.flags_ld)
		self.AddFlag_CC(other.flags_cc)
		self.AddFlag_XX(other.flags_xx)
		self.AddFlag_M(other.flags_m)
		self.AddFlag_MM(other.flags_mm)
		self.AddImportPath(other.path)
		self.AddSources(other.src)
