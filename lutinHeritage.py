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
	
	def append_and_check(self, listout, newElement):
		for element in listout:
			if element==newElement:
				return
		listout.append(newElement)
	
	def append_to_internalList(self, listout, list):
		if type(list) == type(str()):
			self.append_and_check(listout, list)
		else:
			# mulyiple imput in the list ...
			for elem in list:
				self.append_and_check(listout, elem)
	
	def add_flag_LD(self, list):
		self.append_to_internalList(self.flags_ld, list)
	
	def add_flag_CC(self, list):
		self.append_to_internalList(self.flags_cc, list)
	
	def add_flag_XX(self, list):
		self.append_to_internalList(self.flags_xx, list)
	
	def add_flag_M(self, list):
		self.append_to_internalList(self.flags_m, list)
	
	def add_flag_MM(self, list):
		self.append_to_internalList(self.flags_mm, list)
	
	def add_import_path(self, list):
		self.append_to_internalList(self.path, list)
	
	def add_sources(self, list):
		self.append_to_internalList(self.src, list)
	
	def need_update(self, list):
		self.hasBeenUpdated=True
	
	def add_sub(self, other):
		if type(other) == type(None):
			debug.verbose("input of the heriatege class is None !!!")
			return
		if other.hasBeenUpdated==True:
			self.hasBeenUpdated = True
		self.add_flag_LD(other.flags_ld)
		self.add_flag_CC(other.flags_cc)
		self.add_flag_XX(other.flags_xx)
		self.add_flag_M(other.flags_m)
		self.add_flag_MM(other.flags_mm)
		self.add_import_path(other.path)
		self.add_sources(other.src)
