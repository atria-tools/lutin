#!/usr/bin/python
import lutinDebug as debug
import Node


##
## @brief transform template descrption in one element.
## @param[in] list of elements. ex : 'public', 'ewol::classee', '<', 'plop', '<', 'uint8_t', ',', 'int32_t', '>', '>'
## @return a simplify list. ex : 'public', 'ewol::classee<plop<uint8_t,int32_t>>'
##
def concatenate_template(list):
	# TODO ...
	return list

class Class(Node.Node):
	def __init__(self, stack=[], file="", lineNumber=0):
		if len(stack) < 2:
			debug.error("Can not parse class : " + str(stack))
			return
		Node.Node.__init__(self, 'class', stack[1], file, lineNumber)
		# heritage list :
		self.inherit = []
		if len(stack) == 2:
			# just a simple class...
			return
		if len(stack) == 3:
			debug.error("error in parsing class : " + str(stack))
			return
		if stack[2] != ':':
			debug.error("error in parsing class : " + str(stack) + " missing ':' at the 3rd position ...")
		
		list = concatenate_template(stack[3:])
		debug.info("inherit : " + str(list))
		access = "private"
		for element in list:
			if element in ['private', 'protected', 'public']:
				access = element
			elif element == ',':
				pass
			else:
				self.inherit.append({'access' : access, 'class' : element})
		
		debug.info("class : " + self.to_str())
	
	def to_str(self) :
		ret = "class " + self.name
		if len(self.inherit) != 0 :
			ret += " : "
			isFirst = True
			for element in self.inherit:
				if isFirst == False:
					ret += ", "
				isFirst = False
				ret += element['access'] + " " + element['class']
		ret += " { ... };"
		return ret



