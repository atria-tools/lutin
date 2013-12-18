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

class Namespace():
	def __init__(self):
		self.name = ""
		# CPP section:
		self.namespaces = []
		self.classes = []
		# C section:
		self.structs = []
		self.variables = []
		self.methodes = []
		self.unions = []
		self.types = []
	
	def to_str(self) :
		return ""

