##!/usr/bin/python
import lutinDebug as debug
import Node
import Type
import Variable

class Methode(Node.Node):
	def __init__(self, stack=[], file="", lineNumber=0):
		name = ""
		type = 'methode'
		self.virtual = False
		self.virtualPure = False
		self.static = False
		self.inline = False
		self.const = False # the end of line cont methode is sont for the class ...
		
		# remove constructer inside declaration ...
		if ':' in stack:
			res = []
			for element in stack:
				if element != ':':
					res.append(element)
				else:
					break
			stack = res
		
		if     stack[len(stack)-2] == '=' \
		   and stack[len(stack)-1] == '0':
			stack = stack[:len(stack)-2]
			self.virtualPure = True
		
		if stack[0] == 'virtual':
			self.virtual = True
			stack = stack[1:]
		if stack[0] == 'static':
			self.static = True
			stack = stack[1:]
		if stack[0] == 'inline':
			self.inline = True
			stack = stack[1:]
		if stack[len(stack)-1] == 'const':
			self.const = True
			stack = stack[:len(stack)-1]
		
		namePos = -1
		
		debug.verbose("methode parse : " + str(stack))
		for iii in range(0, len(stack)-2):
			if stack[iii+1] == '(':
				name = stack[iii]
				namePos = iii
				break;
		
		if namePos == 0:
			debug.verbose("start with '" + str(name[0]) + "'")
			if name[0] == '~':
				type = 'destructor'
			else:
				type = 'constructor'
		debug.verbose("methode name : " + name)
		Node.Node.__init__(self, type, name, file, lineNumber)
		
		self.returnType = Type.TypeNone()
		self.variable = []
		
		# create the return Type (Can be Empty)
		retTypeStack = stack[:namePos]
		debug.verbose("return : " + str(retTypeStack))
		self.returnType = Type.Type(retTypeStack)
		
		parameterStack = stack[namePos+2:len(stack)-1]
		debug.verbose("parameter : " + str(parameterStack))
		paramTmp = []
		for element in parameterStack:
			if element == ',':
				self.variable.append(Variable.Variable(paramTmp))
				paramTmp = []
			else:
				paramTmp.append(element)
		if len(paramTmp) != 0:
			self.variable.append(Variable.Variable(paramTmp))
	
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
		if self.virtualPure == True:
			ret += " = 0"
		if self.const == True:
			ret += " const"
		return ret
	