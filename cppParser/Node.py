#!/usr/bin/python
import lutinDebug as debug

class Node():
	def __init__(self, type, name="", file="", lineNumber=0):
		self.nodeType = type
		self.name = name
		self.doc = None
		self.fileName = file
		self.lineNumber = lineNumber
		self.subList = []
		
	def to_str(self):
		return ""
		
	def append(self, newSubElement):
		# just add it in a sub List :
		self.subList.append(newSubElement)


