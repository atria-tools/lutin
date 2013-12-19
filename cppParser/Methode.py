##!/usr/bin/python
import lutinDebug as debug
import Node
import Type

class Methode(Node.Node):
	def __init__(self, stack=[], file="", lineNumber=0):
		name = ""
		Node.Node.__init__(self, 'methode', name, file, lineNumber)
		self.name = ""
		self.returnType = Type.TypeVoid()
		self.virtual = False # only for C++
		self.static = False
		self.inline = False
		self.const = False # the end of line cont methode is sont for the class ...
		self.doc = None
		self.variable = None
		self.visibility = "private" # only for C++ : "public" "protected" "private"
	
	def to_str(self):
		ret = ""
		if self.virtual == True:
			ret += "virtual "
		if self.static == True:
			ret += "static "
		if self.inline == True:
			ret += "inline "
		ret += self.returnType.to_str()
		ret += " "
		ret += self.name
		ret += "("
		# ...
		ret += ")"
		if self.const == True:
			ret += " const"
		return ret

