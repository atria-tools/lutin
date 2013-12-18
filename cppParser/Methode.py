#!/usr/bin/python
try :
	# normal install module
	import ply.lex as lex
except ImportError :
	# local module
	import lex
import os
import sys
import re



class Methode():
	def __init__(self):
		self.name = ""
		self.returnType = Type.TypeVoid()
		self.virtual = False # only for C++
		self.static = False
		self.inline = False
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
		return ret

