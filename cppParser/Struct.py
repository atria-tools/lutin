#!/usr/bin/python
import lutinDebug as debug
import Node

class Struct(Node.Node):
	def __init__(self, stack=[], file="", lineNumber=0):
		name = ""
		Node.Node.__init__(self, 'struct', name, file, lineNumber)
		# CPP section:
		self.namespaces = []
		self.classes = []
		# C section:
		self.structs = []
		self.variables = []
		self.methodes = []
		self.unions = []
		self.types = []
	
	def to_str(self) :
		return "struct " + self.name + " { ... };"
		

