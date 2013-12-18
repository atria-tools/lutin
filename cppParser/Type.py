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

import inspect

class Type():
	def __init__(self):
		self.name = ""
		self.const = False # the const xxxxx
		self.constVar = False # the char* const VarName
		self.static = False
		self.inline = False
		self.reference = False


class TypeVoid(Type):
	def __init__(self):
		Type.__init__()
		self.name = "void"

