#!/usr/bin/python
import lutinDebug as debug
import Node

class Namespace(Node.Node):
	def __init__(self, stack=[], file="", lineNumber=0):
		if len(stack) != 2:
			debug.error("Can not parse namespace : " + str(stack))
		Node.Node.__init__(self, 'namespace', stack[1], file, lineNumber)
		# enable sub list
		self.subList = []
		
		debug.verbose("find namespace : " + self.to_str())
	
	def to_str(self) :
		return "namespace " + self.name + " { ... };"
		

