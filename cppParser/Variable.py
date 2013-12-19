#!/usr/bin/python
import lutinDebug as debug
import Type
import Node

class Variable(Node.Node):
	def __init__(self, stack=[], file="", lineNumber=0):
		if len(stack) < 2:
			debug.error("Can not parse variable : " + str(stack))
		Node.Node.__init__(self, 'variable', stack[len(stack)-1], file, lineNumber)
		# force the sublist error  generation ...
		self.subList = None
		# default variable :
		self.type = Type.TypeVoid()
		self.static = False
		self.external = False
		self.volatile = False
		
		if 'static' in stack:
			self.static = True
			stack = [value for value in stack if value != 'static']
		if 'volatile' in stack:
			self.volatile = True
			stack = [value for value in stack if value != 'volatile']
		if 'external' in stack:
			self.external = True
			stack = [value for value in stack if value != 'external']
		
		self.type = Type.Type(stack[:len(stack)-1])
		
		debug.verbose("find variable : " + self.to_str())
	
	def to_str(self) :
		ret = ""
		if self.external == True:
			ret += "external "
		if self.volatile == True:
			ret += "volatile "
		if self.static == True:
			ret += "static "
		ret += self.type.to_str()
		ret += " "
		ret += self.name
		return ret

