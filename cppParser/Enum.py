#!/usr/bin/python
import lutinDebug as debug
import Node

class Enum(Node.Node):
	def __init__(self, stack=[], file="", lineNumber=0):
		name = ""
		Node.Node.__init__(self, 'enum', name, file, lineNumber)
		# CPP section:
		self.listElement = []
	
	def to_str(self) :
		return "enum " + self.name + " { ... };"
		

