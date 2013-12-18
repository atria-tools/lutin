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

class Variable():
	def __init__(self):
		self.name = ""
		self.type = Type.TypeVoid()
		self.const = False # the const xxxxx
		self.constVar = False # the char* const VarName
		self.static = False
		self.external = False
	
	def to_str(self) :
		return ""

