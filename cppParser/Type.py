#!/usr/bin/python
import lutinDebug as debug
import Type
import Node

class Type():
	def __init__(self, stack=[]):
		if len(stack) == 0:
			debug.error("Can not parse Type : " + str(stack))
		self.name = ""
		self.const = False # the const xxxxx
		self.reference = False
		self.constVar = False # the char* const VarName
		if len(stack) == 1:
			self.name = stack[0]
			return;
		# check end const
		if stack[len(stack)-1] == 'const':
			self.constVar = True
			stack = stack[:len(stack)-1]
		# check if element is a reference ...
		if stack[len(stack)-1] == '&':
			self.reference = True
			stack = stack[:len(stack)-1]
		# che k if it start with const ...
		if stack[0] == 'const':
			self.const = True
			stack = stack[1:]
		
		self.name = ""
		for element in stack:
			self.name += element
	
	def to_str(self) :
		ret = ""
		if self.const == True:
			ret += "const "
		ret += self.name
		if self.reference == True:
			ret += " &"
		if self.constVar == True:
			ret += " const"
		return ret

class TypeVoid(Type):
	def __init__(self):
		Type.__init__(self, ['void'])

