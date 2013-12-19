#!/usr/bin/python
import lutinDebug as debug
import Node

class Union(Node.Node):
	def __init__(self, stack=[], file="", lineNumber=0):
		name = ""
		Node.Node.__init__(self, 'union', name, file, lineNumber)
		self.list = []
	
	def to_str(self) :
		return "union " + self.name + " { ... };"
		

