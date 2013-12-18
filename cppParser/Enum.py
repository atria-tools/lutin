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

import Node

import inspect


class Enum(Node):
	def __init__(self):
		self.name = libName
		
		#List is contituated of 3 element : {'name':"plop", 'value':5, 'doc'=""}, ...]
		self.list = []
		
	
